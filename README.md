# Book review app

* Users can add books that they have read. Books have details such as author, genre, page count, plot description, and average review score. 

* Users can create an account and log in to the app. 

* Users can add books and edit the books they have added. 

* Users can see all the books added to the app. 

* Users can search for books based on the name or author. 

* The user page shows how many books the user has added, lists the added books and reviews by the user, and shows the average score the user has given to the books they have reviewed. 

* Users can choose classifications, such as genre. 

* Users can add reviews for the books, with a comment and score. Books also show the comments and reviews from users. 

# How to use

* Clone the repo: git clone https://github.com/vienametsahuone/book-review-app

* Install dependencies: pip install -r requirements.txt

* To create the database, run: sqlite3 database.db < schema.sql 

* First create an account from the front page. After creating the account, go back to the front page to add books.

* Please note that there is no delete feature, as users cannot delete books they have added in order to prevent other users’ reviews from being deleted. 