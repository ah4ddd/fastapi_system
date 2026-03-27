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
from app.auth import hash_password, verify_password, create_access_token # type: ignore
from datetime import datetime

# All routes start with /auth = /signup → /auth/signup → /auth/login
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignup, db: AsyncSession = Depends(get_db)):
    """
    Create a new user account.

    - Checks if email already exists
    - Hashes password
    - Stores user in database
    """

    # Check if user already exists
    query = select(UserDB).where(UserDB.email == user.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none() # Returns ONE result or None

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Plain → bcrypt hash (preparing a row to insert)
    hashed_pw = hash_password(user.password)

    # Create user DB object
    new_user = UserDB(
        email=user.email,
        hashed_password=hashed_pw,
        created_at=datetime.utcnow().isoformat()
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
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login and receive JWT access token.

    - Verifies email exists
    - Verifies password
    - Returns JWT token
    """

    # Find user
    query = select(UserDB).where(UserDB.email == user.email)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password. If password is NOT correct → reject login
    # It’s not stored. It's just: True / False check
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create JWT token
    # sub = "Subject" (standard JWT claim, usually user identifier)
    # user_id = Custom claim (App's user ID)
    access_token = create_access_token(data={"sub": db_user.email, "user_id": db_user.id})

    # Client store this and send it later
    return Token(access_token=access_token, token_type="bearer")


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
