# 🐘 PostgreSQL: The No-Bullshit Guide

**Personal SQL cheat sheet for actually getting shit done.**

---

## 📚 Table of Contents

1. [What the Hell is PostgreSQL?](#what-the-hell-is-postgresql)
2. [The Hierarchy: Database → Schema → Table](#the-hierarchy)
3. [Data Types You'll Actually Use](#data-types)
4. [Core SQL Commands (The 80% You'll Use Daily)](#core-commands)
5. [Creating Tables (DDL)](#creating-tables)
6. [Reading Data (SELECT - The Most Important)](#reading-data)
7. [Writing Data (INSERT, UPDATE, DELETE)](#writing-data)
8. [Filtering & Sorting (WHERE, ORDER BY, LIMIT)](#filtering-sorting)
9. [Combining Tables (JOINs - The Hard Part)](#joins)
10. [Grouping & Aggregating (GROUP BY, COUNT, SUM)](#grouping)
11. [Advanced Shit (Subqueries, CTEs, Window Functions)](#advanced)
12. [FastAPI + SQLAlchemy Integration](#fastapi-integration)
13. [Common Mistakes (And How to Avoid Them)](#common-mistakes)
14. [Quick Reference Cheat Sheet](#cheat-sheet)

---

## 🤔 What the Hell is PostgreSQL?

**PostgreSQL** (often called "Postgres") is a **relational database management system (RDBMS)**. Think of it as:

- 🗄️ A **filing cabinet** that stores structured data (tables with rows and columns)
- 🔍 A **query engine** that lets you ask questions about that data (using SQL)
- 🔒 A **security system** that controls who can access what
- ⚡ A **performance optimizer** that makes queries run fast

### Why Not Just Use Excel?

| Feature | Excel | PostgreSQL |
|---------|-------|------------|
| Max rows | ~1 million | **Billions** |
| Multi-user | ❌ Shared files get corrupted | ✅ Thousands of concurrent users |
| Speed | 🐌 Slow with 100k+ rows | ⚡ Lightning fast with proper indexes |
| Data integrity | ❌ Anyone can break formulas | ✅ Strict rules (constraints, foreign keys) |
| Automation | 🤷 Manual macros | ✅ Code-driven (FastAPI, scripts) |

**Bottom line:** Excel is for quick analysis. PostgreSQL is for building real applications.

---

## 🏗️ The Hierarchy: Database → Schema → Table

```
PostgreSQL Server (The entire filing cabinet)
  │
  ├─ 📦 Database: postgres (Default drawer)
  │   ├─ 📁 Schema: public (Default folder)
  │   │   ├─ 📄 Table: users
  │   │   ├─ 📄 Table: posts
  │   │   └─ 📄 Table: comments
  │   └─ 📁 Schema: private
  │       └─ 📄 Table: secrets
  │
  ├─ 📦 Database: blog_app (Your FastAPI project)
  │   └─ 📁 Schema: public
  │       ├─ 📄 Table: articles
  │       └─ 📄 Table: authors
  │
  └─ 📦 Database: test_db (For experiments)
```

### Key Concepts:

- **Database:** A container for related data. One project = one database (usually).
- **Schema:** A namespace inside a database. 95% of the time, you'll use `public` (the default).
- **Table:** The actual data structure (rows and columns). This is what you interact with 99% of the time.

### How to Switch Databases:

```sql
-- In psql terminal:
\c blog_app  -- Connect to blog_app database

-- In pgweb:
-- Restart pgweb with a different --db flag:
-- pgweb --host=localhost --user=postgres --db=blog_app --pass=yourpass
```

---

## 🧱 Data Types You'll Actually Use

When creating tables, you need to specify what **type** of data each column holds.

### The Essential Types:

| Type | What It Stores | Example | When to Use |
|------|----------------|---------|-------------|
| `SERIAL` | Auto-incrementing integer | `1, 2, 3, 4...` | **Primary keys (IDs)** |
| `INTEGER` / `INT` | Whole numbers | `42, -17, 0` | Counts, ages, quantities |
| `BIGINT` | Really big integers | `9223372036854775807` | User IDs, timestamps (milliseconds) |
| `TEXT` | Any length string | `"Hello world"` | **Usernames, emails, content** |
| `VARCHAR(n)` | String with max length | `VARCHAR(100)` | Rarely needed (use TEXT instead) |
| `BOOLEAN` | True/False | `true, false` | Flags (is_active, is_admin) |
| `TIMESTAMP` | Date + Time | `2026-02-07 22:30:00` | created_at, updated_at |
| `DATE` | Just the date | `2026-02-07` | Birthdays, deadlines |
| `NUMERIC(p,s)` | Precise decimals | `19.99, 0.001` | Money, measurements |
| `JSONB` | JSON data | `{"name": "John"}` | Flexible/dynamic data |

### 🚨 Common Beginner Mistakes:

- ❌ Using `VARCHAR(255)` everywhere → Use `TEXT` instead (it's faster and more flexible in Postgres)
- ❌ Using `FLOAT` for money → Use `NUMERIC(10,2)` to avoid rounding errors
- ❌ Storing dates as strings → Use `DATE` or `TIMESTAMP`

---

## ⚡ Core SQL Commands (The 80% You'll Use Daily)

SQL is divided into categories based on what the command **does**:

### 1️⃣ **DDL (Data Definition Language)** - Structure

| Command | What It Does |
|---------|--------------|
| `CREATE TABLE` | Make a new table |
| `ALTER TABLE` | Modify an existing table (add/remove columns) |
| `DROP TABLE` | Delete a table (⚠️ **permanent**) |
| `TRUNCATE TABLE` | Delete all rows but keep the table structure |

### 2️⃣ **DML (Data Manipulation Language)** - Data

| Command | What It Does |
|---------|--------------|
| `INSERT` | Add new rows |
| `SELECT` | Read/query data (90% of what you'll do) |
| `UPDATE` | Change existing rows |
| `DELETE` | Remove rows |

### 3️⃣ **DCL (Data Control Language)** - Permissions

| Command | What It Does |
|---------|--------------|
| `GRANT` | Give user permissions |
| `REVOKE` | Remove permissions |

*(You won't touch this until you're deploying to production)*

### 4️⃣ **TCL (Transaction Control Language)** - Safety

| Command | What It Does |
|---------|--------------|
| `BEGIN` | Start a transaction |
| `COMMIT` | Save changes permanently |
| `ROLLBACK` | Undo changes (if you fucked up) |

---

## 🛠️ Creating Tables (DDL)

### Basic Syntax:

```sql
CREATE TABLE table_name (
    column_name DATA_TYPE CONSTRAINTS,
    another_column DATA_TYPE CONSTRAINTS,
    ...
);
```

### Example: A Simple Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,           -- Auto-incrementing ID
    username TEXT NOT NULL UNIQUE,   -- Required, must be unique
    email TEXT NOT NULL UNIQUE,      -- Required, must be unique
    password_hash TEXT NOT NULL,     -- Required (never store plain passwords!)
    is_active BOOLEAN DEFAULT true,  -- Defaults to true if not specified
    created_at TIMESTAMP DEFAULT NOW() -- Auto-fills with current time
);
```

### 🔑 Common Constraints:

| Constraint | What It Does | Example |
|------------|--------------|---------|
| `PRIMARY KEY` | Unique identifier (no duplicates, never NULL) | `id SERIAL PRIMARY KEY` |
| `NOT NULL` | Column can't be empty | `username TEXT NOT NULL` |
| `UNIQUE` | No two rows can have the same value | `email TEXT UNIQUE` |
| `DEFAULT` | Auto-fills if you don't provide a value | `is_active BOOLEAN DEFAULT true` |
| `CHECK` | Custom validation rule | `age INT CHECK (age >= 18)` |
| `FOREIGN KEY` | Links to another table (relationships) | See JOINs section |

### Example: A Blog Posts Table (With Foreign Key)

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    author_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    -- This links to the users table:
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**What `ON DELETE CASCADE` means:**
If you delete a user, all their posts get deleted automatically.

### 🗑️ Deleting a Table:

```sql
DROP TABLE users;  -- ⚠️ PERMANENT. No undo.
```

### ✏️ Modifying a Table (Adding a Column):

```sql
ALTER TABLE users ADD COLUMN bio TEXT;
```

### ✏️ Renaming a Column:

```sql
ALTER TABLE users RENAME COLUMN bio TO biography;
```

---

## 🔍 Reading Data (SELECT - The Most Important Command)

**This is 90% of what you'll do in SQL.** Everything else builds on `SELECT`.

### Basic Syntax:

```sql
SELECT column1, column2, ...
FROM table_name;
```

### Example 1: Get Everything

```sql
SELECT * FROM users;  -- The * means "all columns"
```

### Example 2: Get Specific Columns

```sql
SELECT username, email FROM users;
```

### Example 3: Get Unique Values

```sql
SELECT DISTINCT username FROM users;  -- No duplicates
```

### Example 4: Renaming Columns (Aliases)

```sql
SELECT username AS name, email AS contact FROM users;
```

Output:
```
 name  |      contact
-------+-------------------
 ahad  | ahad@example.com
```

---

## 🎯 Filtering & Sorting (WHERE, ORDER BY, LIMIT)

### 1️⃣ **WHERE** - Filter Rows

```sql
SELECT * FROM users WHERE is_active = true;
```

### Common WHERE Operators:

| Operator | Example | Meaning |
|----------|---------|---------|
| `=` | `WHERE age = 25` | Equals |
| `!=` or `<>` | `WHERE age != 25` | Not equals |
| `>`, `<`, `>=`, `<=` | `WHERE age > 18` | Comparisons |
| `BETWEEN` | `WHERE age BETWEEN 18 AND 30` | Range (inclusive) |
| `IN` | `WHERE country IN ('USA', 'UK')` | Match any value in list |
| `LIKE` | `WHERE email LIKE '%@gmail.com'` | Pattern matching |
| `ILIKE` | `WHERE username ILIKE 'john%'` | Case-insensitive LIKE |
| `IS NULL` | `WHERE bio IS NULL` | Check for empty values |
| `IS NOT NULL` | `WHERE bio IS NOT NULL` | Check for non-empty |

### Combining Conditions:

```sql
-- AND: Both conditions must be true
SELECT * FROM users WHERE is_active = true AND age > 18;

-- OR: At least one condition must be true
SELECT * FROM users WHERE country = 'USA' OR country = 'UK';

-- Combining with parentheses:
SELECT * FROM users WHERE (age > 18 AND age < 30) OR country = 'USA';
```

### 2️⃣ **ORDER BY** - Sort Results

```sql
-- Ascending (default):
SELECT * FROM users ORDER BY created_at;

-- Descending:
SELECT * FROM users ORDER BY created_at DESC;

-- Multiple columns:
SELECT * FROM users ORDER BY country ASC, age DESC;
```

### 3️⃣ **LIMIT** - Get Only N Rows

```sql
-- Get the 10 newest users:
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;

-- Skip the first 10, then get the next 10 (pagination):
SELECT * FROM users ORDER BY created_at DESC LIMIT 10 OFFSET 10;
```

---

## ✍️ Writing Data (INSERT, UPDATE, DELETE)

### 1️⃣ **INSERT** - Add New Rows

```sql
-- Single row:
INSERT INTO users (username, email, password_hash)
VALUES ('ahad', 'ahad@example.com', 'hashed_password_here');

-- Multiple rows:
INSERT INTO users (username, email, password_hash) VALUES
    ('john', 'john@example.com', 'hash1'),
    ('jane', 'jane@example.com', 'hash2'),
    ('bob', 'bob@example.com', 'hash3');
```

**💡 Pro Tip:** You don't need to specify `id`, `created_at`, or columns with `DEFAULT` values—they auto-fill.

### 2️⃣ **UPDATE** - Change Existing Rows

```sql
-- Update a single user:
UPDATE users
SET email = 'newemail@example.com'
WHERE username = 'ahad';

-- Update multiple columns:
UPDATE users
SET email = 'new@example.com', is_active = false
WHERE id = 5;

-- Update ALL rows (⚠️ dangerous):
UPDATE users SET is_active = true;  -- No WHERE = affects everyone
```

### 3️⃣ **DELETE** - Remove Rows

```sql
-- Delete a specific user:
DELETE FROM users WHERE username = 'ahad';

-- Delete all inactive users:
DELETE FROM users WHERE is_active = false;

-- Delete EVERYTHING (⚠️ VERY dangerous):
DELETE FROM users;  -- No WHERE = deletes all rows
```

**🚨 Safety Tip:** Always run a `SELECT` first to see what you're about to delete:

```sql
-- 1. Check what you're about to delete:
SELECT * FROM users WHERE is_active = false;

-- 2. If it looks right, change SELECT to DELETE:
DELETE FROM users WHERE is_active = false;
```

---

## 🔗 Combining Tables (JOINs - The Hard Part)

**Why JOINs matter:** Real apps have data split across multiple tables. JOINs let you combine them.

### Example Setup:

```sql
-- Users table:
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL
);

-- Posts table (links to users):
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Sample data:
INSERT INTO users (username) VALUES ('alice'), ('bob'), ('charlie');
INSERT INTO posts (title, user_id) VALUES
    ('Hello World', 1),
    ('SQL is fun', 1),
    ('My first post', 2);
```

### The 4 Types of JOINs:

#### 1️⃣ **INNER JOIN** - Only Matching Rows

```sql
SELECT users.username, posts.title
FROM users
INNER JOIN posts ON users.id = posts.user_id;
```

**Output:**
```
 username |     title
----------+---------------
 alice    | Hello World
 alice    | SQL is fun
 bob      | My first post
```

**What happened?** Charlie has no posts, so he's **excluded**.

#### 2️⃣ **LEFT JOIN** - All Rows from Left Table

```sql
SELECT users.username, posts.title
FROM users
LEFT JOIN posts ON users.id = posts.user_id;
```

**Output:**
```
 username |     title
----------+---------------
 alice    | Hello World
 alice    | SQL is fun
 bob      | My first post
 charlie  | NULL          ← Charlie appears even though he has no posts
```

#### 3️⃣ **RIGHT JOIN** - All Rows from Right Table

```sql
SELECT users.username, posts.title
FROM users
RIGHT JOIN posts ON users.id = posts.user_id;
```

*(Rarely used—just flip the tables and use LEFT JOIN instead)*

#### 4️⃣ **FULL OUTER JOIN** - Everything

```sql
SELECT users.username, posts.title
FROM users
FULL OUTER JOIN posts ON users.id = posts.user_id;
```

Shows users with no posts **AND** posts with no users (orphaned data).

### 🧠 Mental Model:

```
INNER JOIN: Only the overlap (Venn diagram intersection)
LEFT JOIN:  Everything from the left table + matches from the right
RIGHT JOIN: Everything from the right table + matches from the left
FULL OUTER: Everything from both tables
```

### Real-World Example: Get All Posts with Author Names

```sql
SELECT
    posts.id,
    posts.title,
    users.username AS author,
    posts.created_at
FROM posts
INNER JOIN users ON posts.user_id = users.id
ORDER BY posts.created_at DESC;
```

---

## 📊 Grouping & Aggregating (GROUP BY, COUNT, SUM)

**Use case:** "How many posts does each user have?" or "What's the total revenue per month?"

### Aggregate Functions:

| Function | What It Does | Example |
|----------|--------------|---------|
| `COUNT(*)` | Number of rows | `COUNT(*)` |
| `COUNT(column)` | Number of non-NULL values | `COUNT(email)` |
| `SUM(column)` | Add up numbers | `SUM(price)` |
| `AVG(column)` | Average | `AVG(age)` |
| `MIN(column)` | Smallest value | `MIN(price)` |
| `MAX(column)` | Largest value | `MAX(created_at)` |

### Example 1: Count Total Users

```sql
SELECT COUNT(*) AS total_users FROM users;
```

### Example 2: Count Posts Per User

```sql
SELECT
    users.username,
    COUNT(posts.id) AS post_count
FROM users
LEFT JOIN posts ON users.id = posts.user_id
GROUP BY users.username
ORDER BY post_count DESC;
```

**Output:**
```
 username | post_count
----------+------------
 alice    |          2
 bob      |          1
 charlie  |          0
```

### Example 3: Total Revenue Per Month

```sql
SELECT
    DATE_TRUNC('month', created_at) AS month,
    SUM(amount) AS total_revenue
FROM orders
GROUP BY month
ORDER BY month DESC;
```

### 🔍 **HAVING** - Filter After Grouping

```sql
-- Show only users with more than 5 posts:
SELECT
    user_id,
    COUNT(*) AS post_count
FROM posts
GROUP BY user_id
HAVING COUNT(*) > 5;
```

**Difference from WHERE:**
- `WHERE` filters rows **before** grouping
- `HAVING` filters rows **after** grouping

---

## 🚀 Advanced Shit (Subqueries, CTEs, Window Functions)

### 1️⃣ **Subqueries** - Query Inside a Query

```sql
-- Find users who have more posts than the average:
SELECT username
FROM users
WHERE id IN (
    SELECT user_id
    FROM posts
    GROUP BY user_id
    HAVING COUNT(*) > (SELECT AVG(post_count) FROM (
        SELECT COUNT(*) AS post_count FROM posts GROUP BY user_id
    ) AS counts)
);
```

**When to use:** Quick one-off checks. But it gets messy fast.

### 2️⃣ **CTEs (Common Table Expressions)** - Cleaner Subqueries

```sql
-- Same as above, but readable:
WITH user_post_counts AS (
    SELECT user_id, COUNT(*) AS post_count
    FROM posts
    GROUP BY user_id
),
average_posts AS (
    SELECT AVG(post_count) AS avg_count
    FROM user_post_counts
)
SELECT users.username
FROM users
JOIN user_post_counts ON users.id = user_post_counts.user_id
WHERE user_post_counts.post_count > (SELECT avg_count FROM average_posts);
```

**Why CTEs are better:** You can name intermediate steps, making complex queries readable.

### 3️⃣ **Window Functions** - The Advanced Power Tool

**Use case:** "Rank users by post count" or "Calculate running totals"

```sql
-- Rank users by number of posts:
SELECT
    users.username,
    COUNT(posts.id) AS post_count,
    RANK() OVER (ORDER BY COUNT(posts.id) DESC) AS rank
FROM users
LEFT JOIN posts ON users.id = posts.user_id
GROUP BY users.username;
```

**Output:**
```
 username | post_count | rank
----------+------------+------
 alice    |          2 |    1
 bob      |          1 |    2
 charlie  |          0 |    3
```

#### Common Window Functions:

| Function | What It Does |
|----------|--------------|
| `ROW_NUMBER()` | Sequential numbering (1, 2, 3...) |
| `RANK()` | Ranking with gaps for ties |
| `DENSE_RANK()` | Ranking without gaps |
| `LAG(column)` | Get previous row's value |
| `LEAD(column)` | Get next row's value |
| `SUM() OVER (...)` | Running total |

---

## 🐍 FastAPI + SQLAlchemy Integration

### The Setup:

```python
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Connection string:
DATABASE_URL = "postgresql://postgres:yourpass@localhost:5432/blog_app"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define a model (this becomes a table):
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)

# Create tables:
Base.metadata.create_all(bind=engine)
```

### FastAPI Endpoint Example:

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/")
def create_user(username: str, email: str, db: Session = Depends(get_db)):
    user = User(username=username, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username}

@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

### How It Works:

1. **SQLAlchemy** translates Python classes into SQL `CREATE TABLE` statements
2. Your **FastAPI** code calls methods like `db.add()` and `db.commit()`
3. **SQLAlchemy** converts those into `INSERT INTO users ...` queries
4. **PostgreSQL** executes the query and returns results
5. You verify everything in **pgweb** by running `SELECT * FROM users;`

---

## 🚨 Common Mistakes (And How to Avoid Them)

### 1. Forgetting `WHERE` in UPDATE/DELETE

```sql
-- 😱 DISASTER - Updates ALL users:
UPDATE users SET is_active = false;

-- ✅ CORRECT - Updates only one user:
UPDATE users SET is_active = false WHERE id = 5;
```

**Fix:** Always test with `SELECT` first:
```sql
SELECT * FROM users WHERE id = 5;  -- Check what you're targeting
UPDATE users SET is_active = false WHERE id = 5;  -- Then update
```

### 2. Using `VARCHAR(255)` Instead of `TEXT`

In PostgreSQL, `TEXT` is just as fast (or faster) than `VARCHAR`, and you don't have to guess the max length.

```sql
-- ❌ BAD:
username VARCHAR(50)  -- What if someone has a 51-char username?

-- ✅ GOOD:
username TEXT
```

### 3. Not Using Transactions for Multi-Step Operations

```sql
-- If the second INSERT fails, the first one stays (inconsistent data):
INSERT INTO users (username) VALUES ('alice');
INSERT INTO posts (title, user_id) VALUES ('Post', 999);  -- Fails (no user 999)

-- ✅ BETTER - Use a transaction:
BEGIN;
INSERT INTO users (username) VALUES ('alice') RETURNING id;  -- Save the ID
INSERT INTO posts (title, user_id) VALUES ('Post', 1);  -- Use the ID
COMMIT;  -- Only saves if both succeed
```

### 4. Storing Passwords in Plain Text

```sql
-- ❌ NEVER DO THIS:
INSERT INTO users (password) VALUES ('mypassword123');

-- ✅ ALWAYS HASH:
-- Use bcrypt in Python, then store the hash:
INSERT INTO users (password_hash) VALUES ('$2b$12$...');
```

### 5. Not Using Indexes (Slow Queries)

If you're searching by a column frequently, add an index:

```sql
-- Slow without an index:
SELECT * FROM users WHERE email = 'ahad@example.com';

-- Add an index:
CREATE INDEX idx_users_email ON users(email);

-- Now the query is 1000x faster.
```

---

## 📝 Quick Reference Cheat Sheet

### Create & Read:

```sql
-- Create a table:
CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT NOT NULL);

-- Insert data:
INSERT INTO users (username) VALUES ('ahad');

-- Read all data:
SELECT * FROM users;

-- Read specific columns:
SELECT username, email FROM users WHERE is_active = true;
```

### Update & Delete:

```sql
-- Update:
UPDATE users SET email = 'new@example.com' WHERE id = 1;

-- Delete:
DELETE FROM users WHERE id = 1;
```

### Joins:

```sql
-- INNER JOIN:
SELECT users.username, posts.title
FROM users
INNER JOIN posts ON users.id = posts.user_id;

-- LEFT JOIN (show all users, even without posts):
SELECT users.username, posts.title
FROM users
LEFT JOIN posts ON users.id = posts.user_id;
```

### Aggregates:

```sql
-- Count total users:
SELECT COUNT(*) FROM users;

-- Count posts per user:
SELECT user_id, COUNT(*) AS post_count
FROM posts
GROUP BY user_id;
```

### Sorting & Limiting:

```sql
-- Get 10 newest users:
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;
```

---

## 🎯 Your Learning Path

### ✅ Week 1: The Basics
- [ ] Create your first table (`users`)
- [ ] Insert 10 rows manually
- [ ] Practice SELECT with WHERE, ORDER BY, LIMIT
- [ ] Update and delete specific rows

### ✅ Week 2: Relationships
- [ ] Create a second table (`posts`) with a foreign key
- [ ] Practice INNER JOIN and LEFT JOIN
- [ ] Count posts per user (GROUP BY)

### ✅ Week 3: Real Project
- [ ] Build a mini blog database (users, posts, comments)
- [ ] Write queries to get "top 10 posts by comment count"
- [ ] Integrate with FastAPI + SQLAlchemy

### ✅ Week 4: Advanced
- [ ] Learn subqueries and CTEs
- [ ] Practice window functions (RANK, ROW_NUMBER)
- [ ] Add indexes to speed up queries

---

## 🔥 Final Thoughts

**SQL is simple in concept, hard in practice.** The only way to get good is to:

1. **Type the commands yourself** (don't copy-paste from ChatGPT)
2. **Break things** (mess up a query, then fix it)
3. **Build real projects** (your FastAPI app is perfect for this)


