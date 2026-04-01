import firebase_admin
from firebase_admin import credentials, firestore
import sqlite3
import os
import sys

def migrate():
    # Setup Firebase
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "firebase_config.json")
    
    if not os.path.exists(config_path):
        print("No firebase config found!")
        return

    cred = credentials.Certificate(config_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    print("Connected to Firebase.")

    # Setup SQLite
    db_path = os.path.join(base_dir, "local_billing.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clothes (
        id TEXT PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bills (
        id TEXT PRIMARY KEY,
        timestamp TEXT,
        total REAL,
        payment_method TEXT,
        cash_amount REAL,
        upi_amount REAL,
        items TEXT
    )
    ''')
    conn.commit()

    print("Created tables. Fetching clothes...")
    # Fetch and insert clothes
    clothes = db.collection('clothes').stream()
    for doc in clothes:
        data = doc.to_dict()
        cursor.execute('''
        INSERT OR IGNORE INTO clothes (id, name, category, price) 
        VALUES (?, ?, ?, ?)
        ''', (doc.id, data.get('name', ''), data.get('category', ''), float(data.get('price', 0))))
    conn.commit()

    print("Fetching bills...")
    # Fetch and insert bills
    import json
    bills = db.collection('bills').stream()
    for doc in bills:
        data = doc.to_dict()
        
        # handle timestamp from firestore
        ts = data.get('timestamp')
        ts_str = ""
        if ts:
            if hasattr(ts, 'strftime'):
                ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
            else:
                ts_str = str(ts)
        
        items_str = json.dumps(data.get('items', []))
        
        cursor.execute('''
        INSERT OR IGNORE INTO bills (id, timestamp, total, payment_method, cash_amount, upi_amount, items)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (doc.id, ts_str, float(data.get('total', 0)), data.get('payment_method', ''), 
              float(data.get('cash_amount', 0)), float(data.get('upi_amount', 0)), items_str))
    conn.commit()
    conn.close()

    print("Migration complete!")

if __name__ == "__main__":
    migrate()
