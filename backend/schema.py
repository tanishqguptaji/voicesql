"""
schema.py — Plain-text schema description fed into every Claude API prompt
starting Day 4 (NL -> SQL translation). Keep this in sync with
database/build_db.py and docs/SCHEMA.md — if they drift, the AI will
generate SQL referencing columns that don't exist.
"""

DATABASE_SCHEMA = """
Table: customers
  - customer_id (INTEGER, PRIMARY KEY)
  - name (TEXT)
  - email (TEXT, UNIQUE)
  - city (TEXT)
  - signup_date (TEXT, format YYYY-MM-DD)

Table: products
  - product_id (INTEGER, PRIMARY KEY)
  - name (TEXT)
  - category (TEXT)
  - price (REAL)

Table: orders
  - order_id (INTEGER, PRIMARY KEY)
  - customer_id (INTEGER, FOREIGN KEY -> customers.customer_id)
  - order_date (TEXT, format YYYY-MM-DD)
  - status (TEXT, one of: 'pending', 'shipped', 'delivered', 'cancelled')

Table: order_items
  - order_item_id (INTEGER, PRIMARY KEY)
  - order_id (INTEGER, FOREIGN KEY -> orders.order_id)
  - product_id (INTEGER, FOREIGN KEY -> products.product_id)
  - quantity (INTEGER)
  - unit_price (REAL)

Relationships:
  - One customer has many orders (customers.customer_id -> orders.customer_id)
  - One order has many order_items (orders.order_id -> order_items.order_id)
  - One product appears in many order_items (products.product_id -> order_items.product_id)
  - Revenue for an order_item = quantity * unit_price
"""
