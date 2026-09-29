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
    del session["username"]
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not username:
        return render_template("register.html",
                               error="Tunnus puuttuu")

    if not password1:
        return render_template("register.html",
                               error="Salasana puuttuu")

    if len(username) > 25:
        return render_template("register.html",
                                error="Tunnuksessa voi olla korkeintaan 25 kirjainta")

    if password1 != password2:
        return render_template("register.html",
                               error="Salasanat eivät täsmää")

    if username == password1:
        return render_template("register.html",
                                       error="Tunnus ei voi olla sama kuin salasana")

    if len(password1) < 5:
        return render_template("register.html",
                                       error="Salasanassa on oltava vähintään 5 kirjainta")

    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return render_template("register.html",
                               error="Tunnus on jo varattu")

    return redirect("/login")

@app.route("/create_book", methods=["POST"])
def create_book():
    title = request.form["title"]
    author = request.form["author"]
    year = request.form["year"]
    description = request.form["description"]
    genre = request.form["genre"]
    page_count = request.form["page_count"]

    errors = []

    if not title:
        errors.append("Nimi on pakollinen")

    if len(title) > 150:
        errors.append("Nimi saa olla enintään 150 merkkiä")

    if not author:
        errors.append("Tekijä on pakollinen")

    if len(author) > 100:
        errors.append("Tekijä saa olla enintään 100 merkkiä")

    if not year:
        errors.append("Vuosi on pakollinen")

    elif not year.isdigit():
        errors.append("Vuoden tulee olla numero")

    else:
        year = int(year)

        if year > 2026 or year < 0:
            errors.append("Vuoden tulee olla väliltä 0 ja 2026")

    if not genre:
        errors.append("Genre on pakollinen")

    if len(genre) > 100:
        errors.append("Genre saa olla enintään 100 merkkiä")

    if not page_count:
        errors.append("Sivumäärä on pakollinen")

    elif not page_count.isdigit():
        errors.append("Sivumäärän tulee olla numero")

    else:
        page_count = int(page_count)

        if page_count < 0:
            errors.append("Sivumäärä ei voi olla negatiivinen")
    

    if len(description) > 1000:
        errors.append("Kuvaus saa olla enintään 1000 merkkiä")

    if errors:
        return render_template("index.html", errors=errors)

    
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


@app.route("/edit_book/<int:id>")
def edit_book(id):
    sql = "SELECT * FROM books WHERE id = ?"
    result = db.query(sql, [id])

    if not result:
        return "Kirjaa ei löytynyt"

    book = result[0]

    if book["added_by"] != session["user_id"]:
        return "Sinulla ei ole oikeutta muokata tätä kirjaa"

    return render_template("edit_book.html", book=book)


@app.route("/edit_book/<int:id>", methods=["POST"])
def update_book(id):
    title = request.form["title"]
    author = request.form["author"]
    year = request.form["year"]
    genre = request.form["genre"]
    page_count = request.form["page_count"]
    description = request.form["description"]

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