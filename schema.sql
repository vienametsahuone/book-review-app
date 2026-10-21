CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
    profile_picture TEXT
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT,
    author TEXT,
    year INTEGER,
    description TEXT,
    page_count INTEGER,
    added_by INTEGER,
    image_filename TEXT,
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


CREATE TABLE genres (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE book_genres (
    book_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id)
);

INSERT INTO genres (name) VALUES
    ('Fantasy'),
    ('Science fiction'),
    ('Mystery'),
    ('Thriller'),
    ('Romance'),
    ('Horror'),
    ('Historical fiction'),
    ('Contemporary fiction'),
    ('Literary fiction'),
    ('Adventure'),
    ('Biography'),
    ('History'),
    ('Self-help'),
    ('Science'),
    ('Psychology'),
    ('Children''s books'),
    ('Middle grade'),
    ('Young adult'),
    ('Graphic novels'),
    ('Poetry'),
    ('Other');