import sqlite3
import subprocess
import logging
from collections import defaultdict

# -----------------------------
# Instrument Lookup
# -----------------------------

instruments = [
    {"name": "Apple Inc.", "ticker": "AAPL", "currency": "USD", "asset_class": "Equity"},
    {"name": "Microsoft Corporation", "ticker": "MSFT", "currency": "USD", "asset_class": "Equity"},
    {"name": "Alphabet Inc. Class A", "ticker": "GOOGL", "currency": "USD", "asset_class": "Equity"},
    {"name": "Amazon.com, Inc.", "ticker": "AMZN", "currency": "USD", "asset_class": "Equity"},
    {"name": "Tesla, Inc.", "ticker": "TSLA", "currency": "USD", "asset_class": "Equity"}
]

def lookup_instrument_by_ticker(ticker_symbol):
    for instrument in instruments:
        if instrument["ticker"] == ticker_symbol:
            return instrument
    return None

ticker_to_find = input("Enter ticker symbol to lookup: ").upper()
found_instrument = lookup_instrument_by_ticker(ticker_to_find)

if found_instrument:
    print(f"Instrument Found: {found_instrument['name']}")
    print(f"Ticker: {found_instrument['ticker']}")
    print(f"Currency: {found_instrument['currency']}")
    print(f"Asset Class: {found_instrument['asset_class']}")
else:
    print(f"Instrument with ticker '{ticker_to_find}' not found.")

# -----------------------------
# Dummy Market Data (Trinket-safe)
# -----------------------------

dummy_prices = {
    "AAPL": [190, 192, 191, 193],
    "MSFT": [330, 332, 331, 333],
    "GOOGL": [140, 141, 142, 143],
    "AMZN": [125, 126, 124, 127],
    "TSLA": [250, 252, 249, 253]
}

print("\nRecent Dummy Prices:")
for ticker, prices in dummy_prices.items():
    print(f"{ticker}: {prices}")

# -----------------------------
# Create Database
# -----------------------------

def create_and_populate_database():
    conn = sqlite3.connect('day_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            description TEXT,
            due_date DATE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subtasks (
            subtask_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            subtask_name TEXT NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (task_id) REFERENCES tasks (task_id)
        )
    ''')

    conn.commit()
    conn.close()

# -----------------------------
# Pipeline Runner
# -----------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline():
    scripts = [
        "python script1.py",
        "python script2.py",
        "python script3.py"
    ]

    for script in scripts:
        logging.info(f"Running script: {script}")
        try:
            result = subprocess.run(script, shell=True, check=True, capture_output=True, text=True)
            logging.info(f"Script '{script}' completed successfully.")
            logging.info(f"Stdout:\n{result.stdout}")
            if result.stderr:
                logging.warning(f"Stderr:\n{result.stderr}")
        except Exception as e:
            logging.error(f"Error running script '{script}': {e}")
            return False

    logging.info("Pipeline completed successfully.")
    return True

# -----------------------------
# Database Health Checker
# -----------------------------

def check_database_for_problems(db_path="your_database.db"):
    report = {
        "missing_fields": defaultdict(list),
        "duplicate_entries": defaultdict(list),
        "implausible_prices": defaultdict(list),
    }

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check table structure
        try:
            cursor.execute("PRAGMA table_info(products);")
            columns = [col[1] for col in cursor.fetchall()]
            if 'name' not in columns:
                report["missing_fields"]["products"].append("The 'name' field is missing.")
            if 'price' not in columns:
                report["missing_fields"]["products"].append("The 'price' field is missing.")
        except sqlite3.OperationalError:
            report["missing_fields"]["products"].append("The 'products' table does not exist.")

        # Check duplicates
        try:
            cursor.execute("SELECT name, COUNT(*) FROM products GROUP BY name HAVING COUNT(*) > 1;")
            duplicates = cursor.fetchall()
            for name, count in duplicates:
                report["duplicate_entries"]["products"].append(
                    f"Product '{name}' has {count} duplicates."
                )
        except sqlite3.OperationalError:
            pass

        # Check implausible prices
        try:
            cursor.execute("SELECT rowid, name, price FROM products WHERE price < 0 OR price > 1000000;")
            implausible_prices = cursor.fetchall()
            for rowid, name, price in implausible_prices:
                report["implausible_prices"]["products"].append(
                    f"Product '{name}' (ID: {rowid}) has an implausible price: {price}."
                )
        except sqlite3.OperationalError:
            pass

        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return

    print("\n--- Database Health Report ---")
    has_issues = False

    for category, issues in report.items():
        if issues:
            has_issues = True
            print(f"\n[{category.replace('_', ' ').title()}]")
            for table, msgs in issues.items():
                print(f"  Table '{table}':")
                for msg in msgs:
                    print(f"    - {msg}")

    if not has_issues:
        print("No issues found.")

    print("\n--- End of Report ---")

# -----------------------------
# Demo Database Creation
# -----------------------------

if __name__ == "__main__":
    create_and_populate_database()
    run_pipeline()

    db_file = "your_database.db"

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS products;")
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                stock INTEGER
            );
        """)

        cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Laptop', 1200.00, 10);")
        cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Keyboard', 75.50, 50);")
        cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Mouse', 25.00, 100);")
        cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Laptop', 1150.00, 5);")  # Duplicate
        cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Monitor', -50.00, 20);")  # Implausible
        cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Webcam', 1500000.00, 15);")  # Implausible

        conn.commit()
        conn.close()

        print(f"Dummy database '{db_file}' created for demonstration.")

    except sqlite3.Error as e:
        print(f"Error creating dummy database: {e}")

    check_database_for_problems(db_path=db_file)
