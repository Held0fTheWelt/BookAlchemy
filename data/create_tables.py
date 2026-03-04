"""
Einmalig ausführen, um die Datenbanktabellen (authors, books) anzulegen.
Ausführung: python data/create_tables.py  (vom Projektroot)
"""
import sys
from pathlib import Path

# Projektroot für Imports hinzufügen
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app, db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("Tabellen wurden angelegt.")
