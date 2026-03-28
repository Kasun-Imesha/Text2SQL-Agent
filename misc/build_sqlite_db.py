import sqlite3
import csv
import os
from pathlib import Path

DB_FILE = "../test_db.db"
DATA_DIR = "../data"

def initialize_database():
    """Initialize the SQLite database with schema and data from CSV files"""
    
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Drop existing tables if they exist (for fresh start)
    cursor.execute("DROP TABLE IF EXISTS order_details")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS suppliers")
    cursor.execute("DROP TABLE IF EXISTS customers")
    
    # Create tables
    cursor.execute("""
    CREATE TABLE customers (
        customer_id TEXT PRIMARY KEY,
        company_name TEXT,
        contact_name TEXT,
        city TEXT,
        country TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE suppliers (
        supplier_id INTEGER PRIMARY KEY,
        company_name TEXT,
        contact_name TEXT,
        city TEXT,
        country TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT,
        supplier_id INTEGER,
        category TEXT,
        unit_price REAL,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id TEXT,
        order_date DATE,
        ship_city TEXT,
        freight REAL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE order_details (
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        unit_price REAL,
        PRIMARY KEY (order_id, product_id),
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)
    
    conn.commit()
    
    # Import CSV data
    csv_files = [
        ("customers.csv", "customers"),
        ("suppliers.csv", "suppliers"),
        ("products.csv", "products"),
        ("orders.csv", "orders"),
        ("order_details.csv", "order_details"),
    ]
    
    for csv_file, table_name in csv_files:
        csv_path = os.path.join(DATA_DIR, csv_file)
        
        if not os.path.exists(csv_path):
            print(f"Warning: {csv_path} not found, skipping...")
            continue
        
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Get header row
            
            # Insert data
            placeholders = ", ".join(["?" for _ in headers])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
            
            for row in reader:
                cursor.execute(insert_sql, row)
        
        conn.commit()
        print(f"✓ Imported {csv_file} into {table_name}")
    
    conn.close()
    print(f"\n✓ Database initialized successfully! Created {DB_FILE}")
    
    # Verify
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM customers")
    customer_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"✓ Verification: {customer_count} customers in database")

if __name__ == "__main__":
    initialize_database()
