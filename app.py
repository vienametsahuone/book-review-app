import sqlite3
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash

import config
import db
import books as book_data
import reviews as review_data
import users as user_data

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

    user = user_data.get_login_user(username)

    if not user or not check_password_hash(user["password_hash"], password):
        return render_template(
            "index.html", error="Väärä tunnus tai salasana"
        )

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
        errors.append(
            "Tunnuksessa saa olla vain englannin kirjaimia, numeroita ja alaviivoja"
        )

    if not username:
        errors.append(
            "Tunnus ei voi olla tyhjä tai sisältää vain välilyöntejä"
        )

    if not password1.strip():
        errors.append(
            "Salasana ei voi olla tyhjä tai sisältää vain välilyöntejä"
        )

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
        user_data.create_user(username, password_hash)
    except sqlite3.IntegrityError:
        return render_template(
            "register.html",
            errors=["Tunnus on jo varattu"]
        )

    return redirect("/login")


@app.route("/create_book", methods=["GET", "POST"])
def create_book():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "GET":
        return render_template(
            "create_book.html",
            genres=book_data.get_genres(),
            selected_genres=[]
        )

    title = request.form["title"].strip()
    author = request.form["author"].strip()
    year = request.form["year"].strip()
    description = request.form["description"].strip()
    selected_genres = request.form.getlist("genres")
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

    genres = book_data.get_genres()
    valid_genre_ids = {str(genre["id"]) for genre in genres}

    if not selected_genres:
        errors.append("Valitse vähintään yksi genre")
    elif len(selected_genres) > 3:
        errors.append("Voit valita enintään kolme genreä")

    if any(genre_id not in valid_genre_ids for genre_id in selected_genres):
        errors.append("Valitse kelvolliset genret")

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
            "title": title,
            "author": author,
            "year": request.form["year"],
            "description": description,
            "page_count": request.form["page_count"]
        }

        return render_template(
            "create_book.html",
            errors=errors,
            book=book,
            genres=genres,
            selected_genres=selected_genres
        )

    book_id = book_data.create_book(
        title, author, year, description, page_count,
        session["user_id"], selected_genres
    )

    return redirect("/book/" + str(book_id))


@app.route("/books")
def books():
    search = request.args.get("search", "").strip()
    book_list = book_data.get_books(search)

    return render_template("books.html", books=book_list)


@app.route("/book/<int:id>")
def book(id):
    book_info = book_data.get_book(id)

    if not book_info:
        return render_template(
            "book.html", book=None, reviews=[], user_review=None
        )

    book_reviews = review_data.get_reviews_for_book(id)

    user_review = None
    if "user_id" in session:
        user_review = review_data.get_user_review(
            id, session["user_id"]
        )

    return render_template(
        "book.html",
        book=book_info,
        reviews=book_reviews,
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

    book_info = book_data.get_book(id)
    if not book_info:
        return "Kirjaa ei löytynyt"

    if errors:
        return render_template(
            "book.html",
            book=book_info,
            reviews=review_data.get_reviews_for_book(id),
            user_review=review_data.get_user_review(
                id, session["user_id"]
            ),
            errors=errors
        )

    review_data.save_review(
        id,
        session["user_id"],
        int(grade),
        title,
        review_text,
        int(recommendation)
    )

    return redirect("/book/" + str(id))


@app.route("/edit_book/<int:id>")
def edit_book(id):
    book_info = book_data.get_book_for_edit(id)

    if not book_info:
        return "Kirjaa ei löytynyt"

    if "user_id" not in session or book_info["added_by"] != session["user_id"]:
        return "Sinulla ei ole oikeutta muokata tätä kirjaa"

    return render_template(
        "edit_book.html",
        book=book_info,
        genres=book_data.get_genres(),
        selected_genres=book_data.get_selected_genres(id)
    )


@app.route("/edit_book/<int:id>", methods=["POST"])
def update_book(id):
    book_info = book_data.get_book_for_edit(id)

    if not book_info:
        return "Kirjaa ei löytynyt"

    if "user_id" not in session or book_info["added_by"] != session["user_id"]:
        return "Sinulla ei ole oikeutta muokata tätä kirjaa"

    title = request.form["title"].strip()
    author = request.form["author"].strip()
    year = request.form["year"].strip()
    description = request.form["description"].strip()
    page_count = request.form["page_count"].strip()
    selected_genres = request.form.getlist("genres")

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

    genres = book_data.get_genres()
    valid_genre_ids = {str(genre["id"]) for genre in genres}

    if not selected_genres:
        errors.append("Valitse vähintään yksi genre")
    elif len(selected_genres) > 3:
        errors.append("Voit valita enintään kolme genreä")

    if any(genre_id not in valid_genre_ids for genre_id in selected_genres):
        errors.append("Valitse kelvolliset genret")

    if not page_count:
        errors.append("Sivumäärä on pakollinen")
    elif not page_count.isdigit():
        errors.append("Sivumäärän tulee olla numero")
    else:
        page_count = int(page_count)
        if page_count < 1:
            errors.append("Sivumäärän tulee olla vähintään 1")
        if page_count > 5000:
            errors.append("Sivumäärä ei voi olla yli 5000")

    if len(description) > 1000:
        errors.append("Kuvaus saa olla enintään 1000 merkkiä")

    if errors:
        book_info["title"] = title
        book_info["author"] = author
        book_info["year"] = request.form["year"]
        book_info["description"] = description
        book_info["page_count"] = request.form["page_count"]

        return render_template(
            "edit_book.html",
            book=book_info,
            genres=genres,
            selected_genres=selected_genres,
            errors=errors
        )

    book_data.update_book(
        id, title, author, year, description, page_count,
        selected_genres
    )

    return redirect("/book/" + str(id))


@app.route("/users")
def users():
    user_list = user_data.get_users()
    return render_template("users.html", users=user_list)


@app.route("/user/<int:id>")
def user(id):
    user_info = user_data.get_user(id)

    if not user_info:
        return render_template("user.html", user=None, reviews=[])

    books_added = user_data.get_books_added_count(id)
    stats = review_data.get_user_review_stats(id)
    user_reviews = review_data.get_user_reviews(id)

    return render_template(
        "user.html",
        user=user_info,
        books_added=books_added,
        reviews_written=stats["reviews_written"],
        average_grade=stats["average_grade"],
        reviews=user_reviews
    )


@app.route("/delete_book/<int:id>", methods=["POST"])
def delete_book(id):
    if "user_id" not in session:
        return redirect("/login")

    book_info = book_data.get_book_for_edit(id)

    if not book_info:
        return "Kirjaa ei löytynyt"

    if book_info["added_by"] != session["user_id"]:
        return "Sinulla ei ole oikeutta poistaa tätä kirjaa"

    if review_data.count_reviews_for_book(id):
        return redirect("/book/" + str(id))

    book_data.delete_book(id)

    return redirect("/books")


@app.route("/delete_review/<int:id>", methods=["POST"])
def delete_review(id):
    if "user_id" not in session:
        return redirect("/login")

    review_info = review_data.get_review(id)

    if not review_info:
        return "Arvostelua ei löytynyt"

    if review_info["user_id"] != session["user_id"]:
        return "Sinulla ei ole oikeutta poistaa tätä arvostelua"

    book_id = review_data.delete_review(id)

    return redirect("/book/" + str(book_id))