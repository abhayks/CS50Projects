import os 
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")
# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))    

for i in range (2,10):
	password=f"user{i}"
	password_hash=generate_password_hash(password)
	sql=f"insert into users (username, passwordhash, first_name, last_name, email) values ('user{i}', '{password_hash}', 'first_user{i}', 'user{i}_last', 'user{i}@mail.com')"
	db.execute(sql)
	
db.commit() # transactions are assumed, so close the transaction finished
