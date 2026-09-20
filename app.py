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


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if not result:
        return "VIRHE: väärä tunnus tai salasana"

    user_id = result[0][0]
    password_hash = result[0][1]

    if check_password_hash(password_hash, password):
        session["username"] = username
        session["user_id"] = user_id
        return redirect("/")
    else:
        return "VIRHE: väärä tunnus tai salasana"

    
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
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/create_book", methods=["POST"])
def create_book():
    title = request.form["title"]
    author = request.form["author"]
    year = request.form["year"]
    description = request.form["description"]
    genre = request.form["genre"]
    page_count = request.form["page_count"]

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