# 🐍 SQLAlchemy + FastAPI: The No-Bullshit Guide

**Your complete guide to building production-ready APIs with Python, PostgreSQL, and SQLAlchemy.**

Last updated: Your SQLAlchemy learning journey begins now (Feb 2026)

---

## 📚 Table of Contents

1. [What the Hell is SQLAlchemy?](#what-the-hell-is-sqlalchemy)
2. [The Two Faces of SQLAlchemy (Core vs ORM)](#two-faces)
3. [Setting Up SQLAlchemy with PostgreSQL](#setup)
4. [Models: Your Python Classes = Database Tables](#models)
5. [CRUD Operations (Create, Read, Update, Delete)](#crud)
6. [Relationships: Foreign Keys, One-to-Many, Many-to-Many](#relationships)
7. [Querying Like a Pro (Filters, Joins, Aggregates)](#querying)
8. [Sessions: The Transaction Manager](#sessions)
9. [Migrations with Alembic (Schema Changes Without Breaking Shit)](#migrations)
10. [FastAPI Integration (The Full Stack)](#fastapi-integration)
11. [Async SQLAlchemy (For High-Performance Apps)](#async-sqlalchemy)
12. [Common Patterns & Best Practices](#best-practices)
13. [Performance Optimization (N+1 Queries, Eager Loading)](#performance)
14. [Common Mistakes (And How to Avoid Them)](#common-mistakes)
15. [Production Checklist](#production-checklist)
16. [Quick Reference Cheat Sheet](#cheat-sheet)

---

## 🤔 What the Hell is SQLAlchemy?

**SQLAlchemy** is a Python library that lets you interact with databases without writing raw SQL. Think of it as a **translator** between Python code and database queries.

### Why Use SQLAlchemy Instead of Raw SQL?

| Raw SQL (psycopg2) | SQLAlchemy ORM |
|-------------------|----------------|
| `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))` | `session.query(User).filter(User.id == user_id).first()` |
| Manual connection management | Automatic connection pooling |
| SQL injection risks if you fuck up | Built-in protection |
| Different syntax for each database | Write once, works on PostgreSQL, MySQL, SQLite |
| No type hints | Full Python type support |

**Bottom line:** SQLAlchemy makes your code **safer, cleaner, and more Pythonic**.

---

## 🎭 The Two Faces of SQLAlchemy (Core vs ORM)

SQLAlchemy has **two layers**:

### 1️⃣ **SQLAlchemy Core** - The Low-Level Layer

- Writes SQL using Python expressions
- Direct database access
- More control, more verbose

```python
# Core example:
from sqlalchemy import select, text

result = connection.execute(
    text("SELECT * FROM users WHERE username = :username"),
    {"username": "ahad"}
)
```

**When to use:** Raw SQL performance, complex queries, database migrations.

### 2️⃣ **SQLAlchemy ORM** - The High-Level Layer (What You'll Use 95% of the Time)

- Maps Python classes to database tables
- Treats rows as Python objects
- Less boilerplate, more intuitive

```python
# ORM example:
user = session.query(User).filter(User.username == "ahad").first()
print(user.email)  # Access like a Python object
```

**When to use:** Building APIs, CRUD operations, anything where you want clean Python code.

---

## 🛠️ Setting Up SQLAlchemy with PostgreSQL

### Installation:

```bash
# In your WSL2 terminal:
pip install sqlalchemy psycopg2-binary --break-system-packages

# For async support (we'll cover this later):
pip install sqlalchemy[asyncio] asyncpg --break-system-packages
```

### Project Structure:

```
my_fastapi_project/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app
│   ├── database.py       # Database connection
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic models (validation)
│   └── crud.py           # Database operations
├── alembic/              # Migrations (we'll set this up later)
├── .env                  # Secret config
└── requirements.txt
```

### Basic Database Setup (`database.py`):

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Connection string format:
# postgresql://username:password@host:port/database_name
DATABASE_URL = "postgresql://postgres:password@localhost:5432/fastapi_app"

# Create engine (connection pool manager):
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Check connections before using them
    echo=True            # Print SQL queries (disable in production)
)

# Session factory (creates database sessions):
SessionLocal = sessionmaker(
    autocommit=False,    # Manual commits (safer)
    autoflush=False,     # Manual flushes (more control)
    bind=engine
)

# Base class for models:
Base = declarative_base()

# Dependency for FastAPI:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**What's happening:**
- `engine` = The connection manager (talks to PostgreSQL)
- `SessionLocal` = Factory for creating sessions (transactions)
- `Base` = Parent class for all your models
- `get_db()` = FastAPI dependency that gives each request its own database session

---

## 📦 Models: Your Python Classes = Database Tables

**A model is a Python class that represents a database table.**

### Example 1: Simple User Model

```python
# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"  # The actual table name in PostgreSQL

    # Columns:
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**This Python class automatically creates this SQL:**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_users_id ON users(id);
CREATE INDEX ix_users_username ON users(username);
```

### Creating the Tables:

```python
# In your main.py or a separate script:
from database import engine, Base
from models import User  # Import all models

# Create all tables:
Base.metadata.create_all(bind=engine)
```

**Run once** when you first set up your database. After that, use migrations (Alembic).

---

## 🔧 CRUD Operations (Create, Read, Update, Delete)

### Setup: Getting a Database Session

```python
from database import SessionLocal

db = SessionLocal()  # Create a session
# ... do database operations ...
db.close()  # Always close when done
```

**Better (with context manager):**

```python
from database import SessionLocal

with SessionLocal() as db:
    # ... do database operations ...
    pass  # Session auto-closes when block exits
```

---

### 1️⃣ **CREATE** - Adding New Records

```python
from models import User

# Create a new user object:
new_user = User(
    username="ahad",
    email="ahad@example.com",
    hashed_password="$2b$12$..."  # Use bcrypt to hash passwords!
)

# Add to session (staged, not saved yet):
db.add(new_user)

# Save to database:
db.commit()

# Refresh to get auto-generated fields (id, created_at):
db.refresh(new_user)

print(f"Created user with ID: {new_user.id}")
```

**Bulk insert:**

```python
users = [
    User(username="alice", email="alice@example.com", hashed_password="hash1"),
    User(username="bob", email="bob@example.com", hashed_password="hash2"),
]

db.add_all(users)
db.commit()
```

---

### 2️⃣ **READ** - Querying Data

#### Get All Records:

```python
users = db.query(User).all()
for user in users:
    print(user.username, user.email)
```

#### Get One Record:

```python
# By primary key (fastest):
user = db.query(User).get(1)  # Returns None if not found

# By filter (first match):
user = db.query(User).filter(User.username == "ahad").first()

# Raises exception if not found:
user = db.query(User).filter(User.id == 999).one()  # Throws NoResultFound
```

#### Filtering:

```python
# WHERE is_active = true:
active_users = db.query(User).filter(User.is_active == True).all()

# WHERE username LIKE 'a%':
users = db.query(User).filter(User.username.like("a%")).all()

# WHERE created_at > '2026-01-01':
from datetime import datetime
recent_users = db.query(User).filter(
    User.created_at > datetime(2026, 1, 1)
).all()

# Multiple conditions (AND):
user = db.query(User).filter(
    User.username == "ahad",
    User.is_active == True
).first()

# OR conditions:
from sqlalchemy import or_
users = db.query(User).filter(
    or_(User.username == "ahad", User.username == "bob")
).all()

# IN clause:
users = db.query(User).filter(User.id.in_([1, 2, 3])).all()
```

#### Ordering & Limiting:

```python
# ORDER BY created_at DESC LIMIT 10:
recent_users = db.query(User).order_by(User.created_at.desc()).limit(10).all()

# Pagination (OFFSET):
page_2 = db.query(User).offset(10).limit(10).all()  # Skip 10, get next 10
```

#### Counting:

```python
total_users = db.query(User).count()
active_count = db.query(User).filter(User.is_active == True).count()
```

---

### 3️⃣ **UPDATE** - Modifying Records

#### Option 1: Fetch, Modify, Commit

```python
user = db.query(User).filter(User.username == "ahad").first()
user.email = "newemail@example.com"
user.is_admin = True
db.commit()
```

#### Option 2: Bulk Update (Faster)

```python
# Update all inactive users:
db.query(User).filter(User.is_active == False).update({
    "is_active": True
})
db.commit()
```

---

### 4️⃣ **DELETE** - Removing Records

#### Delete a Specific Record:

```python
user = db.query(User).filter(User.id == 5).first()
if user:
    db.delete(user)
    db.commit()
```

#### Bulk Delete:

```python
# Delete all inactive users:
db.query(User).filter(User.is_active == False).delete()
db.commit()
```

---

## 🔗 Relationships: Foreign Keys, One-to-Many, Many-to-Many

### Example: Blog with Users and Posts

```python
# models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship (not a column, just a Python attribute):
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    # cascade="all, delete-orphan" means: if you delete a user, delete their posts too


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship:
    author = relationship("User", back_populates="posts")
```

**What this creates in PostgreSQL:**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    content TEXT,
    author_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Using Relationships:

```python
# Create user and post:
user = User(username="ahad", email="ahad@example.com")
db.add(user)
db.commit()
db.refresh(user)  # Get the auto-generated ID

post = Post(
    title="My First Post",
    content="Hello world!",
    author_id=user.id  # Link to the user
)
db.add(post)
db.commit()

# Access relationship (SQLAlchemy auto-joins):
post = db.query(Post).first()
print(post.author.username)  # "ahad" (auto-fetches from users table)

# Reverse relationship:
user = db.query(User).first()
for post in user.posts:  # Auto-fetches all posts by this user
    print(post.title)
```

---

### Many-to-Many Relationships (Tags Example)

```python
# Association table (no model needed):
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    posts = relationship("Post", secondary=post_tags, back_populates="tags")
```

**Usage:**

```python
# Create post and tags:
post = Post(title="SQLAlchemy Tutorial")
tag1 = Tag(name="python")
tag2 = Tag(name="database")

post.tags.append(tag1)
post.tags.append(tag2)

db.add(post)
db.commit()

# Query:
post = db.query(Post).first()
print([tag.name for tag in post.tags])  # ["python", "database"]
```

---

## 🔍 Querying Like a Pro (Filters, Joins, Aggregates)

### Joins:

```python
from sqlalchemy.orm import joinedload

# INNER JOIN (only users with posts):
results = db.query(User).join(Post).all()

# LEFT JOIN (all users, even without posts):
results = db.query(User).outerjoin(Post).all()

# Access joined data:
results = db.query(User, Post).join(Post).all()
for user, post in results:
    print(f"{user.username} wrote {post.title}")
```

### Eager Loading (Solve N+1 Query Problem):

```python
# BAD (N+1 queries):
users = db.query(User).all()
for user in users:
    print(user.posts)  # Each iteration triggers a separate query!

# GOOD (1 query with JOIN):
users = db.query(User).options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # All posts already loaded
```

### Aggregates:

```python
from sqlalchemy import func

# Count posts per user:
results = db.query(
    User.username,
    func.count(Post.id).label("post_count")
).join(Post).group_by(User.username).all()

for username, count in results:
    print(f"{username}: {count} posts")
```

### Subqueries:

```python
# Users with more than 5 posts:
subquery = db.query(
    Post.author_id,
    func.count(Post.id).label("count")
).group_by(Post.author_id).subquery()

results = db.query(User).join(
    subquery, User.id == subquery.c.author_id
).filter(subquery.c.count > 5).all()
```

---

## 🎫 Sessions: The Transaction Manager

### What is a Session?

A **session** is like a workspace where you:
1. Load objects from the database
2. Modify them
3. Save changes back to the database

**Key methods:**

| Method | What It Does |
|--------|--------------|
| `db.add(obj)` | Stage a new object for insertion |
| `db.commit()` | Save all changes to the database |
| `db.rollback()` | Undo all changes since last commit |
| `db.flush()` | Send changes to DB but don't commit (useful for getting auto-generated IDs) |
| `db.refresh(obj)` | Reload object from database (get latest data) |
| `db.close()` | Close the session |

### Transaction Example:

```python
from database import SessionLocal

db = SessionLocal()

try:
    # Create user:
    user = User(username="test", email="test@example.com")
    db.add(user)
    db.flush()  # Generates user.id but doesn't commit yet

    # Create post linked to user:
    post = Post(title="Test Post", author_id=user.id)
    db.add(post)

    # Commit both together (atomic):
    db.commit()
except Exception as e:
    db.rollback()  # Undo everything if anything fails
    print(f"Error: {e}")
finally:
    db.close()
```

---

## 🔄 Migrations with Alembic (Schema Changes Without Breaking Shit)

**Problem:** Your database is live with user data. You need to add a new column. Can't just drop the table and recreate it.

**Solution:** Alembic (migration tool for SQLAlchemy).

### Setup:

```bash
pip install alembic --break-system-packages

# Initialize Alembic:
alembic init alembic
```

### Configure (`alembic/env.py`):

```python
# Add at the top:
from app.database import Base
from app.models import User, Post  # Import all models

# Find this line and change it:
target_metadata = Base.metadata  # Was: None
```

### Configure (`alembic.ini`):

```ini
# Change this line:
sqlalchemy.url = postgresql://postgres:password@localhost:5432/fastapi_app
```

### Create Your First Migration:

```bash
# Auto-generate migration from model changes:
alembic revision --autogenerate -m "Create users and posts tables"

# Apply migration:
alembic upgrade head
```

### Example: Adding a Column

```python
# models.py - Add a new field:
class User(Base):
    # ... existing fields ...
    bio = Column(Text, nullable=True)  # New field
```

```bash
# Generate migration:
alembic revision --autogenerate -m "Add bio to users"

# Apply:
alembic upgrade head
```

Alembic creates this SQL automatically:

```sql
ALTER TABLE users ADD COLUMN bio TEXT;
```

### Rollback:

```bash
# Undo last migration:
alembic downgrade -1
```

---

## 🚀 FastAPI Integration (The Full Stack)

### File Structure:

```
app/
├── __init__.py
├── main.py          # FastAPI app
├── database.py      # Connection setup
├── models.py        # SQLAlchemy models
├── schemas.py       # Pydantic schemas (request/response validation)
└── crud.py          # Database operations
```

---

### 1. Database Setup (`database.py`):

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://username:password@localhost:5432/fastapi_app"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

### 2. Models (`models.py`):

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

### 3. Pydantic Schemas (`schemas.py`):

**Why Pydantic?** SQLAlchemy models are for the **database**. Pydantic models are for **API validation**.

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Request schema (what the client sends):
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Response schema (what the API returns):
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models
```

---

### 4. CRUD Operations (`crud.py`):

```python
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()
```

---

### 5. FastAPI Routes (`main.py`):

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from schemas import UserCreate, UserResponse
import crud
import models

# Create tables:
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="My Blog API")

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists:
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create user:
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

### Running the App:

```bash
uvicorn app.main:app --reload
```

**Test it:**
```bash
# Create user:
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"username": "ahad", "email": "ahad@example.com", "password": "secret123"}'

# Get all users:
curl "http://localhost:8000/users/"
```

**Verify in pgweb:**
```sql
SELECT * FROM users;
```

---

## ⚡ Async SQLAlchemy (For High-Performance Apps)

**Why async?** Handle 1000s of concurrent requests without blocking.

### Installation:

```bash
pip install sqlalchemy[asyncio] asyncpg --break-system-packages
```

### Async Database Setup:

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql+asyncpg://bd_username:passwordl@localhost:5432/fastapi_app"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### Async CRUD:

```python
# crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=pwd_context.hash(user.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

### Async FastAPI Routes:

```python
# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
import crud

app = FastAPI()

@app.get("/users/", response_model=list[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users
```

**Performance difference:**
- **Sync:** 100 requests/second
- **Async:** 1000+ requests/second (with proper database connection pooling)

---

## 💎 Common Patterns & Best Practices

### 1. Use Enums for Fixed Choices:

```python
import enum
from sqlalchemy import Enum as SQLEnum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
```

### 2. Use Mixins for Common Fields:

```python
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    # created_at and updated_at inherited from TimestampMixin
```

### 3. Use Hybrid Properties for Computed Fields:

```python
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# Usage:
user = db.query(User).first()
print(user.full_name)  # "John Doe"

# Can even filter by it:
users = db.query(User).filter(User.full_name == "John Doe").all()
```

### 4. Soft Deletes (Don't Actually Delete Data):

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

# Instead of deleting:
user.is_deleted = True
user.deleted_at = datetime.utcnow()
db.commit()

# Only query non-deleted users:
active_users = db.query(User).filter(User.is_deleted == False).all()
```

---

## 🚀 Performance Optimization

### 1. N+1 Query Problem:

```python
# BAD (100 users = 101 queries):
users = db.query(User).all()  # 1 query
for user in users:
    print(user.posts)  # 100 queries (one per user)

# GOOD (100 users = 1 query):
from sqlalchemy.orm import joinedload
users = db.query(User).options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # Already loaded
```

### 2. Use Indexes:

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)  # Auto-creates index
    username = Column(String, index=True)  # Faster lookups
```

### 3. Batch Operations:

```python
# BAD (100 commits):
for data in user_data:
    user = User(**data)
    db.add(user)
    db.commit()  # Slow!

# GOOD (1 commit):
users = [User(**data) for data in user_data]
db.add_all(users)
db.commit()
```

### 4. Use `select_in_loading` for Large Collections:

```python
from sqlalchemy.orm import selectinload

# Better than joinedload for one-to-many with lots of related records:
users = db.query(User).options(selectinload(User.posts)).all()
```

---

## 🚨 Common Mistakes (And How to Avoid Them)

### 1. Forgetting to Commit:

```python
# ❌ WRONG - Changes not saved:
user = User(username="test")
db.add(user)
# Missing db.commit()!

# ✅ CORRECT:
user = User(username="test")
db.add(user)
db.commit()
```

### 2. Using `==` for NULL Checks:

```python
# ❌ WRONG:
users = db.query(User).filter(User.bio == None).all()  # Doesn't work!

# ✅ CORRECT:
users = db.query(User).filter(User.bio.is_(None)).all()
# OR:
users = db.query(User).filter(User.bio == None).all()  # SQLAlchemy handles this now
```

### 3. Not Closing Sessions:

```python
# ❌ WRONG - Memory leak:
db = SessionLocal()
user = db.query(User).first()
# Missing db.close()!

# ✅ CORRECT:
with SessionLocal() as db:
    user = db.query(User).first()
# Auto-closes
```

### 4. Mixing Session and Detached Objects:

```python
# ❌ WRONG:
db1 = SessionLocal()
user = db1.query(User).first()
db1.close()

db2 = SessionLocal()
db2.add(user)  # Error! user is from a different session
db2.commit()

# ✅ CORRECT:
db1 = SessionLocal()
user = db1.query(User).first()
db1.expunge(user)  # Detach from session
db1.close()

db2 = SessionLocal()
db2.add(user)  # Now it works
db2.commit()
```

### 5. Not Using Transactions:

```python
# ❌ WRONG - If second insert fails, first one stays:
db.add(User(username="alice"))
db.commit()
db.add(Post(title="Post", author_id=999))  # Fails (no author 999)
db.commit()  # alice is still in DB!

# ✅ CORRECT - Both or neither:
try:
    db.add(User(username="alice"))
    db.add(Post(title="Post", author_id=999))
    db.commit()  # Both saved together
except:
    db.rollback()  # Undo both
```

---

## ✅ Production Checklist

### Before Deploying:

- [ ] **Disable `echo=True`** in `create_engine()` (stops printing SQL queries)
- [ ] **Use environment variables** for `DATABASE_URL` (never hardcode passwords)
- [ ] **Set up Alembic** for migrations
- [ ] **Add connection pooling** (`pool_size=20, max_overflow=10`)
- [ ] **Add indexes** to frequently queried columns
- [ ] **Use `select_in_loading` or `joinedload`** to avoid N+1 queries
- [ ] **Implement retry logic** for database connection failures
- [ ] **Add logging** (not `echo=True`, use proper logging)
- [ ] **Use async SQLAlchemy** if handling high traffic
- [ ] **Set up database backups** (PostgreSQL `pg_dump`)

### Environment Variables:

```python
# Use .env file:
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
```

`.env`:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

---

## 📝 Quick Reference Cheat Sheet

### Setup:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://user:pass@host:port/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

### Models:

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
```

### CRUD:

```python
# Create:
user = User(username="ahad")
db.add(user)
db.commit()

# Read:
user = db.query(User).filter(User.username == "ahad").first()
users = db.query(User).all()

# Update:
user.username = "new_name"
db.commit()

# Delete:
db.delete(user)
db.commit()
```

### Relationships:

```python
class Post(Base):
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

class User(Base):
    posts = relationship("Post", back_populates="author")
```

### FastAPI:

```python
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    return db_user
```

---

## 🎯 Your Learning Path

### ✅ Week 1: SQLAlchemy Basics
- [ ] Set up database connection
- [ ] Create User model
- [ ] Practice CRUD operations in Python REPL
- [ ] Verify in pgweb

### ✅ Week 2: Relationships
- [ ] Add Post model with foreign key
- [ ] Practice one-to-many relationships
- [ ] Add many-to-many (tags)

### ✅ Week 3: FastAPI Integration
- [ ] Build REST API with CRUD endpoints
- [ ] Add Pydantic schemas
- [ ] Separate CRUD logic into `crud.py`

### ✅ Week 4: Production Features
- [ ] Set up Alembic migrations
- [ ] Add authentication (JWT + password hashing)
- [ ] Optimize queries (eager loading)
- [ ] Deploy to production

---

## 🔥 Final Thoughts

**SQLAlchemy is powerful but has a learning curve.** The key is:

1. **Start simple** - Just CRUD operations with one table
2. **Add relationships** - Foreign keys, joins
3. **Integrate with FastAPI** - Build a real API
4. **Optimize** - Fix N+1 queries, add indexes

You now have the full picture: from raw SQL to production-ready FastAPI apps with SQLAlchemy. Go build something real. 🚀

---

**Saved:** `sqlalchemy-fastapi-guide.md` | Last updated: Feb 2026
**Author:** Your battle-hardened SQLAlchemy knowledge, forged in production.
