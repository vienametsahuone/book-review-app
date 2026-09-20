CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
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

