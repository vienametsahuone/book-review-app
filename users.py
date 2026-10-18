import db


def get_login_user(username):
    result = db.query(
        "SELECT id, password_hash FROM users WHERE username = ?",
        [username]
    )

    return result[0] if result else None


def create_user(username, password_hash):
    db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        [username, password_hash]
    )


def get_users():
    return db.query(
        """
        SELECT users.id, users.username,
            (SELECT COUNT(*) FROM books
             WHERE books.added_by = users.id) AS books_added,
            (SELECT COUNT(*) FROM reviews
             WHERE reviews.user_id = users.id) AS reviews_written
        FROM users
        ORDER BY users.username
        """
    )


def get_user(id):
    result = db.query(
        """
        SELECT id, username, joined_at
        FROM users
        WHERE id = ?
        """,
        [id]
    )

    return result[0] if result else None


def get_books_added_count(user_id):
    return db.query(
        "SELECT COUNT(*) AS books_added FROM books WHERE added_by = ?",
        [user_id]
    )[0]["books_added"]
