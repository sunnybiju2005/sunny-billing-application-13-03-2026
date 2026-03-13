import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import sys
from datetime import datetime

class Database:
    def __init__(self, config_filename="firebase_config.json"):
        self.db = None
        self.connected = False
        
        # Determine the base path (works for both script and .exe)
        if getattr(sys, 'frozen', False):
            # If running as .exe, look in the same folder as the .exe
            base_dir = os.path.dirname(sys.executable)
        else:
            # If running as .py script, look in the current folder
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.config_path = os.path.join(base_dir, config_filename)
        self.connect()

    def connect(self):
        try:
            if not os.path.exists(self.config_path):
                print(f"Config file {self.config_path} not found.")
                return False
            
            # Check if already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.config_path)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.connected = True
            return True
        except Exception as e:
            print(f"Error connecting to Firebase: {e}")
            self.connected = False
            return False

    def is_connected(self):
        try:
            # Simple check to see if we can reach firestore
            if self.db:
                # We don't want to make a network call every time, 
                # but we can try a light ping if needed.
                return True
            return False
        except:
            return False

    # --- Clothes Methods ---
    def add_cloth(self, name, category, price):
        if not self.db: return False, "Database not initialized"
        try:
            # Using name as ID as per requirement ("this also serves as the Cloth ID/code for staff search")
            doc_ref = self.db.collection('clothes').document(name)
            doc_ref.set({
                'name': name,
                'category': category,
                'price': float(price)
            })
            return True, "Success"
        except Exception as e:
            error_msg = str(e)
            print(f"Error adding cloth: {error_msg}")
            return False, error_msg

    def get_all_clothes(self):
        if not self.db: return []
        try:
            clothes = self.db.collection('clothes').stream()
            return [doc.to_dict() for doc in clothes]
        except Exception as e:
            print(f"Error getting clothes: {e}")
            return []

    def delete_cloth(self, cloth_id):
        if not self.db: return False
        try:
            self.db.collection('clothes').document(cloth_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting cloth: {e}")
            return False

    # --- Bills Methods ---
    def save_bill(self, bill_data):
        if not self.db: return False, "Database not initialized"
        try:
            # bill_data should contain items, total, payment_method, etc.
            bill_data['timestamp'] = firestore.SERVER_TIMESTAMP
            doc_ref = self.db.collection('bills').document()
            doc_ref.set(bill_data)
            return True, doc_ref.id
        except Exception as e:
            error_msg = str(e)
            print(f"Error saving bill: {error_msg}")
            return False, error_msg

    def get_bills(self, date=None, payment_method=None):
        if not self.db: return []
        try:
            query = self.db.collection('bills')
            
            if date:
                # Firestore date filtering can be tricky with SERVER_TIMESTAMP.
                # Usually we search for the full day range.
                start_of_day = datetime.combine(date, datetime.min.time())
                end_of_day = datetime.combine(date, datetime.max.time())
                query = query.where('timestamp', '>=', start_of_day).where('timestamp', '<=', end_of_day)
            
            if payment_method and payment_method != "All":
                query = query.where('payment_method', '==', payment_method.lower())
                
            bills = query.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
            return [{"id": doc.id, **doc.to_dict()} for doc in bills]
        except Exception as e:
            print(f"Error getting bills: {e}")
            return []

    def get_today_stats(self):
        if not self.db: return 0, 0
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
        if not self.db: return False, "Database not initialized"
        try:
            self.db.collection('bills').document(bill_id).delete()
            return True, "Bill deleted"
        except Exception as e:
            return False, str(e)

    def delete_all_bills(self):
        if not self.db: return False, "Database not initialized"
        try:
            batch = self.db.batch()
            bills = self.db.collection('bills').stream()
            for doc in bills:
                batch.delete(doc.reference)
            batch.commit()
            return True, "All bills deleted"
        except Exception as e:
            return False, str(e)
