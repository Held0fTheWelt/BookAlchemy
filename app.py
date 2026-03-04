import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

from data.data_models import db, Author, Book

app = Flask(__name__, template_folder="template")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/library.sqlite')}"
app.config["SECRET_KEY"] = "change-me-in-production"
db.init_app(app)


def get_ai_recommendation(library_text):
    """
    Call an AI API to get book recommendations. Uses OPENAI_API_KEY by default.
    For a free tier with a hard limit, you can use OpenAI's free credits or
    a RapidAPI ChatGPT API (set OPENAI_API_KEY and optionally OPENAI_BASE_URL).
    Returns (recommendation_text, error_message). One of them is None.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not api_key.strip():
        return None, "No API key set. Set OPENAI_API_KEY in your environment (e.g. from OpenAI or a RapidAPI ChatGPT API)."

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key.strip())
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly book recommender. Reply with 3–5 book suggestions only, with a short reason for each. Use clear formatting (e.g. bullet points or numbered list). Do not repeat books from the user's list.",
                },
                {
                    "role": "user",
                    "content": "Based on the following books in my library (and my ratings when given), suggest 3–5 books I might enjoy.\n\n" + library_text,
                },
            ],
            max_tokens=500,
        )
        choice = response.choices[0]
        if choice.message and choice.message.content:
            return choice.message.content.strip(), None
        return None, "Empty response from API."
    except ImportError:
        return None, "Install the openai package: pip install openai"
    except Exception as e:
        return None, str(e)


def parse_date(value):
    """Convert form string (YYYY-MM-DD) to date or None."""
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
            flash("Please enter a name.", "error")
            return render_template("add_author.html")
        author = Author(
            name=name,
            birth_date=parse_date(request.form.get("birthdate")),
            date_of_death=parse_date(request.form.get("date_of_death")),
        )
        db.session.add(author)
        db.session.commit()
        flash("Author was added successfully.", "success")
        return redirect(url_for("add_author"))
    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author_id = request.form.get("author_id", type=int)
        if not title:
            flash("Please enter a book title.", "error")
            return render_template("add_book.html", authors=Author.query.order_by(Author.name).all())
        if not author_id or not Author.query.get(author_id):
            flash("Please select a valid author.", "error")
            return render_template("add_book.html", authors=Author.query.order_by(Author.name).all())
        isbn = request.form.get("isbn", "").strip() or None
        pub_year = request.form.get("publication_year", type=int) or None
        rating = request.form.get("rating", type=int) or None
        if rating is not None and (rating < 1 or rating > 10):
            rating = None
        book = Book(
            title=title,
            isbn=isbn,
            publication_year=pub_year,
            rating=rating,
            author_id=author_id,
        )
        db.session.add(book)
        db.session.commit()
        flash("Book was added successfully.", "success")
        return redirect(url_for("add_book"))
    return render_template("add_book.html", authors=Author.query.order_by(Author.name).all())


@app.route("/")
def index():
    # #region agent log
    _debug_log("index_request_received", {"path": "/"}, "H1")
    # #endregion
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


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template("book_detail.html", book=book)


@app.route("/author/<int:author_id>")
def author_detail(author_id):
    author = Author.query.get_or_404(author_id)
    books = author.books.order_by(Book.title).all()
    return render_template("author_detail.html", author=author, books=books)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author
    author_book_count = Book.query.filter_by(author_id=author.id).count()
    db.session.delete(book)
    if author_book_count == 1:
        db.session.delete(author)
    db.session.commit()
    flash("Book was deleted successfully.", "success")
    return redirect(url_for("index"))


@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    flash("Author and all associated books were deleted successfully.", "success")
    return redirect(url_for("index"))


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    recommendation = None
    error = None
    if request.method == "POST" or request.args.get("generate"):
        books = Book.query.join(Author).order_by(Author.name, Book.title).all()
        if not books:
            error = "Add some books to your library first."
        else:
            lines = []
            for b in books:
                if b.rating is not None:
                    lines.append(f"- {b.title} by {b.author.name} (rated {b.rating}/10)")
                else:
                    lines.append(f"- {b.title} by {b.author.name}")
            library_text = "\n".join(lines)
            recommendation, error = get_ai_recommendation(library_text)
    return render_template("recommend.html", recommendation=recommendation, error=error)


@app.route("/book/<int:book_id>/rate", methods=["POST"])
def rate_book(book_id):
    book = Book.query.get_or_404(book_id)
    rating = request.form.get("rating", type=int)
    if rating is not None and 1 <= rating <= 10:
        book.rating = rating
    elif request.form.get("rating") == "":
        book.rating = None
    else:
        return redirect(request.referrer or url_for("index"))
    db.session.commit()
    flash("Rating was saved.", "success")
    return redirect(request.referrer or url_for("index"))


# #region agent log
def _debug_log(message, data=None, hypothesis_id="H1"):
    try:
        import json
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug-e810f4.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"sessionId": "e810f4", "message": message, "data": data or {}, "hypothesisId": hypothesis_id, "timestamp": datetime.now().isoformat()}) + "\n")
    except Exception:
        pass
# #endregion

if __name__ == "__main__":
    _debug_log("app_run_start", {"host": "0.0.0.0", "port": 5002}, "H2")
    # Listen on all interfaces so Codio's proxy can reach the app (avoids 502)
    app.run(debug=True, host="0.0.0.0", port=5002)
