from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

fake_user_db = {
    "Ahad": {
        "username": "ahad",
        "full_name": "Abdul Ahad",
        "email": "ahad@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "siya":{
        "username": "siya",
        "full_name": "Siya Sharma",
        "email": "siya@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": False
    }
}

app = FastAPI()

def fake_hashed_password(passowrd: str):
    return "fakehashed" + passowrd


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
