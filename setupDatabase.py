import os 
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))  

# Drop Tables 
db.execute("DROP TABLE IF EXISTS users,books,reviews")
db.execute("""CREATE TABLE IF NOT EXISTS books ( 
		book_id SERIAL PRIMARY KEY,
                title TEXT,
                author TEXT,
                isbn TEXT Unique,
                year TEXT                
                );CREATE TABLE IF NOT EXISTS users (
      		user_id SERIAL PRIMARY KEY,
                username TEXT UNIQUE,
                passwordhash TEXT,
                first_name TEXT,
                last_name TEXT,
                email  TEXT
                );
                CREATE TABLE IF NOT EXISTS reviews (
                review_id SERIAL PRIMARY KEY,
                text TEXT,
                rating TEXT,
                user_id INTEGER REFERENCES users(user_id),
                book_id INTEGER REFERENCES books(book_id)
                )"""
                )
db.commit() # transactions are assumed, so close the transaction finished
