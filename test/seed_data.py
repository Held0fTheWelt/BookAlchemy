"""
Seed-Script: Legt Autoren und Bücher in der Datenbank an.
Ausführung vom Projektroot: python test/seed_data.py
"""
import sys
from pathlib import Path
from datetime import date

# Projektroot für Imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app, db
from data_models import Author, Book


AUTHORS = [
    {"name": "Jane Austen", "birth_date": date(1775, 12, 16), "date_of_death": date(1817, 7, 18)},
    {"name": "George Orwell", "birth_date": date(1903, 6, 25), "date_of_death": date(1950, 1, 21)},
    {"name": "Agatha Christie", "birth_date": date(1890, 9, 15), "date_of_death": date(1976, 1, 12)},
    {"name": "Stephen King", "birth_date": date(1947, 9, 21), "date_of_death": None},
    {"name": "Haruki Murakami", "birth_date": date(1949, 1, 12), "date_of_death": None},
    {"name": "Ursula K. Le Guin", "birth_date": date(1929, 10, 21), "date_of_death": date(2018, 1, 22)},
    {"name": "Terry Pratchett", "birth_date": date(1948, 4, 28), "date_of_death": date(2015, 3, 12)},
]

BOOKS = [
    {"title": "Pride and Prejudice", "isbn": "9780141439518", "publication_year": 1813, "author_index": 0},
    {"title": "1984", "isbn": "9780451524935", "publication_year": 1949, "author_index": 1},
    {"title": "Animal Farm", "isbn": "9780451526342", "publication_year": 1945, "author_index": 1},
    {"title": "Murder on the Orient Express", "isbn": "9780062693662", "publication_year": 1934, "author_index": 2},
    {"title": "The Shining", "isbn": "9780307743657", "publication_year": 1977, "author_index": 3},
    {"title": "Norwegian Wood", "isbn": "9780375704024", "publication_year": 1987, "author_index": 4},
    {"title": "Kafka on the Shore", "isbn": "9781400079278", "publication_year": 2002, "author_index": 4},
    {"title": "The Left Hand of Darkness", "isbn": "9780441478125", "publication_year": 1969, "author_index": 5},
    {"title": "Guards! Guards!", "isbn": "9780062225752", "publication_year": 1989, "author_index": 6},
    {"title": "Good Omens", "isbn": "9780060853983", "publication_year": 1990, "author_index": 6},
]


def seed():
    with app.app_context():
        if Author.query.first():
            print("Datenbank enthält bereits Daten. Keine Seed-Daten eingefügt.")
            return
        authors = []
        for a in AUTHORS:
            author = Author(**a)
            db.session.add(author)
            db.session.flush()
            authors.append(author)
        for b in BOOKS:
            book = Book(
                title=b["title"],
                isbn=b["isbn"],
                publication_year=b["publication_year"],
                author_id=authors[b["author_index"]].id,
            )
            db.session.add(book)
        db.session.commit()
        print(f"{len(authors)} Autoren und {len(BOOKS)} Bücher wurden angelegt.")


if __name__ == "__main__":
    seed()
