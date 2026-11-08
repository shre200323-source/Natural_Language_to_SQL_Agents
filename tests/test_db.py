
import sqlite3
from pathlib import Path

DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sales.db"
)

with sqlite3.connect(DB_PATH) as conn:
    conn.execute("PRAGMA foreign_keys = ON")

    for table in ("customers", "products", "orders", "order_items"):
        count = conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        print(f"{table}: {count} rows")

    print("\nSample products:")
    rows = conn.execute("""
        SELECT product_name, category, price
        FROM products
        ORDER BY price DESC
    """).fetchall()

    for row in rows:
        print(row)
