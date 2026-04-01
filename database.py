import sqlite3
import json
import os
import sys
from datetime import datetime
import uuid

class Database:
    def __init__(self, config_filename="local_billing.db"):
        self.db = None
        self.connected = False
        
        # Determine the base path (works for both script and .exe)
        if getattr(sys, 'frozen', False):
            # If running as .exe, look in the same folder as the .exe
            base_dir = os.path.dirname(sys.executable)
        else:
            # If running as .py script, look in the current folder
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.db_path = os.path.join(base_dir, config_filename)
        self.connect()

    def connect(self):
        try:
            self.db = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.db.cursor()
            
            # Create tables if not exist
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clothes (
                id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                price REAL
            )
            ''')

            self.cursor.execute('''
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
            self.db.commit()
            
            self.connected = True
            return True
        except Exception as e:
            print(f"Error connecting to SQLite Database: {e}")
            self.connected = False
            return False

    def is_connected(self):
        return self.connected

    # --- Clothes Methods ---
    def add_cloth(self, name, category, price):
        if not self.connected: return False, "Database not initialized"
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO clothes (id, name, category, price) 
            VALUES (?, ?, ?, ?)
            ''', (name, name, category, float(price)))
            self.db.commit()
            return True, "Success"
        except Exception as e:
            error_msg = str(e)
            print(f"Error adding cloth: {error_msg}")
            return False, error_msg

    def get_all_clothes(self):
        if not self.connected: return []
        try:
            self.cursor.execute("SELECT name, category, price FROM clothes")
            rows = self.cursor.fetchall()
            return [{'name': row[0], 'category': row[1], 'price': row[2]} for row in rows]
        except Exception as e:
            print(f"Error getting clothes: {e}")
            return []

    def delete_cloth(self, cloth_id):
        if not self.connected: return False
        try:
            self.cursor.execute("DELETE FROM clothes WHERE id=?", (cloth_id,))
            self.db.commit()
            return True
        except Exception as e:
            print(f"Error deleting cloth: {e}")
            return False

    # --- Bills Methods ---
    def save_bill(self, bill_data):
        if not self.connected: return False, "Database not initialized"
        try:
            doc_id = str(uuid.uuid4())
            ts = datetime.now()
            ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')
            
            items_str = json.dumps(bill_data.get('items', []))
            
            self.cursor.execute('''
            INSERT INTO bills (id, timestamp, total, payment_method, cash_amount, upi_amount, items)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (doc_id, ts_str, float(bill_data.get('total', 0)), 
                  bill_data.get('payment_method', ''), float(bill_data.get('cash_amount', 0)), 
                  float(bill_data.get('upi_amount', 0)), items_str))
            
            self.db.commit()
            return True, doc_id
        except Exception as e:
            error_msg = str(e)
            print(f"Error saving bill: {error_msg}")
            return False, error_msg

    def get_bills(self, date=None, payment_method=None):
        if not self.connected: return []
        try:
            query = "SELECT id, timestamp, total, payment_method, cash_amount, upi_amount, items FROM bills WHERE 1=1"
            params = []
            
            if date:
                # SQLite dates as strings YYYY-MM-DD
                date_str = date.strftime('%Y-%m-%d')
                query += " AND timestamp LIKE ?"
                params.append(f"{date_str}%")
            
            if payment_method and payment_method != "All":
                query += " AND payment_method = ?"
                params.append(payment_method.lower())
                
            query += " ORDER BY timestamp DESC"
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            bills = []
            for row in rows:
                ts_obj = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') if row[1] else datetime.now()
                items = json.loads(row[6]) if row[6] else []
                bills.append({
                    'id': row[0],
                    'timestamp': ts_obj,
                    'total': row[2],
                    'payment_method': row[3],
                    'cash_amount': row[4],
                    'upi_amount': row[5],
                    'items': items
                })
            return bills
        except Exception as e:
            print(f"Error getting bills: {e}")
            return []

    def get_today_stats(self):
        if not self.connected: return 0, 0
        try:
            today = datetime.now().date()
            bills = self.get_bills(date=today)
            total_sales = sum(bill.get('total', 0) for bill in bills)
            num_bills = len(bills)
            return total_sales, num_bills
        except Exception as e:
            print(f"Error getting today's stats: {e}")
            return 0, 0

    def delete_bill(self, bill_id):
        if not self.connected: return False, "Database not initialized"
        try:
            self.cursor.execute("DELETE FROM bills WHERE id=?", (bill_id,))
            self.db.commit()
            return True, "Bill deleted"
        except Exception as e:
            return False, str(e)

    def delete_all_bills(self):
        if not self.connected: return False, "Database not initialized"
        try:
            self.cursor.execute("DELETE FROM bills")
            self.db.commit()
            return True, "All bills deleted"
        except Exception as e:
            return False, str(e)
