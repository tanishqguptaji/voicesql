"""
build_db.py — Creates and seeds the VoiceSQL sample database.

This implements the exact schema defined in docs/SCHEMA.md:
customers, products, orders, order_items.

Run this once to create database/sample.db:
    python database/build_db.py
"""

import sqlite3
import os
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "sample.db")

SCHEMA_SQL = """
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    city TEXT,
    signup_date TEXT NOT NULL
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL CHECK (price >= 0)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending','shipped','delivered','cancelled')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
"""

CUSTOMERS = [
    ("Alice Kumar", "alice.kumar@example.com", "Mumbai"),
    ("Bob Rao", "bob.rao@example.com", "Delhi"),
    ("Chetan Mehta", "chetan.mehta@example.com", "Bengaluru"),
    ("Divya Nair", "divya.nair@example.com", "Chennai"),
    ("Esha Sharma", "esha.sharma@example.com", "Pune"),
    ("Farhan Ali", "farhan.ali@example.com", "Hyderabad"),
    ("Gauri Joshi", "gauri.joshi@example.com", "Mumbai"),
    ("Harsh Patel", "harsh.patel@example.com", "Ahmedabad"),
    ("Isha Kapoor", "isha.kapoor@example.com", "Delhi"),
    ("Jatin Verma", "jatin.verma@example.com", "Jaipur"),
    ("Kavya Iyer", "kavya.iyer@example.com", "Chennai"),
    ("Lakshay Singh", "lakshay.singh@example.com", "Delhi"),
    ("Meera Pillai", "meera.pillai@example.com", "Kochi"),
    ("Nikhil Das", "nikhil.das@example.com", "Kolkata"),
    ("Priya Reddy", "priya.reddy@example.com", "Hyderabad"),
]

PRODUCTS = [
    ("Wireless Mouse", "Electronics", 24.99),
    ("Mechanical Keyboard", "Electronics", 59.99),
    ("USB-C Hub", "Electronics", 34.50),
    ("Bluetooth Speaker", "Electronics", 45.00),
    ("Noise Cancelling Headphones", "Electronics", 89.99),
    ("Cotton T-Shirt", "Apparel", 14.99),
    ("Denim Jacket", "Apparel", 54.99),
    ("Running Shoes", "Apparel", 64.99),
    ("Wool Sweater", "Apparel", 39.99),
    ("Leather Wallet", "Apparel", 29.99),
    ("Table Lamp", "Home", 22.50),
    ("Ceramic Mug Set", "Home", 18.99),
    ("Throw Blanket", "Home", 27.99),
    ("Scented Candle", "Home", 12.99),
    ("Kitchen Knife Set", "Home", 49.99),
]

STATUSES = ["delivered", "shipped", "pending", "delivered", "delivered", "cancelled"]


def random_date_within_months(months_back, seed):
    """Deterministic pseudo-random date within the last `months_back` months."""
    today = date.today()
    days_back = (seed * 37) % (months_back * 30)
    return today - timedelta(days=days_back)


def build():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA_SQL)

    for i, (name, email, city) in enumerate(CUSTOMERS):
        signup = random_date_within_months(24, i + 1).isoformat()
        cur.execute(
            "INSERT INTO customers (name, email, city, signup_date) VALUES (?, ?, ?, ?)",
            (name, email, city, signup),
        )

    for name, category, price in PRODUCTS:
        cur.execute(
            "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
            (name, category, price),
        )

    num_customers = len(CUSTOMERS)
    num_products = len(PRODUCTS)
    order_count = 40
    for o in range(1, order_count + 1):
        customer_id = (o % num_customers) + 1
        order_date = random_date_within_months(6, o).isoformat()
        status = STATUSES[o % len(STATUSES)]
        cur.execute(
            "INSERT INTO orders (customer_id, order_date, status) VALUES (?, ?, ?)",
            (customer_id, order_date, status),
        )
        order_id = cur.lastrowid

        # 1-3 items per order
        items_in_order = (o % 3) + 1
        for j in range(items_in_order):
            product_id = ((o * 3 + j) % num_products) + 1
            cur.execute("SELECT price FROM products WHERE product_id = ?", (product_id,))
            unit_price = cur.fetchone()[0]
            quantity = (j % 3) + 1
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, product_id, quantity, unit_price),
            )

    conn.commit()

    # Verification counts
    counts = {}
    for table in ["customers", "products", "orders", "order_items"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cur.fetchone()[0]

    conn.close()
    print("Database built successfully at:", DB_PATH)
    for table, count in counts.items():
        print(f"  {table}: {count} rows")


if __name__ == "__main__":
    build()
