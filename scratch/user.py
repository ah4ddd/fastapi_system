from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

# Backend's private signature stamp, JWT uses this to sign tokens
SECRET_KEY = "e606675cf40e959035c05fd5c682f78b39571578423bc55931c16eb764d8a859"
# mathematical signing algorithm
ALGORITHM = "HS256"
# JWT dies after 30 mins
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Main Admin",
        "email": "admin@example.com",
        "hashed_password": "",
        "disabled": False,
    }
}


# The response you send back after successful login
class Token(BaseModel):
    access_token: str
    token_type: str


# The data you extract FROM a JWT after decoding it
class TokenData(BaseModel):
    username: str | None = None


# The safe user representation, pull out sub, store it in TokenData.username
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


# The database version of a user
class UserInDB(User):
    hashed_password: str


# This is the input shape for /register/. User submits plaintext password here
class RegisterUser(BaseModel):
    username: str
    password: str
    email: str | None = None
    full_name: str | None = None

# Passoword Hashing Engine
# A PasswordHash object configured with Argon2id using
# secure recommended settings (65536 KB memory, 3 iterations, 4 parallel threads)
# knows: how to hash passwords & verify passwords
password_hash = PasswordHash.recommended()

def get_password_hash(password):
    """
    Takes plaintext string → generate random salt + mix with password 8+ argon2 hash + store everything in one string.
    """
    return password_hash.hash(password)

admin_password = "admin123"

# Runs at startup. It dynamically hashes the admin password
# and stores it in the fake database
fake_users_db["admin"]["hashed_password"] = get_password_hash(admin_password)

# Pre-computed hash of a dummy password. Created once at startup.
# Used in authenticate_user to prevent timing attacks
DUMMY_HASH = password_hash.hash("dummypassword")

# TOKEN EXTRACTOR DEPENDENCY
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    """
    What it does in memory:
    * Takes plain_password (what the user typed) — e.g. "admin123"
    * Takes hashed_password (what's stored) — e.g. "$argon2id$v=19$m=65536..."
    * Extracts the salt from hashed_password
    * Runs Argon2 on plain_password using that SAME salt
    * Compares the resulting hash to the stored hash
    * Returns True if they match, False if not
    """
    return password_hash.verify(plain_password, hashed_password)


def get_user(db, username: str | None):
    """
    The result in memory is a UserInDB object with all fields populated.
    You can now do user.hashed_password, user.username, etc. with editor autocomplete.
    """
    if username is None:
        return None
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict) # spreads the dict as keyword arguments


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    # Even when user DOESN'T EXIST: backend STILL performs fake hash verification.
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    # User exists. Now check their password.
    # verify_password hashes what they sent using the stored salt
    # and compares. Wrong password → return False.
    if not verify_password(password, user.hashed_password):
        return False
    # Both checks passed. Returns the UserInDB object.
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    THE TOKEN DOES NOT EXPIRE BY ITSELF
    The SERVER checks:
    “Is the current time greater than the token's stored expiry time?”
    That's it.
    """
    # This is the payload — what you want to store in the token
    # Makes a copy of the dict. You never mutate function arguments
    to_encode = data.copy()
    if expires_delta:
        # Current UTC time + 30 minutes = token expiration time
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    to_encode.update({"exp": expire})
    # serializes header + payload & signs it cryptographically
    # produces: SUPER LONG RANDOM SIGNATURE & final token (h.p.s)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    jwt.decode does THREE things simultaneously:

    * Decodes the base64 — extracts the payload dict
    * Verifies the signature — recalculates HMAC-SHA256 of header+payload using * * your SECRET_KEY and checks it matches Part3. If someone tampered with the * * payload, the signature won't match → InvalidTokenError
    * Checks exp — compares the expiry datetime to right now. If expired → InvalidTokenError

    If all three pass, payload is now a plain Python dict
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # server verifies if it created this token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post("/register/")
async def register(user: RegisterUser):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=400,
            detail="Username already exisits"
            )
    # run hashing process
    hashed_password = get_password_hash(user.password)

    fake_users_db[user.username] = {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "hashed_password": hashed_password,
        "disabled": False
    }

"""
Protected Route
      ↓
get_current_active_user()
      ↓
get_current_user()
      ↓
jwt.decode()
      ↓
TOKEN VALID?
   ↓       ↓
 YES       NO
 ↓          ↓
return      raise 401
user
"""
@app.get("/users/me/")
async def read_users_me(

    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "siya", "owner": current_user.username}]


@app.get("/generate-hash/{password}")
async def generate_hash(password: str):
    hashed = get_password_hash(password)

    return {
        "plain_password": password,
        "hashed_password": hashed
    }


# just for test (dont do this in production)
@app.get("/all-users")
async def all_users():
    return fake_users_db


"""
ENTIRE FLOW:

REGISTER
↓
hash password
↓
store user in DB

LOGIN
↓
verify password
↓
create JWT token
↓
give token to browser

PROTECTED ROUTE
↓
browser sends token
↓
backend verifies token
↓
backend extracts username
↓
backend fetches user
↓
route unlocked
"""
