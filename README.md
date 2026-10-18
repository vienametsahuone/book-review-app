# Book Review App

## Description

A web application for sharing book reviews. Users can register, log in, add books, search for books, and write reviews with ratings and recommendations. Each book has its own page displaying its information, reviews, and average rating.

Users can edit their own books and reviews. Books cannot be deleted if doing so would remove reviews written by other users.

## Requirements

- Python 3
- Flask
- SQLite

## Setup

### 1. Clone the repository

Clone the repository and navigate to the project directory.

### 2. Create a virtual environment

Run the following commands:

    python3 -m venv venv
    source venv/bin/activate

### 3. Install Flask

    pip install flask

### 4. Create the database

The database file is not included in the repository. Create it using the provided SQL schema file:

    sqlite3 database.db < schema.sql

This creates the database and inserts the initial genre data.

## Running the application

Make sure the virtual environment is activated and you are in the project directory. Start the application with:

    flask run

Open the local URL shown in the terminal in your browser.

## Testing the application

1. Register a new user account and log in.
2. Add a book and select its genres.
3. Browse the book list and search for books.
4. Open a book's page and check its information and average rating.
5. Write a review with a rating and recommendation.
6. Edit a book you added and a review you wrote.
7. Visit the users page and your own profile.
8. Log out.

## Notes

- The database must be created locally before running the application.
- SQLite is used to store users, books, genres, and reviews.