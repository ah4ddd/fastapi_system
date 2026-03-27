from datetime import datetime, timedelta # token expiry
from jose import JWTError, jwt # create + verify JWT
from passlib.context import CryptContext # handle password hashing safely
# load secrets from .env
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Password hashing
# Sets up bcrypt hashing
# Handle: salt generation, hashing, verification
# Salt automatically -- Each hash is unique, even for same password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password.

    Uses bcrypt algorithm. One-way transformation.
    """
    return pwd_context.hash(password)


# Extract salt from stored hash
# Re-hashe input password
# Compares
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Returns True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


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
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # exp -- Expiration claim (standard JWT field)
    to_encode.update({"exp": expire})

    # Encode JWT. Create: header.payload.signature
    # Signature is created using: SECRET_KEY & algorithm (HS256)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


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
    except JWTError:
        return None


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
