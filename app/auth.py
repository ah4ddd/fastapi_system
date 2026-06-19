from datetime import datetime, timedelta, timezone # token expiry
import jwt # create + verify JWT
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash # handle password hashing safely
# load secrets from .env
import os
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from .config import settings

load_dotenv()


SECRET_KEY = settings.jwt_secret_key
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set")

ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Password hashing
# Sets up argon2 hashing
# Handle: salt generation, hashing, verification
# Salt automatically -- Each hash is unique, even for same password
# PasswordHash.recommended() automatically uses the best available algorithm.
password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

# Expects header: Authorization: Bearer <token>
# Automatically extracts token from header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password.

    Uses Argon2 algorithm. One-way transformation.
    """
    return password_hash.hash(password)


# Extract salt from stored hash
# Re-hashes input password
# Compares
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Returns True if password matches, False otherwise.
    """
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dict containing claims (e.g., {"sub": "user@example.com"})

    Returns:
        Encoded JWT string
    """

    to_encode = data.copy() # So you don’t mutate original input

    # Add expiration time (this token dies after X minutes)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # exp -- Expiration claim (standard JWT field)
    to_encode.update({"exp": expire})

    # Encode JWT. Create: header.payload.signature (JWT string)
    # Signature is created using: SECRET_KEY & algorithm (HS256)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# Given the same inputs, these functions always produce the same output.
#    (bcrypt with a fixed salt, HMAC with a fixed key)
def decode_access_token(token: str) -> dict | None:
    """
    Decode and validate a JWT token.

    Returns:
        Decoded payload if valid, None if invalid/expired

    Validates:
        Signature (was it created by our server?)
        Expiration (is it still valid?)
        Structure (is it a valid JWT?)
    If any check fails: Returns None (token is invalid).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        return None


# This function becomes a dependency.
# When you add user = Depends(get_current_user) to a route:
#    FastAPI extracts Authorization header
#    Validates token
#    Returns user info
#    Or raises 401 if invalid
# A verification function that checks the token and returns user info
async def get_current_user(token: Annotated[str,  Depends(oauth2_scheme)]) -> dict:
    """
    Dependency to extract and validate JWT from request.

    Usage:
        @app.get("/protected route")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user": user}

    Returns:
        Decoded JWT payload (contains user info)

    Raises:
        401 if token is missing, invalid, or expired
    """

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload

"""
Full system flow (connect everything)
Signup:
    User gives password
    hash_password()
    Store hash in DB
Login:
    User gives password
    verify_password()
    If valid → create_access_token()
    Send JWT to client
Authenticated request:
    Client sends JWT
    decode_access_token()
    If valid → allow access


Mental model (burn this in)
Password → hashed → stored

Login:
    password → verify → create JWT

JWT:
    signed with SECRET_KEY

Request:
    JWT → decode → trust user
"""

"""
So what is a JWT actually?

A JWT is just:
    header.payload.signature

Example:
    abc.def.ghi
header → algorithm info
payload → your data (user_id, sub, exp)
signature → proves it wasn't tampered with

Key realization:
    The user does NOT create the token.
    Your server creates it after login.
"""

"""
Password auth:
Signup:
    salt = random
    hash = bcrypt(password, salt)

Login:
    extract salt
    recompute hash
    compare
JWT auth:
Create:
    signature = HMAC(data, SECRET_KEY)

Validate:
    recompute signature
    compare
"""

"""
Request
  ↓
Depends → runs get_current_user
  ↓
decode JWT using SECRET_KEY
  ↓
IF valid → return user
IF invalid → 401
  ↓
Route runs (or not)

----------------------------------

[Cryptography] → provides security
        ↓
[get_current_user] → uses it
        ↓
[Depends] → enforces it
        ↓
[Route] → gets protected
"""
