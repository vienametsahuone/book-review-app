import db
from flask import g


def get_genres():
    return db.query("SELECT * FROM genres ORDER BY name")


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
        result = db.query("SELECT * FROM books ORDER BY title")

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

    return book


def get_book_for_edit(id):
    result = db.query("SELECT * FROM books WHERE id = ?", [id])

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
                user_id, selected_genres):
    db.execute(
        """
        INSERT INTO books
        (title, author, year, description, page_count, added_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [title, author, year, description, page_count, user_id]
    )

    book_id = g.last_insert_id

    for genre_id in selected_genres:
        db.execute(
            "INSERT INTO book_genres (book_id, genre_id) VALUES (?, ?)",
            [book_id, int(genre_id)]
        )

    return book_id


def update_book(id, title, author, year, description, page_count,
                selected_genres):
    db.execute(
        """
        UPDATE books
        SET title = ?, author = ?, year = ?, description = ?,
            page_count = ?
        WHERE id = ?
        """,
        [title, author, year, description, page_count, id]
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
