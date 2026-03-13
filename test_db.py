import firebase_admin
from firebase_admin import credentials, firestore
import os

def test_connection():
    config_path = "firebase_config.json"
    if not os.path.exists(config_path):
        print("Config file not found.")
        return

    try:
        cred = credentials.Certificate(config_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        
        print("Attempting to write to 'test_collection'...")
        db.collection('test_collection').document('test_doc').set({'status': 'working'})
        print("Success! Firestore is working.")
        
    except Exception as e:
        print("\n--- ERROR DETECTED ---")
        print(e)
        print("----------------------\n")

if __name__ == "__main__":
    test_connection()
