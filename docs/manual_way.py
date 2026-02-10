import psycopg2 #A wire between Python and PostgreSQL.
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Did you load .env?")
print(DATABASE_URL)

# 1) Open a TCP connection to Postgres
conn = psycopg2.connect(DATABASE_URL)

# 2) Create a cursor (this is your tool to send SQL commands)
cursor = conn.cursor()

# 3) Send an INSERT query with safe parameter binding
cursor.execute(
    """
    INSERT INTO items (name, price, description, cost_price, supplier_secret)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
    """,
    ("Mia", 999.99, "Annoying asf", 600.0, "SECRET-NONE")
)

# 4) Get the ID of the row Postgres just created
result = cursor.fetchone()
item_id = result[0] if result else None

# 5) Make the change permanent
conn.commit()

# 6) Query the row back
cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
row = cursor.fetchone()

print(row)

# 7) Clean up
cursor.close()
conn.close()

# You get a tuple: (1, 'Laptop', 999.99, 'Gaming laptop')
# How do you know which column is which?
# row[0]? row[1]? Fragile as fuck.
