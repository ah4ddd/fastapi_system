# Authentication API layer
# connects:
#          HTTP requests (signup/login)
#          Auth logic (auth.py)
#          Database

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession # DB connection
from sqlalchemy import select # SQL query builder
# db session injection
from app.database import get_db # type: ignore
# Pydantic models
from app.models import UserSignup, UserLogin, Token, UserResponse # type: ignore
# Actual db table model. UserDB = DB structure. UserSignup = API input
from app.db_models import UserDB # type: ignore
# Auth logic
from app.auth import hash_password, verify_password, create_access_token, get_current_user # type: ignore
from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

# All routes start with /auth = /signup → /auth/signup → /auth/login
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# Request arrives (HTTP layer)
# FastAPI:
#    parses JSON
#    validates using UserSignup
#    gives user.email, user.password
async def signup(
    user: UserSignup,
    db: Annotated[AsyncSession, Depends(get_db)]
    ):
    """
    Create a new user account.

    - Checks if email already exists
    - Hashes password
    - Stores user in database
    """

    # Check if user already exists

    # SELECT * FROM users WHERE email = 'ahad@example.com'
    # DB execute it
    #    return:
    #        row → if exist
    #        None → if not
    query = select(UserDB).where(UserDB.email == user.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none() # Returns ONE result or None

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Plain → current hash
    hashed_pw = hash_password(user.password)

    # Create user DB object
    new_user = UserDB(
        email=user.email,
        hashed_password=hashed_pw,
        created_at=datetime.now(timezone.utc).isoformat()
    )

    db.add(new_user) # stage insert
    await db.commit() # actual write
    await db.refresh(new_user) # reload with DB-generated values (like id)

    # You DO NOT return password
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        created_at=new_user.created_at
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
    ):
    """
    Login and receive JWT access token.

    - Verifies email exists
    - Verifies password
    - Returns JWT token
    """
    email = form_data.username
    password = form_data.password

    # Find user
    query = select(UserDB).where(UserDB.email == email)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password. If password is NOT correct → reject login
    # It’s not stored. It's just: True / False check
    # inside verify = pwd_context.verify(plain, hash)
    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create JWT token
    # sub = "Subject" (standard JWT claim, usually user identifier)
    # user_id = Custom claim (App's user ID)
    access_token = create_access_token(
        data={
        "sub": db_user.email,
        "user_id": db_user.id
        }
    )

    # Client store this and send it later
    return Token(access_token=access_token, token_type="bearer")

# The dependency (Depends(get_current_user)) does ALL the validation
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
    ):
    """
    Get current user's info.

    PROTECTED ROUTE: Requires valid JWT token.
    """

    # user contains decoded JWT payload
    email = user.get("sub")

    # Fetch full user from database
    query = select(UserDB).where(UserDB.email == email)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        created_at=db_user.created_at
    )


"""
FULL FLOW (connect everything)
Signup:
    Client → /auth/signup
        → check email
        → hash password
        → save user
        → return safe data
Login:
    Client → /auth/login
        → find user
        → verify password
        → create JWT
        → return token

After login:
    Client sends:
        Authorization: Bearer <JWT>

Then backend:
    decodes token
    trusts user
"""

"""
Brutal clarity (no confusion left)
    Server is creating the JWT
    The browser does NOT create it
    verify_password → returns True/False
    if not → means “if incorrect”
    Token is proof of identity after login
"""


"""
Burn this in:
    The server doesn't remember the token.
    It recomputes the signature using its SECRET_KEY and checks if it matches.
"""

"""
WHAT BCRYPT ACTUALLY DOES (low-level)

Let's go deep.

Input:
    password = "password"
Step 1: Generate random salt
    salt = random_bytes(16)

Example:
    $2b$12$WV3a7pQn4A7zycXbkSEdfu

Step 2: Combine password + salt

Not simple concatenation — bcrypt does:
    hash = bcrypt(password, salt, cost=12)

Step 3: Run through expensive hashing loop

Internally:
    Blowfish-based key expansion
    repeated 2^12 times (cost factor)

    This is intentionally slow to stop brute force

Output:
    $2b$12$WV3a7pQn4A7zycXbkSEdfu51wGUrQZsCi9m8iGgvtRla.JXqN3DkC

This string contains:
    algorithm (2b)
    cost (12)
    salt
    hash

salt = random once
hash = deterministic function(password + salt)
verify = recompute + compare
"""
