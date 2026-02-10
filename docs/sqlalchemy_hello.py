# Tools to define table structure
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
# Creates session factory (sessions = conversations with DB)
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Step 1: Create connection to database
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Did you load .env?")
print(DATABASE_URL)

"""
Engine is the connection manager. It:
Holds connection details (username, password, host, database name)
Manages connection pool (reuses connections instead of creating new ones)
Doesn't actually connect yet (lazy connection)"""
engine = create_engine(DATABASE_URL, echo=True)

# Step 2: Create base class for models
"""
Base is a class factory. Every model you create will inherit from it.
Why it exists:
SQLAlchemy needs to track all your models. Base keeps that registry.
Mental model:
Base = parent class that all your table classes inherit from."""
Base = declarative_base()

# Step 3: Define a table as a Python class
# A Python class that inherits from Base. This class represents the products table
class Product(Base):
    # actual table name in PostgreSQL.
    __tablename__ = "products"
    #defines columns
    id = Column(Integer, primary_key=True)# unique identifier, auto-increments
    name = Column(String)
    price = Column(Integer)

# Step 4: Create the table in database
"""Looks at all classes that inherit from Base
Generates CREATE TABLE statements
Executes them in PostgreSQL
This creates the 'products' table if it doesn't exist"""
Base.metadata.create_all(engine)

# Step 5: Create a session (conversation with database)
"""session is a conversation with the database. It:
- Tracks changes (adds, updates, deletes)
- Executes them when you call `commit()`
- Rolls back if errors happen"""
Session = sessionmaker(bind=engine)# Tie sessions to this database connection
session = Session()

# Step 6: Create a new product (INSERT-CREATE)
# Creates a Python object. This is just a Python object in memory. Nothing in database yet.
laptop = Product(name="Laptop", price=1000)
# Stages the object for insertion. Still not in database.
session.add(laptop)
# Now it executes: INSERT INTO products (name, price) VALUES ('Laptop', 1000);
"""After commit:
laptop.id is now populated (PostgreSQL auto-generated it)
Object is in database"""
session.commit()

# Step 7: Query products (SELECT-READ)
# Start a query on the products table
all_products = session.query(Product).all()# Get all rows
for product in all_products:
    # Returns: List of Product objects (not tuples).
    print(f"ID: {product.id}, Name: {product.name}, Price: {product.price}")

# Step 8: Find specific product
"""
What this does:
.filter(Product.name == "Laptop") = WHERE clause
.first() = Get first result
"""
laptop = session.query(Product).filter(Product.name == "Laptop").first()
"""
Generates:
SELECT * FROM products WHERE name = 'Laptop' LIMIT 1;
Returns:
Single Product object (or None if not found).
"""
print(f"Found: {laptop.name}, Price: {laptop.price}") # pyright: ignore[reportOptionalMemberAccess]

# Step 9: Update product (UPDATE)
"""
Change attribute on Python object
session.commit() = SQLAlchemy detects the change and executes:
UPDATE products SET price = 900 WHERE id = 1;
"""
laptop.price = 900  # type: ignore
session.commit()

# Step 10: Delete product (DELETE)
session.delete(laptop) # Mark for deletion
# session.commit() = Execute: DELETE FROM products WHERE id = 1;
session.commit()

"""Shuts the door on the database conversation you were having.
Releases the database connection back to the pool"""
session.close()
