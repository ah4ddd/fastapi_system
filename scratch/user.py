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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class RegisterUser(BaseModel):
    username: str
    password: str
    email: str | None = None
    full_name: str | None = None


# create a password hashing security engine
# knows: how to hash passwords & verify passwords
password_hash = PasswordHash.recommended()

def get_password_hash(password):
    # generate random salt + mix with password +
    # + argon2 hash + store everything in one string
    return password_hash.hash(password)

admin_password = "admin123"

fake_users_db["admin"]["hashed_password"] = get_password_hash(admin_password)

DUMMY_HASH = password_hash.hash("dummypassword")

# TOKEN EXTRACTOR DEPENDENCY
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_user(db, username: str | None):
    if username is None:
        return None
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    # Even when user DOESN'T EXIST: backend STILL performs fake hash verification.
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        # Current UTC time + 30 minutes = token expiration time
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    to_encode.update({"exp": expire})
    # serializes payload & signs it cryptographically. ALSO verifies signature
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
    hashed_password = get_password_hash(user.password)

    fake_users_db[user.username] = {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "hashed_password": hashed_password,
        "disabled": False
    }


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


@app.get("/all-users")
async def all_users():
    return fake_users_db
