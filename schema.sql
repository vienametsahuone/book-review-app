CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    joined_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT,
    author TEXT,
    year INTEGER,
    description TEXT,
    genre TEXT,
    page_count INTEGER,
    added_by INTEGER,
    FOREIGN KEY (added_by) REFERENCES users(id)
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    book_id INTEGER,
    user_id INTEGER,
    grade INTEGER,
    title TEXT,
    review_text TEXT,
    recommendation INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(book_id, user_id)
);