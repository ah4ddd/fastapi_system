from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

SECRECT_KEY = "e606675cf40e959035c05fd5c682f78b39571578423bc55931c16eb764d8a859"
ALGORITHMV = "HS256"
ACESS_TOKEN_EXPIRE_MINUTES = 30

fake_user_db = {
    "ahad": {
        "username": "ahad",
        "full_name": "Abdul Ahad",
        "email": "ahad@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
    },
    "siya":{
        "username": "siya",
        "full_name": "Siya Sharma",
        "email": "siya@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True
    }
}

app = FastAPI()

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

# extracts token
# can name tokenUrl anything but it should match login route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def fake_hashed_password(password: str):
    return "fakehashed" + password


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

# username = token btw
def fake_decode_token(token):
    user = get_user(fake_user_db, token)
    return user

# turns token into user
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

# check if user active
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# class that receives the login form submission.
# It's a dependency — FastAPI reads the incoming form data
# and populates it automatically
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_user_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400,
                            detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hashed_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400,
                            detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
    ):
    return current_user


"""
REQUEST ARRIVES
↓
/users/me
↓
get_current_active_user()
↓
get_current_user()
↓
oauth2_scheme()
↓
extract token from Authorization header
↓
returns "ahad"
↓
get_current_user(token="ahad")
↓
fake_decode_token("ahad")
↓
get_user(fake_user_db, "ahad")
↓
returns actual user object
↓
check disabled
↓
route finally executes
"""
