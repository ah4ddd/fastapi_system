# PostgreSQL + SQL Cheat Sheet 🧠

---

# 0. THE BIG HIERARCHY

```text id="x1v8m4"
PostgreSQL Server
    ↓
Databases
    ↓
Tables
    ↓
Rows
    ↓
Columns
```

---

# 1. TERMINAL VS POSTGRESQL SHELL

---

# Linux / ZSH Shell

```text id="m7q2p9"
➜ ~
```

Used for:

* cd
* ls
* pwd
* psql

---

# PostgreSQL Shell

```text id="n4x6w1"
postgres=#
```

Used for:

* SQL
* SELECT
* INSERT
* CREATE TABLE

---

# Connect To PostgreSQL

```bash id="f2m9r5"
psql -U postgres
```

---

# Quit PostgreSQL

```sql id="t6q3w8"
\q
```

---

# 2. DATABASE COMMANDS

---

# Show Databases

```sql id="v8n1x4"
\l
```

---

# Create Database

```sql id="k3m7p2"
CREATE DATABASE gym_tracker;
```

---

# Connect To Database

```sql id="c9q4w1"
\c gym_tracker
```

Prompt changes:

```text id="p5x8m6"
gym_tracker=#
```

---

# Show Current Database

```sql id="z2v7n3"
SELECT current_database();
```

---

# Show Current User

```sql id="r1m5q9"
SELECT current_user;
```

---

# 3. TABLE COMMANDS

---

# Show Tables

```sql id="y4x2m8"
\dt
```

---

# Describe Table

```sql id="u7q1n5"
\d users
```

Shows:

* columns
* types
* constraints

---

# Create Table

```sql id="j9m3v2"
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    age INTEGER
);
```

---

# Delete Table

```sql id="w5x8p1"
DROP TABLE users;
```

⚠️ Permanently deletes table + data.

---

# 4. DATA TYPES

| Type      | Meaning                |
| --------- | ---------------------- |
| SERIAL    | auto-increment integer |
| INTEGER   | whole number           |
| TEXT      | string                 |
| BOOLEAN   | true/false             |
| REAL      | decimal                |
| TIMESTAMP | date + time            |

---

# 5. CONSTRAINTS

---

# PRIMARY KEY

Unique identity.

```sql id="b8q2m7"
id SERIAL PRIMARY KEY
```

---

# NOT NULL

Cannot be empty.

```sql id="f1x6w3"
username TEXT NOT NULL
```

---

# UNIQUE

No duplicates.

```sql id="n5v9p2"
email TEXT UNIQUE
```

---

# FOREIGN KEY

Connects tables.

```sql id="h3m8q4"
user_id INTEGER REFERENCES users(id)
```

Meaning:

```text id="q7x1w5"
this value must exist in users.id
```

---

# 6. CRUD OPERATIONS

CRUD =

* Create
* Read
* Update
* Delete

---

# INSERT (Create)

```sql id="m2q7x8"
INSERT INTO users(username, age)
VALUES ('ahad', 21);
```

---

# SELECT (Read)

```sql id="t4v1m9"
SELECT * FROM users;
```

---

# UPDATE

```sql id="x8n3q5"
UPDATE users
SET age = 22
WHERE username = 'ahad';
```

⚠️ NEVER forget WHERE unless updating all rows.

---

# DELETE

```sql id="z1m6p4"
DELETE FROM users
WHERE id = 3;
```

⚠️ Without WHERE deletes EVERYTHING.

---

# 7. FILTERING

---

# WHERE

```sql id="r5x2n8"
SELECT * FROM users
WHERE age > 18;
```

---

# Multiple Conditions

```sql id="k9q4v1"
SELECT * FROM users
WHERE age > 18
AND username = 'ahad';
```

---

# 8. SORTING + LIMITING

---

# ORDER BY

```sql id="j7m1x3"
SELECT * FROM users
ORDER BY age DESC;
```

---

# LIMIT

```sql id="u4q8n2"
SELECT * FROM users
LIMIT 5;
```

---

# 9. AGGREGATE FUNCTIONS

---

# COUNT

```sql id="c3v7m5"
SELECT COUNT(*) FROM users;
```

---

# AVG

```sql id="n8x2q4"
SELECT AVG(age) FROM users;
```

---

# MAX

```sql id="p6m1w9"
SELECT MAX(age) FROM users;
```

---

# MIN

```sql id="y2q5v8"
SELECT MIN(age) FROM users;
```

---

# SUM

```sql id="f9x4m1"
SELECT SUM(duration) FROM workouts;
```

---

# 10. GROUP BY

Groups similar rows before aggregation.

---

# Example

```sql id="m4q7x2"
SELECT user_id, COUNT(*)
FROM workouts
GROUP BY user_id;
```

Result:

| user_id | count |
| ------- | ----- |
| 1       | 2     |
| 2       | 1     |

Meaning:

* user 1 has 2 workouts
* user 2 has 1 workout

---

# Better Grouping

```sql id="t1v8n4"
SELECT users.id, users.username, COUNT(*)
FROM users
JOIN workouts
ON users.id = workouts.user_id
GROUP BY users.id, users.username;
```

---

# 11. RELATIONAL DATABASE THINKING

THIS is the core concept.

---

# Example Structure

```text id="w8m3q1"
users
   ↓
workouts
   ↓
exercises
```

---

# users Table

| id | username |
| -- | -------- |
| 1  | ahad     |

---

# workouts Table

| id | workout_name | user_id |
| -- | ------------ | ------- |
| 1  | Push Day     | 1       |

---

# exercises Table

| id | exercise_name | workout_id |
| -- | ------------- | ---------- |
| 1  | Pushups       | 1          |

---

# Relationships

```text id="g2x7v4"
users.id
    ↓
workouts.user_id

workouts.id
    ↓
exercises.workout_id
```

---

# 12. JOINS

JOIN reconnects related tables temporarily.

It DOES NOT:

* create tables
* permanently merge data

It only combines rows during query execution.

---

# Simple JOIN

```sql id="r6m2q9"
SELECT users.username, workouts.workout_name
FROM users
JOIN workouts
ON users.id = workouts.user_id;
```

---

# Multi-Table JOIN

```sql id="x1v5n8"
SELECT users.username,
       workouts.workout_name,
       exercises.exercise_name
FROM users
JOIN workouts
ON users.id = workouts.user_id
JOIN exercises
ON workouts.id = exercises.workout_id;
```

---

# Read JOIN Like English

```text id="k4q9m3"
Start from users
↓
connect workouts where IDs match
↓
connect exercises where IDs match
```

---

# 13. FOREIGN KEYS

---

# Example

```sql id="z7n2x5"
user_id INTEGER REFERENCES users(id)
```

Means:

```text id="u3m8q1"
workouts.user_id
must point to
existing users.id
```

---

# VALID

```sql id="b5v1m7"
user_id = 1
```

if user 1 exists.

---

# INVALID

```sql id="j8q4x2"
user_id = 999
```

if user 999 does not exist.

PostgreSQL blocks invalid relationships.

---

# 14. SERIAL + SEQUENCES

---

# SERIAL

```sql id="t2m7v9"
id SERIAL PRIMARY KEY
```

creates:

* integer column
* auto-increment sequence

---

# IMPORTANT

Usually DO NOT manually insert IDs.

GOOD:

```sql id="p4x1n6"
INSERT INTO users(username, age)
VALUES ('maya', 24);
```

---

# BAD (usually)

```sql id="f7q3m2"
INSERT INTO users(id, username, age)
VALUES (1, 'maya', 24);
```

---

# Sequences Do NOT Reuse Deleted IDs

IDs:

* identify rows
* not row counts

Gaps are normal.

---

# 15. MOST COMMON BEGINNER ERRORS

---

# Forgot Semicolon

Wrong:

```sql id="n1v8x5"
SELECT * FROM users
```

Correct:

```sql id="m6q2p9"
SELECT * FROM users;
```

---

# Typo In Column Name

Wrong:

```sql id="z3x7m1"
temprature
```

Correct:

```sql id="r8q4v6"
temperature
```

---

# Running SQL In Linux Shell

Wrong place:

```text id="w5n1m8"
➜ ~
```

Correct place:

```text id="y7q2x4"
postgres=#
```

---

# Missing Quotes

Wrong:

```sql id="j4m9v2"
WHERE username = ahad
```

Correct:

```sql id="u1x6q5"
WHERE username = 'ahad'
```

---

# 16. NAMING CONVENTIONS

---

# Table/Column Names

Use:

```text id="p8v3m7"
snake_case
```

Examples:

* workout_name
* user_id
* created_at

---

# Human Data

Use normal formatting:

```text id="c5q1x9"
'Chest Press'
'Full Body Day'
```

---

# 17. YOUR CURRENT DATABASE STRUCTURE

```text id="h9m4q2"
gym_tracker
│
├── users
│      ├── id
│      ├── username
│      └── age
│
├── workouts
│      ├── id
│      ├── workout_name
│      ├── duration
│      └── user_id
│
└── exercises
       ├── id
       ├── exercise_name
       ├── sets
       ├── reps
       └── workout_id
```

---

# 18. MOST IMPORTANT MENTAL MODEL

Databases are NOT:

* magic
* spreadsheets only
* random syntax

Databases are:

```text id="v1q8m5"
structured connected data
```

Everything comes down to:

```text id="n7x2p4"
What exists?
What belongs to what?
How are things related?
```

That’s backend engineering.
