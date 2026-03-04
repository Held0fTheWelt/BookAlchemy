import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from data_models import db, Author, Book

app = Flask(__name__, template_folder="template")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/library.sqlite')}"
app.config["SECRET_KEY"] = "change-me-in-production"
db.init_app(app)


def parse_date(value):
    """Form-String (YYYY-MM-DD) in date oder None umwandeln."""
    if not value or not value.strip():
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Bitte einen Namen angeben.", "error")
            return render_template("add_author.html")
        author = Author(
            name=name,
            birth_date=parse_date(request.form.get("birthdate")),
            date_of_death=parse_date(request.form.get("date_of_death")),
        )
        db.session.add(author)
        db.session.commit()
        flash("Autor wurde erfolgreich hinzugefügt.", "success")
        return redirect(url_for("add_author"))
    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author_id = request.form.get("author_id", type=int)
        if not title:
            flash("Bitte einen Buchtitel angeben.", "error")
            return render_template("add_book.html", authors=Author.query.order_by(Author.name).all())
        if not author_id or not Author.query.get(author_id):
            flash("Bitte einen gültigen Autor auswählen.", "error")
            return render_template("add_book.html", authors=Author.query.order_by(Author.name).all())
        isbn = request.form.get("isbn", "").strip() or None
        pub_year = request.form.get("publication_year", type=int) or None
        book = Book(
            title=title,
            isbn=isbn,
            publication_year=pub_year,
            author_id=author_id,
        )
        db.session.add(book)
        db.session.commit()
        flash("Buch wurde erfolgreich hinzugefügt.", "success")
        return redirect(url_for("add_book"))
    return render_template("add_book.html", authors=Author.query.order_by(Author.name).all())


@app.route("/")
def index():
    sort = request.args.get("sort", "title")
    search_query = request.args.get("q", "").strip()

    query = Book.query.join(Author)
    if search_query:
        pattern = f"%{search_query}%"
        query = query.filter(
            db.or_(Book.title.ilike(pattern), Author.name.ilike(pattern))
        )
    if sort == "author":
        books = query.order_by(Author.name, Book.title).all()
    else:
        books = query.order_by(Book.title).all()

    return render_template(
        "home.html", books=books, sort=sort, search_query=search_query
    )


if __name__ == "__main__":
    app.run(debug=True)
