import psycopg2

conn = psycopg2.connect("postgresql://postgres:linuxpsql@localhost/fastapi_db")
cursor = conn.cursor()

cursor.execute(
    """
    INSERT INTO items (name, price, description, cost_price, supplier_secret)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
    """,
    ("SCARX", 999.99, "Gaming laptop", 600.00, "SECRET-XYZ")
)

result = cursor.fetchone()
item_id = result[0] if result else None

conn.commit()

cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
row = cursor.fetchone()

print(row)

cursor.close()
conn.close()
