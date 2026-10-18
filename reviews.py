import db


def get_reviews_for_book(book_id):
    return db.query(
        """
        SELECT reviews.*, users.username
        FROM reviews
        JOIN users ON reviews.user_id = users.id
        WHERE reviews.book_id = ?
        ORDER BY reviews.created_at DESC
        """,
        [book_id]
    )


def get_user_review(book_id, user_id):
    result = db.query(
        """
        SELECT id, book_id, user_id, grade, title, review_text,
               recommendation, created_at
        FROM reviews
        WHERE book_id = ? AND user_id = ?
        """,
        [book_id, user_id]
    )

    return result[0] if result else None


def save_review(book_id, user_id, grade, title,
                review_text, recommendation):
    existing_review = db.query(
        """
        SELECT id
        FROM reviews
        WHERE book_id = ? AND user_id = ?
        """,
        [book_id, user_id]
    )

    if existing_review:
        db.execute(
            """
            UPDATE reviews
            SET grade = ?, title = ?, review_text = ?,
                recommendation = ?
            WHERE book_id = ? AND user_id = ?
            """,
            [
                grade, title, review_text, recommendation,
                book_id, user_id
            ]
        )
    else:
        db.execute(
            """
            INSERT INTO reviews
            (book_id, user_id, grade, title, review_text, recommendation)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                book_id, user_id, grade, title,
                review_text, recommendation
            ]
        )


def get_review(id):
    result = db.query("""
        SELECT id, book_id, user_id, grade, title, review_text,
               recommendation, created_at
        FROM reviews
        WHERE id = ?
    """, [id])
    return result[0] if result else None


def delete_review(id):
    review = get_review(id)

    if not review:
        return None

    book_id = review["book_id"]

    db.execute("DELETE FROM reviews WHERE id = ?", [id])

    return book_id


def get_user_reviews(user_id):
    return db.query(
        """
        SELECT reviews.*, books.title AS book_title
        FROM reviews
        JOIN books ON reviews.book_id = books.id
        WHERE reviews.user_id = ?
        ORDER BY reviews.created_at DESC
        """,
        [user_id]
    )


def count_reviews_for_book(book_id):
    return db.query(
        "SELECT id FROM reviews WHERE book_id = ?",
        [book_id]
    )


def get_user_review_stats(user_id):
    return db.query(
        """
        SELECT COUNT(*) AS reviews_written,
               AVG(grade) AS average_grade
        FROM reviews
        WHERE user_id = ?
        """,
        [user_id]
    )[0]
