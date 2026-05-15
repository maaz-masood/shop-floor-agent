import sqlite3
import random
from datetime import datetime, date

conn = sqlite3.connect("database/shop_floor.db")
cursor = conn.cursor()

# ── Operators ──
operators = [
    (1, "Ahmed Khan", 8),
    (2, "Maria Lopez", 5),
    (3, "James Smith", 12),
    (4, "Sarah Chen", 3),
]
cursor.executemany(
    "INSERT OR IGNORE INTO operators VALUES (?,?,?)",
    operators
)

# ── Machines ──
machines = [
    (1, "CNC Machine A", "Precision cutting", "2025-03-01", "2020-06-15", 1),
    (2, "Assembly Line B", "Component assembly", "2025-02-15", "2019-11-20", 2),
    (3, "Welding Station C", "Metal welding", "2025-04-10", "2021-03-08", 3),
    (4, "Quality Scanner D", "Defect detection", "2025-01-20", "2022-07-14", 4),
    (5, "Packaging Unit E", "Final packaging", "2025-03-25", "2023-01-30", 1),
]
cursor.executemany(
    "INSERT OR IGNORE INTO machines VALUES (?,?,?,?,?,?)",
    machines
)

# ── Shift ──
today = date.today().isoformat()
cursor.execute(
    "INSERT OR IGNORE INTO shifts VALUES (?,?,?,?,?,?)",
    (1, today, "Morning", "06:00", "14:00", 1)
)

# ── Production ──
# Machine 3 has abnormal defect rate to trigger alert
production = [
    (1, 1, 1, 98,  2, today),   # normal
    (2, 2, 1, 102, 3, today),   # normal
    (3, 3, 1, 87,  9, today),   # abnormal ← high defects
    (4, 4, 1, 100, 1, today),   # normal
    (5, 5, 1, 95,  2, today),   # normal
]
cursor.executemany(
    "INSERT OR IGNORE INTO production VALUES (?,?,?,?,?,?)",
    production
)

# ── Issues ──
issues = [
    (1, 3, 1, "Vibration anomaly", 45, 1, 0),  # recurring, unresolved
    (2, 1, 1, "Minor calibration drift", 15, 0, 1),  # resolved
]
cursor.executemany(
    "INSERT OR IGNORE INTO issues VALUES (?,?,?,?,?,?,?)",
    issues
)

conn.commit()
conn.close()
print("Shift data simulated successfully ✅")