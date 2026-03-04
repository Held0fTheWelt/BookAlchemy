"""
Run once to create database tables (authors, books).
Adds missing columns (e.g. rating) if the database already existed.
Run from project root: python -m data.create_tables
"""
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app import app, db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        try:
            with db.engine.begin() as conn:
                conn.execute(text("ALTER TABLE books ADD COLUMN rating INTEGER"))
            print("Column 'rating' added.")
        except OperationalError as err:
            if "duplicate column name" not in str(err).lower():
                print("Note (rating):", err)
    print("Tables created.")
