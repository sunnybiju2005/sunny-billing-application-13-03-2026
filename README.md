# DROP | Premium Billing Application

A modern, minimalist desktop billing application for clothing shops, built with Python, CustomTkinter, and Firebase Firestore.

## Features
- **Modern UI**: Dark-themed, fashion-forward interface matching the brand "DROP".
- **Staff Panel**: Product search by ID, dropdown selection, manual entry, and dynamic cart management.
- **Admin Panel**: Dashboard with daily stats, bill management system, and inventory control.
- **Firebase Sync**: Real-time connection to Firestore for cloud data persistence.
- **PDF Invoicing**: Generate professional receipts using ReportLab.
- **Secure Deletion**: Password-protected bill deletion ("ArJuN").

## Prerequisites
- Python 3.8 or higher.
- A Firebase project with Firestore enabled.

## Setup Instructions

1. **Install Dependencies**:
   Open your terminal and run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Firebase**:
   - Go to your [Firebase Console](https://console.firebase.google.com/).
   - Navigate to **Project Settings** > **Service Accounts**.
   - Click **Generate New Private Key**.
   - Rename the downloaded JSON file to `firebase_config.json`.
   - Place `firebase_config.json` in the project root directory.

3. **Database Collections**:
   Ensure you have (or the app will create) the following collections:
   - `clothes`: For inventory management.
   - `bills`: For storing transaction history.

4. **Run the Application**:
   ```bash
   python main.py
   ```

## Admin Panel Password
The default password for sensitive actions (deleting bills) is: `ArJuN`

## Tech Stack
- **UI**: CustomTkinter
- **Database**: Firebase Admin SDK (Firestore)
- **PDF**: ReportLab
- **Table View**: Tkinter Treeview (styled)
"# sunny-billing-application-13-03-2026" 
