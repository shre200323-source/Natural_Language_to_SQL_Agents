
import sqlite3
from pathlib import Path

# Locate the project root independently of the current terminal directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "sales.db"


def create_database():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Enable foreign key enforcement for this connection.
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            city TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL CHECK (price >= 0)
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL
                CHECK (status IN (
                    'pending', 'processing',
                    'shipped', 'delivered', 'cancelled'
                )),
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            unit_price REAL NOT NULL CHECK (unit_price >= 0),
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
        """)

        # Insert sample data only if the database is empty.
        existing = conn.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        if existing == 0:
            conn.executemany(
                """
                INSERT INTO customers
                    (customer_id, name, email, city)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (1, "Alice Johnson", "alice@example.com", "Bengaluru"),
                    (2, "Bob Smith", "bob@example.com", "Mumbai"),
                    (3, "Carol Davis", "carol@example.com", "Delhi"),
                    (4, "David Wilson", "david@example.com", "Chennai"),
                    (5, "Eva Brown", "eva@example.com", "Bengaluru"),
                    (6, "Frank Miller", "frank@example.com", "Pune"),
                ],
            )

            conn.executemany(
                """
                INSERT INTO products
                    (product_id, product_name, category, price)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (1, "Laptop", "Electronics", 60000.00),
                    (2, "Smartphone", "Electronics", 25000.00),
                    (3, "Headphones", "Accessories", 2500.00),
                    (4, "Office Chair", "Furniture", 8000.00),
                    (5, "Desk", "Furniture", 12000.00),
                    (6, "Keyboard", "Accessories", 1500.00),
                    (7, "Monitor", "Electronics", 18000.00),
                ],
            )

            conn.executemany(
                """
                INSERT INTO orders
                    (order_id, customer_id, order_date, status)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (101, 1, "2025-01-15", "delivered"),
                    (102, 2, "2025-02-10", "delivered"),
                    (103, 1, "2025-03-05", "shipped"),
                    (104, 3, "2025-03-20", "delivered"),
                    (105, 4, "2025-04-12", "pending"),
                    (106, 5, "2025-05-08", "delivered"),
                    (107, 2, "2025-06-18", "cancelled"),
                    (108, 6, "2025-07-22", "processing"),
                    (109, 3, "2025-08-14", "delivered"),
                    (110, 5, "2025-09-03", "shipped"),
                    (111, 4, "2025-10-11", "delivered"),
                    (112, 1, "2025-11-25", "delivered"),
                ],
            )

            conn.executemany(
                """
                INSERT INTO order_items
                    (order_item_id, order_id, product_id,
                     quantity, unit_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (1, 101, 1, 1, 60000),
                    (2, 101, 3, 2, 2500),
                    (3, 102, 2, 2, 25000),
                    (4, 102, 6, 1, 1500),
                    (5, 103, 7, 2, 18000),
                    (6, 103, 3, 1, 2500),
                    (7, 104, 1, 1, 58000),
                    (8, 104, 4, 2, 8000),
                    (9, 105, 5, 1, 12000),
                    (10, 105, 6, 2, 1500),
                    (11, 106, 2, 1, 25000),
                    (12, 106, 7, 1, 17500),
                    (13, 107, 1, 1, 60000),
                    (14, 108, 4, 1, 8000),
                    (15, 108, 3, 3, 2500),
                    (16, 109, 7, 3, 18000),
                    (17, 109, 2, 1, 25000),
                    (18, 110, 5, 2, 11500),
                    (19, 110, 6, 2, 1500),
                    (20, 111, 1, 2, 59000),
                    (21, 111, 4, 1, 8000),
                    (22, 112, 2, 2, 24000),
                    (23, 112, 3, 2, 2500),
                ],
            )

        conn.commit()

    print(f"Database ready: {DB_PATH}")


if __name__ == "__main__":
    create_database()
