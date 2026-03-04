# BookAlchemy

Eine kleine digitale Bibliothek mit Flask: Autoren und Bücher verwalten, bewerten und per KI Buch-Empfehlungen abrufen.

## Voraussetzungen

- Python 3.10+
- pip

## Installation

```bash
cd BookAlchemy
pip install -r requirements.txt
```

## Konfiguration

- **Datenbank:** Die SQLite-Datei liegt unter `data/library.sqlite` und wird beim ersten Tabellen-Setup angelegt.
- **KI-Empfehlungen:** In der Projektroot eine `.env` Datei anlegen mit:
  ```
  OPENAI_API_KEY=dein-api-key
  ```
  (Optional; ohne Key funktioniert die App, nur die Seite „Suggest a Book“ meldet einen fehlenden Key.)

## Tabellen anlegen

Einmalig ausführen, um die Tabellen für Autoren und Bücher zu erstellen:

```bash
python data/create_tables.py
```

## Testdaten (optional)

```bash
python test/seed_data.py
```

Legt einige Beispieldaten an (Autoren und Bücher).

## App starten

```bash
python app.py
```

Im Browser: **http://127.0.0.1:5000/**

## Funktionen

- **Startseite:** Bücherliste mit Suche, Sortierung (Titel/Autor), Bewertung (1–10), Cover-Bilder (über ISBN)
- **Autoren/Bücher anlegen:** `/add_author`, `/add_book`
- **Detailseiten:** Klick auf Buchtitel oder Autor
- **Löschen:** Buch oder Autor (inkl. zugehöriger Bücher) löschen
- **Suggest a Book:** KI-Empfehlungen basierend auf deiner Bibliothek und Bewertungen (benötigt `OPENAI_API_KEY`)

## Projektstruktur

- `app.py` – Flask-App und Routen
- `data/data_models.py` – SQLAlchemy-Modelle (Author, Book)
- `data/create_tables.py` – Tabellen anlegen
- `template/` – HTML-Vorlagen
- `test/` – Seed-Skript
