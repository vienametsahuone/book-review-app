import db
from flask import g


def get_genres():
    return db.query("SELECT id, name FROM genres ORDER BY name")


def get_books(search=""):
    if search:
        search_value = "%" + search + "%"
        sql = """
            SELECT DISTINCT books.*
            FROM books
            LEFT JOIN book_genres ON books.id = book_genres.book_id
            LEFT JOIN genres ON book_genres.genre_id = genres.id
            WHERE books.title LIKE ?
               OR books.author LIKE ?
               OR genres.name LIKE ?
            ORDER BY books.title
        """
        result = db.query(
            sql, [search_value, search_value, search_value]
        )
    else:
        result = db.query("""
            SELECT id, title, author, year, description, page_count, added_by
            FROM books
            ORDER BY title
        """)

    book_list = [dict(book) for book in result]

    for book in book_list:
        book["genres"] = db.query(
            """
            SELECT genres.name
            FROM genres
            JOIN book_genres ON genres.id = book_genres.genre_id
            WHERE book_genres.book_id = ?
            ORDER BY genres.name
            """,
            [book["id"]]
        )

    for book in book_list:
        rating = get_book_rating(book["id"])
        book["average_grade"] = rating["average_grade"]
        book["review_count"] = rating["review_count"]

    return book_list


def get_book(id):
    result = db.query(
        """
        SELECT books.*, users.username
        FROM books
        JOIN users ON books.added_by = users.id
        WHERE books.id = ?
        """,
        [id]
    )

    if not result:
        return None

    book = dict(result[0])

    book["genres"] = db.query(
        """
        SELECT genres.name
        FROM genres
        JOIN book_genres ON genres.id = book_genres.genre_id
        WHERE book_genres.book_id = ?
        ORDER BY genres.name
        """,
        [id]
    )

    rating = get_book_rating(id)
    book["average_grade"] = rating["average_grade"]
    book["review_count"] = rating["review_count"]

    return book


def get_book_rating(book_id):
    result = db.query(
        """
        SELECT COUNT(*) AS review_count,
               AVG(grade) AS average_grade
        FROM reviews
        WHERE book_id = ?
        """,
        [book_id]
    )

    return result[0]


def get_book_for_edit(id):
    result = db.query("""
        SELECT id, title, author, year, description, page_count, added_by, image_filename
        FROM books
        WHERE id = ?
    """, [id])

    if not result:
        return None

    return dict(result[0])


def get_selected_genres(id):
    result = db.query(
        "SELECT genre_id FROM book_genres WHERE book_id = ?",
        [id]
    )

    return [str(row["genre_id"]) for row in result]


def create_book(title, author, year, description, page_count,
                user_id, selected_genres, image_filename=None):
    db.execute(
        """
        INSERT INTO books
        (title, author, year, description, page_count, added_by, image_filename)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [title, author, year, description, page_count, user_id, image_filename]
    )

    book_id = g.last_insert_id

    for genre_id in selected_genres:
        db.execute(
            "INSERT INTO book_genres (book_id, genre_id) VALUES (?, ?)",
            [book_id, int(genre_id)]
        )

    return book_id


def update_book(id, title, author, year, description, page_count,
                selected_genres, image_filename):
    db.execute(
        """
        UPDATE books
        SET title = ?, author = ?, year = ?, description = ?,
            page_count = ?, image_filename = ?
        WHERE id = ?
        """,
        [title, author, year, description, page_count, image_filename, id]
    )

    db.execute("DELETE FROM book_genres WHERE book_id = ?", [id])

    for genre_id in selected_genres:
        db.execute(
            "INSERT INTO book_genres (book_id, genre_id) VALUES (?, ?)",
            [id, int(genre_id)]
        )


def delete_book(id):
    db.execute("DELETE FROM book_genres WHERE book_id = ?", [id])
    db.execute("DELETE FROM books WHERE id = ?", [id])


def get_random_book():
    sql = """
        SELECT id, title, author, year
        FROM books
        ORDER BY RANDOM()
        LIMIT 1
    """
    result = db.query(sql)

    if result:
        book = dict(result[0])

        book["genres"] = db.query(
            """
            SELECT genres.name
            FROM genres
            JOIN book_genres ON genres.id = book_genres.genre_id
            WHERE book_genres.book_id = ?
            ORDER BY genres.name
            """,
            [book["id"]]
        )

        return book

    return None