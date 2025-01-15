import os
import qrcode
from PIL import Image
import sqlite3
import streamlit as st
import pandas as pd

# Setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, "calculator_management.db")
BARCODE_DIR = os.path.join(SCRIPT_DIR, "barcodes")
os.makedirs(BARCODE_DIR, exist_ok=True)

# Database
@st.cache_resource
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        calculator_id TEXT PRIMARY KEY,
        student_name TEXT
    )
    """)
    conn.commit()
    return conn

conn = init_db()

def main():
    st.title("Calculator Management System")
    
    # Calculator IDs
    calculator_ids = [
        "A1", "A2", "A3", "A4", "A5", "A6",
        "B1", "B2", "B3", "B4", "B5", "B6",
        "C1", "C2", "C3", "C4", "C5", "C6",
        "D1", "D2", "D3", "D4", "D5", "D6"
    ]

    # Sidebar for actions
    action = st.sidebar.selectbox(
        "Select Action",
        ["Borrow Calculator", "Return Calculator", "View Inventory", "Clear End of Day"]
    )

    if action == "Borrow Calculator":
        calculator_id = st.selectbox("Select Calculator", calculator_ids)
        student_name = st.text_input("Student Name")
        if st.button("Borrow"):
            cursor = conn.cursor()
            cursor.execute("SELECT student_name FROM assignments WHERE calculator_id = ?", (calculator_id,))
            if cursor.fetchone():
                st.error(f"Calculator {calculator_id} is currently borrowed.")
            else:
                cursor.execute("INSERT INTO assignments VALUES (?, ?)", (calculator_id, student_name))
                conn.commit()
                st.success(f"Calculator {calculator_id} borrowed by {student_name}")

    elif action == "Return Calculator":
        calculator_id = st.selectbox("Select Calculator to Return", calculator_ids)
        if st.button("Return"):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM assignments WHERE calculator_id = ?", (calculator_id,))
            conn.commit()
            st.success(f"Calculator {calculator_id} returned")

    elif action == "View Inventory":
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assignments")
        data = cursor.fetchall()
        if data:
            df = pd.DataFrame(data, columns=["Calculator ID", "Student Name"])
            st.dataframe(df)
        else:
            st.info("No calculators currently borrowed")

    elif action == "Clear End of Day":
        if st.button("Clear All Assignments"):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM assignments")
            conn.commit()
            st.success("All assignments cleared")

if __name__ == "__main__":
    main()
