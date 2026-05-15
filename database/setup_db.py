import sqlite3
import os

# Create database folder if not exists
os.makedirs("database", exist_ok=True)

conn = sqlite3.connect("database/shop_floor.db")
cursor = conn.cursor()

# Create all 5 tables
cursor.executescript("""

CREATE TABLE IF NOT EXISTS operators (
    operator_id INTEGER PRIMARY KEY,
    operator_name TEXT NOT NULL,
    experience_years INTEGER
);

CREATE TABLE IF NOT EXISTS shifts (
    shift_id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    shift_type TEXT NOT NULL,
    shift_start_time TEXT,
    shift_end_time TEXT,
    operator_id INTEGER,
    FOREIGN KEY (operator_id) REFERENCES operators(operator_id)
);

CREATE TABLE IF NOT EXISTS machines (
    machine_id INTEGER PRIMARY KEY,
    machine_name TEXT NOT NULL,
    purpose TEXT,
    last_maintenance TEXT,
    manufacturing_date TEXT,
    operator_id INTEGER,
    FOREIGN KEY (operator_id) REFERENCES operators(operator_id)
);

CREATE TABLE IF NOT EXISTS production (
    production_id INTEGER PRIMARY KEY,
    machine_id INTEGER,
    shift_id INTEGER,
    units_produced INTEGER,
    defective_units INTEGER,
    shift_date TEXT,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id),
    FOREIGN KEY (shift_id) REFERENCES shifts(shift_id)
);

CREATE TABLE IF NOT EXISTS issues (
    issue_id INTEGER PRIMARY KEY,
    machine_id INTEGER,
    shift_id INTEGER,
    issue_type TEXT,
    duration_minutes INTEGER,
    is_recurring INTEGER,
    resolved INTEGER,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id),
    FOREIGN KEY (shift_id) REFERENCES shifts(shift_id)
);

""")

conn.commit()
conn.close()
print("Database created successfully ✅")