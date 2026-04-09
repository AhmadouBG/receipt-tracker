import sqlite3
from .config import DB_NAME
from datetime import datetime

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                id TEXT PRIMARY KEY,
                filename TEXT,
                status TEXT DEFAULT 'uploaded',
                datetime TEXT,
                company TEXT,
                date TEXT,
                total REAL,
                address TEXT,
                confidence REAL
            )
        """)


def save_receipt_record(receipt_id: str, filename: str, ocr_result: dict = None):
    if ocr_result:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                """INSERT INTO receipts (id, filename, status, datetime, company, date, total, address, confidence) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    receipt_id,
                    filename,
                    "parsed",
                    datetime.now(),
                    ocr_result.get("company"),
                    ocr_result.get("date"),
                    ocr_result.get("total"),
                    ocr_result.get("address"),
                    ocr_result.get("confidence"),
                ),
            )
    else:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT INTO receipts (id, filename) VALUES (?, ?)",
                (receipt_id, filename),
            )
