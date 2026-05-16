import sqlite3
import random
import time
from datetime import datetime

DB_PATH = "database/shop_floor.db"

# Realistic ranges per machine
MACHINE_PROFILES = {
    1: {"normal_units": (8, 12), "normal_defects": (0, 1)},   # CNC — stable
    2: {"normal_units": (9, 13), "normal_defects": (0, 1)},   # Assembly — stable
    3: {"normal_units": (6, 9),  "normal_defects": (1, 3)},   # Welding — degrading
    4: {"normal_units": (10, 12),"normal_defects": (0, 0)},   # Scanner — very stable
    5: {"normal_units": (8, 11), "normal_defects": (0, 1)},   # Packaging — stable
}

def insert_reading(machine_id, shift_id, units, defects):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO production 
        (machine_id, shift_id, units_produced, defective_units, shift_date)
        VALUES (?, ?, ?, ?, ?)
    """, (machine_id, shift_id, units, defects, 
          datetime.now().date().isoformat()))
    conn.commit()
    conn.close()

print("Simulator started — inserting readings every 30 seconds")
print("Press Ctrl+C to stop\n")

cycle = 0
while True:
    cycle += 1
    print(f"Cycle {cycle} — {datetime.now().strftime('%H:%M:%S')}")
    
    for machine_id, profile in MACHINE_PROFILES.items():
        if random.random() < 0.3:  # 30% chance any machine has bad cycle
            units = random.randint(1, 8)
            defects = random.randint(2, 5)
        else:
            units = random.randint(*profile["normal_units"])
            defects = random.randint(*profile["normal_defects"])
        
        insert_reading(machine_id, 1, units, defects)
        print(f"  Machine {machine_id}: {units} units, {defects} defects")
        
    print()
    time.sleep(30)