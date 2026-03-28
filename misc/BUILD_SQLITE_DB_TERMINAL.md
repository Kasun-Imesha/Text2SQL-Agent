1. Open Command Prompt in your project folder
```
cd path\to\your\project\folder
```

2. Create the database and tables
```
sqlite3 test_db.db
```
Now you will be inside the sqlite db, run the following command to create the tables.
```
sqlite> .read data/test_db-schema_creation.sql
```

To verify the tables run,
```
sqlite> .tables
```

4. Import CSV data into each table
```
sqlite> .mode csv
sqlite> .headers on

sqlite> .import data/customers.csv customers
sqlite> .import data/suppliers.csv suppliers
sqlite> .import data/products.csv products
sqlite> .import data/orders.csv orders
sqlite> .import data/order_details.csv order_details
```

5. Verify the data
```
sqlite> SELECT COUNT(*) FROM customers;
sqlite> SELECT * FROM customers LIMIT 3;
```

6. Exit SQLite
```
sqlite> .quit
```
