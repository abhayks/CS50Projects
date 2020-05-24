import os 
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")
# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))    

for book_id in range(2,9):
	for user_id in range (4,10):
		rating=random.randint(1,5)
		sql=f"insert into reviews (text, rating, user_id, book_id) values ('text{user_id}_{book_id}', '{rating}', '{user_id}', '{book_id}')"
		db.execute(sql)
	
db.commit() # transactions are assumed, so close the transaction finished
