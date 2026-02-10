from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Step 1: Create connection to database
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Did you load .env?")
print(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=True)

# Step 2: Create base class for models
Base = declarative_base()

# Step 3: Define a table as a Python class
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)

# Step 4: Create the table in database
Base.metadata.create_all(engine)

# Step 5: Create a session (conversation with database)
Session = sessionmaker(bind=engine)
session = Session()

# Step 6: Create a new product (INSERT)
laptop = Product(name="Laptop", price=1000)
session.add(laptop)
session.commit()

# Step 7: Query products (SELECT)
all_products = session.query(Product).all()
for product in all_products:
    print(f"ID: {product.id}, Name: {product.name}, Price: {product.price}")

# Step 8: Find specific product
laptop = session.query(Product).filter(Product.name == "Laptop").first()
print(f"Found: {laptop.name}, Price: {laptop.price}")

# Step 9: Update product (UPDATE)
laptop.price = 900
session.commit()

# Step 10: Delete product (DELETE)
session.delete(laptop)
session.commit()

session.close()
