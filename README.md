# Work-experience
import yfinance as yf
import sqlite3
import subprocess
import logging
from collections import defaultdict



instruments = [
    {"name": "Apple Inc.", "ticker": "APPL", "currency": "USD", "asset_class": "Equity"},
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

ticker_to_find = input("Enter ticker symbol to lookup: ")
found_instrument = lookup_instrument_by_ticker(ticker_to_find.upper())

if found_instrument:
    print(f"Instrument Found: {found_instrument['name']}")
    print(f"Ticker: {found_instrument['ticker']}")
    print(f"Currency: {found_instrument['currency']}")
    print(f"Asset Class: {found_instrument['asset_class']}")
else:
    print(f"Instrument with ticker '{ticker_to_find}' not found.")


# Define the tickers for the 5 instruments
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

# Fetch recent price data
data = yf.download(tickers, period="1mo", interval="1d")

# Extract the 'Close' prices
close_prices = data['Close']

# Save the data to a CSV file
close_prices.to_csv("recent_prices.csv")

print("Recent price data saved to recent_prices.csv")

# Display the first few rows of the data
print(close_prices.head())




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


    
    
cursor.execute("SELECT task_id FROM tasks WHERE task_name IN ('Plan Project Structure', 'Set up Development Environment') ORDER BY task_id")
    task_ids_day2 = [row[0] for row in cursor.fetchall()]

subtasks_day2_with_ids = []
    for i, task_id in enumerate(task_ids_day2):
        if i == 0: # Plan Project Structure
            subtasks_day2_with_ids.append((task_id, 'Create project directory', False))
            subtasks_day2_with_ids.append((task_id, 'Define database schema', False))
        elif i == 1: # Set up Development Environment
            subtasks_day2_with_ids.append((task_id, 'Install Python', False))
            subtasks_day2_with_ids.append((task_id, 'Install VS Code', False))
            subtasks_day2_with_ids.append((task_id, 'Install Monaco Editor integration', False))
    cursor.executemany('INSERT INTO subtasks (task_id, subtask_name, completed) VALUES (?, ?, ?)', subtasks_day2_with_ids)
    conn.commit()


    
tasks_day3 = [
        ('Implement Task Management API', 'Create endpoints for CRUD operations on tasks.', '2023-10-27'),
        ('Develop User Interface', 'Build the frontend using HTML, CSS, and JavaScript.', '2023-10-27')
    ]
   
cursor.executemany('INSERT INTO tasks (task_name, description, due_date) VALUES (?, ?, ?)', tasks_day3)
    conn.commit()

cursor.execute("SELECT task_id FROM tasks WHERE task_name IN ('Implement Task Management API', 'Develop User Interface') ORDER BY task_id")
    task_ids_day3 = [row[0] for row in cursor.fetchall()]

subtasks_day3_with_ids = []
    for i, task_id in enumerate(task_ids_day3):
        if i == 0: # Implement Task Management API
            subtasks_day3_with_ids.append((task_id, 'Design API endpoints', False))
            subtasks_day3_with_ids.append((task_id, 'Write Python backend code', False))
        elif i == 1: # Develop User Interface
            subtasks_day3_with_ids.append((task_id, 'Create HTML structure', False))
            subtasks_day3_with_ids.append((task_id, 'Style with CSS', False))
            subtasks_day3_with_ids.append((task_id, 'Add JavaScript interactivity', False))

cursor.executemany('INSERT INTO subtasks (task_id, subtask_name, completed) VALUES (?, ?, ?)', subtasks_day3_with_ids)
    conn.commit()

conn.close()

if __name__ == '__main__':
    create_and_populate_database()

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
        except subprocess.CalledProcessError as e:
            logging.error(f"Script '{script}' failed with exit code {e.returncode}.")
            logging.error(f"Stderr:\n{e.stderr}")
            return False
        except FileNotFoundError:
            logging.error(f"Script '{script}' not found. Please ensure it exists.")
            return False
        except Exception as e:
            logging.error(f"An unexpected error occurred while running '{script}': {e}")
            return False
    logging.info("Pipeline completed successfully.")
    return True

if __name__ == "__main__":
    run_pipeline()


def check_database_for_problems(db_path="your_database.db"):
    """
    Checks a SQLite database for common problems: missing fields, duplicate entries,
    and implausible prices.

Args:
        db_path (str): The path to the SQLite database file.
    """
    report = {
        "missing_fields": defaultdict(list),
        "duplicate_entries": defaultdict(list),
        "implausible_prices": defaultdict(list),
    }

 try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

      
  try:
        cursor.execute("PRAGMA table_info(products);")
        columns = [col[1] for col in cursor.fetchall()]
        if 'name' not in columns:
            report["missing_fields"]["products"].append("The 'name' field is missing.")
            if 'price' not in columns:
                report["missing_fields"]["products"].append("The 'price' field is missing.")
        except sqlite3.OperationalError:
            report["missing_fields"]["products"].append("The 'products' table does not exist.")

        
try:
            cursor.execute("SELECT name, COUNT(*) FROM products GROUP BY name HAVING COUNT(*) > 1;")
            duplicates = cursor.fetchall()
            for name, count in duplicates:
                report["duplicate_entries"]["products"].append(f"Product '{name}' has {count} duplicates.")
        except sqlite3.OperationalError:
            pass # Table might not exist or 'name' column might be missing

      
  try:
            cursor.execute("SELECT rowid, name, price FROM products WHERE price < 0 OR price > 1000000;")
            implausible_prices = cursor.fetchall()
            for rowid, name, price in implausible_prices:
                report["implausible_prices"]["products"].append(f"Product '{name}' (ID: {rowid}) has an implausible price: {price}.")
        except sqlite3.OperationalError:
            pass # Table might not exist or 'price' column might be missing
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return

 print("--- Database Health Report ---")
    has_issues = False
    if report["missing_fields"]:
        has_issues = True
        print("\n[Missing Fields]")
        for table, issues in report["missing_fields"].items():
            print(f"  Table '{table}':")
            for issue in issues:
                print(f"    - {issue}")
    if report["duplicate_entries"]:
        has_issues = True
        print("\n[Duplicate Entries]")
        for table, issues in report["duplicate_entries"].items():
            print(f"  Table '{table}':")
            for issue in issues:
                print(f"    - {issue}")
    if report["implausible_prices"]:
        has_issues = True
        print("\n[Implausible Prices]")
        for table, issues in report["implausible_prices"].items():
            print(f"  Table '{table}':")
            for issue in issues:
                print(f"    - {issue}")
    if not has_issues:
        print("\nNo issues found.")
    print("\n--- End of Report ---")

if __name__ == "__main__":
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
        cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Laptop', 1150.00, 5);") # Duplicate name
        cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Monitor', -50.00, 20);") # Implausible price
        cursor.execute("INSERT INTO products (name, price, stock) VALUES ('Webcam', 1500000.00, 15);") # Implausible price
        conn.commit()
        conn.close()
        print(f"Dummy database '{db_file}' created for demonstration.")
    except sqlite3.Error as e:
        print(f"Error creating dummy database: {e}")

check_database_for_problems(db_path=db_file)




