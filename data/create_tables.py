"""
Run once to create database tables (authors, books).
Adds missing columns (e.g. rating) if the database already existed.
Run from project root: python data/create_tables.py
"""
import sys
from pathlib import Path

# Add project root for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app import app, db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Add "rating" column if table already existed
        try:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE books ADD COLUMN rating INTEGER"))
            print("Column 'rating' added.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                pass
            else:
                print("Note (rating):", e)
    print("Tables created.")
