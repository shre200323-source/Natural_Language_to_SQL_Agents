import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "sales.db"   # works from any folder

# Connect to database
conn = sqlite3.connect(DB_PATH)

# Create cursor
cursor = conn.cursor()

# Get all table names
cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""")

tables = cursor.fetchall()

print("Tables in database:")

for table in tables:
    print(table[0])

# Read all records from customers table
cursor.execute("SELECT * FROM customers")

rows = cursor.fetchall()

print("\nCustomer records:")

for row in rows:
    print(row)

conn.close()