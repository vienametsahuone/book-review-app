import sqlite3
from flask import Flask
import config
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("index.html")

    username = request.form["username"]
    password = request.form["password"]

    result = db.query(
        "SELECT id, password_hash FROM users WHERE username = ?",
        [username]
    )

    if len(result) == 0:
        return render_template("index.html", error="Väärä tunnus tai salasana")

    user = result[0]

    if not check_password_hash(user["password_hash"], password):
        return render_template("index.html", error="Väärä tunnus tai salasana")

    session["user_id"] = user["id"]
    session["username"] = username

    return redirect("/")

    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"].strip()
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    errors = []

    if username and not all(
        char.isascii() and (char.isalnum() or char == "_")
        for char in username
    ):
        errors.append("Tunnuksessa saa olla vain englannin kirjaimia, numeroita ja alaviivoja")

    if not username:
        errors.append("Tunnus ei voi olla tyhjä tai sisältää vain välilyöntejä")

    if not password1.strip():
        errors.append("Salasana ei voi olla tyhjä tai sisältää vain välilyöntejä")

    if len(username) > 25:
        errors.append("Tunnuksessa voi olla korkeintaan 25 merkkiä")

    if password1 != password2:
        errors.append("Salasanat eivät täsmää")

    if username and password1 and username == password1:
        errors.append("Tunnus ei voi olla sama kuin salasana")

    if password1.strip() and len(password1) < 5:
        errors.append("Salasanassa on oltava vähintään 5 merkkiä")

    if errors:
        return render_template("register.html", errors=errors)

    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return render_template(
            "register.html",
            errors=["Tunnus on jo varattu"]
        )

    return redirect("/login")


@app.route("/create_book", methods=["GET", "POST"])
def create_book():
    if request.method == "GET":
        return render_template("create_book.html")
    
    title = request.form["title"].strip()
    author = request.form["author"].strip()
    year = request.form["year"].strip()
    description = request.form["description"].strip()
    genre = request.form["genre"].strip()
    page_count = request.form["page_count"].strip()

    errors = []

    if not title:
        errors.append("Nimi on pakollinen")
    elif len(title) > 150:
        errors.append("Nimi saa olla enintään 150 merkkiä")

    if not author:
        errors.append("Tekijä on pakollinen")
    elif len(author) > 100:
        errors.append("Tekijä saa olla enintään 100 merkkiä")

    if not year:
        errors.append("Vuosi on pakollinen")
    elif not year.isdigit():
        errors.append("Vuoden tulee olla numero")
    else:
        year = int(year)
        if year > 2026:
            errors.append("Vuosi ei voi olla tulevaisuudessa")

    if not genre:
        errors.append("Genre on pakollinen")
    elif len(genre) > 100:
        errors.append("Genre saa olla enintään 100 merkkiä")

    if not page_count:
        errors.append("Sivumäärä on pakollinen")
    elif not page_count.isdigit():
        errors.append("Sivumäärän tulee olla numero")
    else:
        page_count = int(page_count)
        if page_count < 1:
            errors.append("Sivumäärä ei voi olla 0 tai negatiivinen")
        if page_count > 5000:
            errors.append("Sivumäärä ei voi olla yli 5000")

    if len(description) > 1000:
        errors.append("Kuvaus saa olla enintään 1000 merkkiä")

    if errors:
        book = {
            "title": request.form["title"],
            "author": request.form["author"],
            "year": request.form["year"],
            "description": request.form["description"],
            "genre": request.form["genre"],
            "page_count": request.form["page_count"]
        }

        return render_template(
            "create_book.html",
            errors=errors,
            book=book
        )

    
    user_id = db.query(
        "SELECT id FROM users WHERE username = ?",
        [session["username"]]
    )[0][0]

    sql = """
    INSERT INTO books
    (title, author, year, description, genre, page_count, added_by)
    VALUES (?, ?, ?, ?, ?, ?, ?)
"""

    db.execute(sql, [
        title,
        author,
        year,
        description,
        genre,
        page_count,
        user_id
                    ])

    return redirect("/")

@app.route("/books")
def books():
    search = request.args.get("search", "")

    if search:
        sql = """
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ?
        """
        search = "%" + search + "%"
        books = db.query(sql, [search, search])
    else:
        sql = "SELECT * FROM books"
        books = db.query(sql)

    return render_template("books.html", books=books)

@app.route("/book/<int:id>")
def book(id):
    sql = """
        SELECT books.*, users.username
        FROM books
        JOIN users ON books.added_by = users.id
        WHERE books.id = ?
    """
    result = db.query(sql, [id])

    if not result:
        return render_template("book.html", book=None, reviews=[])

    book = result[0]

    sql = """
        SELECT reviews.*, users.username
        FROM reviews
        JOIN users ON reviews.user_id = users.id
        WHERE reviews.book_id = ?
        ORDER BY reviews.created_at DESC
    """
    reviews = db.query(sql, [id])

    user_review = None

    if "user_id" in session:
        result = db.query(
            """
            SELECT *
            FROM reviews
            WHERE book_id = ? AND user_id = ?
            """,
            [id, session["user_id"]]
        )

        if result:
            user_review = result[0]

    return render_template(
        "book.html",
        book=book,
        reviews=reviews,
        user_review=user_review
    )


@app.route("/book/<int:id>/review", methods=["POST"])
def review(id):
    if "user_id" not in session:
        return redirect("/login")

    grade = request.form.get("grade", "").strip()
    title = request.form.get("title", "").strip()
    review_text = request.form.get("review_text", "").strip()
    recommendation = request.form.get("recommendation", "").strip()

    errors = []

    if not grade.isdigit() or not 1 <= int(grade) <= 5:
        errors.append("Arvosanan tulee olla numero väliltä 1–5")

    if not title:
        errors.append("Otsikko on pakollinen")
    elif len(title) > 150:
        errors.append("Otsikko saa olla enintään 150 merkkiä")

    if not review_text:
        errors.append("Arvostelu on pakollinen")
    elif len(review_text) > 2000:
        errors.append("Arvostelu saa olla enintään 2000 merkkiä")

    if not recommendation.isdigit() or not 1 <= int(recommendation) <= 3:
        errors.append("Valitse kelvollinen suositus")

    if errors:
        book_result = db.query("""
            SELECT books.*, users.username
            FROM books
            JOIN users ON books.added_by = users.id
            WHERE books.id = ?
        """, [id])

        if not book_result:
            return "Kirjaa ei löytynyt"

        reviews = db.query("""
            SELECT reviews.*, users.username
            FROM reviews
            JOIN users ON reviews.user_id = users.id
            WHERE reviews.book_id = ?
            ORDER BY reviews.created_at DESC
        """, [id])

        user_review_result = db.query("""
            SELECT *
            FROM reviews
            WHERE book_id = ? AND user_id = ?
        """, [id, session["user_id"]])

        user_review = user_review_result[0] if user_review_result else None

        return render_template(
            "book.html",
            book=book_result[0],
            reviews=reviews,
            user_review=user_review,
            errors=errors
        )

    grade = int(grade)
    recommendation = int(recommendation)

    existing_review = db.query("""
        SELECT id
        FROM reviews
        WHERE book_id = ? AND user_id = ?
    """, [id, session["user_id"]])

    if existing_review:
        db.execute("""
            UPDATE reviews
            SET grade = ?, title = ?, review_text = ?, recommendation = ?
            WHERE book_id = ? AND user_id = ?
        """, [
            grade, title, review_text, recommendation,
            id, session["user_id"]
        ])
    else:
        db.execute("""
            INSERT INTO reviews
            (book_id, user_id, grade, title, review_text, recommendation)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            id, session["user_id"], grade, title,
            review_text, recommendation
        ])

    return redirect("/book/" + str(id))


@app.route("/edit_book/<int:id>")
def edit_book(id):
    sql = "SELECT * FROM books WHERE id = ?"
    result = db.query(sql, [id])

    if not result:
        return render_template("book.html", book=None)

    book = result[0]

    if book["added_by"] != session["user_id"]:
        return "Sinulla ei ole oikeutta muokata tätä kirjaa"

    return render_template("edit_book.html", book=book)


@app.route("/edit_book/<int:id>", methods=["POST"])
def update_book(id):
    result = db.query("SELECT * FROM books WHERE id = ?", [id])

    if not result:
        return "Kirjaa ei löytynyt"

    book = result[0]

    if "user_id" not in session or book["added_by"] != session["user_id"]:
        return "Sinulla ei ole oikeutta muokata tätä kirjaa"

    title = request.form["title"].strip()
    author = request.form["author"].strip()
    year = request.form["year"].strip()
    description = request.form["description"].strip()
    genre = request.form["genre"].strip()
    page_count = request.form["page_count"].strip()

    errors = []

    if not title:
        errors.append("Nimi on pakollinen")
    elif len(title) > 150:
        errors.append("Nimi saa olla enintään 150 merkkiä")

    if not author:
        errors.append("Tekijä on pakollinen")
    elif len(author) > 100:
        errors.append("Tekijä saa olla enintään 100 merkkiä")

    if not year:
        errors.append("Vuosi on pakollinen")
    elif not year.isdigit():
        errors.append("Vuoden tulee olla numero")
    else:
        year = int(year)
        if year > 2026:
            errors.append("Vuosi ei voi olla tulevaisuudessa")

    if not genre:
        errors.append("Genre on pakollinen")
    elif len(genre) > 100:
        errors.append("Genre saa olla enintään 100 merkkiä")

    if not page_count:
        errors.append("Sivumäärä on pakollinen")
    elif not page_count.isdigit():
        errors.append("Sivumäärän tulee olla numero")
    else:
        page_count = int(page_count)
        if page_count < 1:
            errors.append("Sivumäärä ei voi olla negatiivinen")
        if page_count > 5000:
            errors.append("Sivumäärä ei voi olla yli 5000")

    if len(description) > 1000:
        errors.append("Kuvaus saa olla enintään 1000 merkkiä")

    if errors:
        book = dict(book)
        book["title"] = title
        book["author"] = request.form["author"]
        book["year"] = request.form["year"]
        book["description"] = description
        book["genre"] = genre
        book["page_count"] = request.form["page_count"]

        return render_template("edit_book.html", book=book, errors=errors)


    sql = """
        UPDATE books
        SET title = ?, author = ?, year = ?, description = ?,
            genre = ?, page_count = ?
        WHERE id = ?
    """

    db.execute(sql, [
        title,
        author,
        year,
        description,
        genre,
        page_count,
        id
    ])

    return redirect("/books")

@app.route("/users")
def users():
    sql = """
        SELECT users.id, users.username,
            (SELECT COUNT(*) FROM books
             WHERE books.added_by = users.id) AS books_added,
            (SELECT COUNT(*) FROM reviews
             WHERE reviews.user_id = users.id) AS reviews_written
        FROM users
        ORDER BY users.username
    """

    users = db.query(sql)

    return render_template("users.html", users=users)


@app.route("/user/<int:id>")
def user(id):
    sql = """
        SELECT id, username, joined_at
        FROM users
        WHERE id = ?
    """
    result = db.query(sql, [id])

    if not result:
        return render_template("user.html", user=None, reviews=[])

    user = result[0]

    sql = """
        SELECT COUNT(*) AS books_added
        FROM books
        WHERE added_by = ?
    """
    books_added = db.query(sql, [id])[0]["books_added"]

    sql = """
        SELECT COUNT(*) AS reviews_written,
               AVG(grade) AS average_grade
        FROM reviews
        WHERE user_id = ?
    """
    result = db.query(sql, [id])[0]

    reviews_written = result["reviews_written"]
    average_grade = result["average_grade"]

    sql = """
        SELECT reviews.*, books.title AS book_title
        FROM reviews
        JOIN books ON reviews.book_id = books.id
        WHERE reviews.user_id = ?
        ORDER BY reviews.created_at DESC
    """
    reviews = db.query(sql, [id])

    return render_template(
        "user.html",
        user=user,
        books_added=books_added,
        reviews_written=reviews_written,
        average_grade=average_grade,
        reviews=reviews
    )

@app.route("/delete_book/<int:id>", methods=["POST"])
def delete_book(id):
    if "user_id" not in session:
        return redirect("/login")

    result = db.query(
        "SELECT * FROM books WHERE id = ?",
        [id]
    )

    if not result:
        return "Kirjaa ei löytynyt"

    book = result[0]

    if book["added_by"] != session["user_id"]:
        return "Sinulla ei ole oikeutta poistaa tätä kirjaa"

    reviews = db.query(
        "SELECT id FROM reviews WHERE book_id = ?",
        [id]
    )

    if reviews:
        return redirect("/book/" + str(id))

    db.execute(
        "DELETE FROM books WHERE id = ?",
        [id]
    )

    return redirect("/books")


@app.route("/delete_review/<int:id>", methods=["POST"])
def delete_review(id):
    if "user_id" not in session:
        return redirect("/login")

    review = db.query(
        "SELECT * FROM reviews WHERE id = ?",
        [id]
    )

    if not review:
        return "Arvostelua ei löytynyt"

    if review[0]["user_id"] != session["user_id"]:
        return "Sinulla ei ole oikeutta poistaa tätä arvostelua"

    book_id = review[0]["book_id"]

    db.execute(
        "DELETE FROM reviews WHERE id = ?",
        [id]
    )

    return redirect("/book/" + str(book_id))