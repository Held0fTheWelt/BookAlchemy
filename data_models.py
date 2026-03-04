from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<Author(id={self.id}, name={repr(self.name)})>"

    def __str__(self):
        return self.name or f"Author #{self.id}"


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), unique=True, nullable=True)
    title = db.Column(db.String(500), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    author = db.relationship(
        "Author",
        backref=db.backref("books", lazy="dynamic", cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<Book(id={self.id}, title={repr(self.title)})>"

    def __str__(self):
        return self.title or f"Book #{self.id}"
