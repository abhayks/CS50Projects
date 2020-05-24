import os

from flask import Flask, session, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import LoginForm, RegistrationForm, BookSearchForm
from config import Config
from flask import render_template, request, redirect, url_for,  jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)



# Check for environment variable
if not os.getenv("DATABASE_URL"):
	raise RuntimeError("DATABASE_URL is not set")

print (os.getenv("DATABASE_URL"))	

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET', 'POST'])
def index():
	if not session.get('logged_in'):
		print("Not logged in")
		return redirect(url_for('login'))
	else:
		print ("Logged in")
		search = BookSearchForm(request.form)
		if request.method == 'POST':
			method = request.form['select']
			keywords = request.form['search']
			sql = f"Select * from books where Lower({method}) like Lower('%{keywords}%')"
			#print(f" SQL going ot be executed {sql} ")
			books=db.execute(sql
			).fetchall()
			if books is None:
				flash(u'No Books found with this criteria', 'error')
				return render_template('index.html', title='Glenwood Public Library', form=search )
			return render_template('books.html', title='Glenwood Public Library', books=books)
		return render_template('index.html', title='Glenwood Public Library', form=search )

@app.route("/books/<int:book_id>")
def book(book_id):
	if not session.get('logged_in'):
		print("Not logged in")
		return redirect(url_for('login'))
	else:
		userreviewed=False
		book= db.execute(
			"Select * from books where book_id= :book_id", {"book_id": book_id}	).fetchone()
		if book is None:
			flash(u'No Books found with this book ID', 'error')
			return render_template('index.html', title='Glenwood Public Library' )
		  # Get all reviews.
		reviews = db.execute("SELECT rev.rating, rev.text, usr.username, rev.user_id FROM reviews rev, users usr  WHERE rev.book_id = :book_id and usr.user_id=rev.user_id", {"book_id": book_id}).fetchall()
		# SELECT rev.rating, rev.text, usr.username, rev.user_id FROM reviews rev, users usr  WHERE rev.book_id = :book_id and usr.user_id=rev.user_id"
		if  reviews is None:
			flash(u'No review found with this book ID', 'error')
		for review in reviews:
			if review['user_id'] == session['user_id']:
				userreviewed=True
				flash(u'You have already reviewed this book', 'error')
		return render_template("bookDetails.html", book=book, reviews=reviews, userreviewed=userreviewed)

	#return  redirect(url_for('login'))

@app.route("/books/<int:book_id>/review" , methods=['GET', 'POST'])
def bookreview(book_id):
	if not session.get('logged_in'):
		print("Not logged in")
		return redirect(url_for('login'))
	else:
		print (request.method)
		if request.method == 'POST':
			star = request.form['star']
			reviewtext = request.form['reviewtext']
			print (star)
			print(reviewtext)
			sql=f"Insert into reviews (text, rating, user_id, book_id) VALUES ('{reviewtext}', {star}, {session['user_id']}, {book_id})"
			db.execute(sql)
			db.commit()
			return redirect(url_for('book', book_id=book_id))
		return render_template('starReview.html', book_id=book_id)
    
@app.route("/logout")
def logout():
	session['logged_in'] = False
	session.clear()  ### Added to clear session. 
	return index()


@app.route('/login' , methods=['GET', 'POST'])
def login():
	print("Entering Login Form")
	form = LoginForm()
	if form.validate_on_submit():
	#	flash('Login requested for user {}, remember_me={}'.format(
	#		form.username.data, form.remember_me.data))
		username = request.form['username']
		password = request.form['password']
		print(username)
		print(password)
		error = None
		user = db.execute(
			"SELECT * FROM users where username= :name", {"name": username}	).fetchone()
		if user is None:
			error = 'Incorrect username.'
			flash(u'Invalid user provided', 'error')
		elif not check_password_hash(user['passwordhash'], password):
			error = 'Incorrect password.'
			flash(u'Invalid password provided', 'error')
		if error is None:
			session['logged_in'] = True
			session['user_id']=user['user_id']
			return redirect(url_for('index'))
	return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
	error= None
	form=RegistrationForm()
	if form.validate_on_submit():
		username = request.form['username']
		password = request.form['password']
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		email = request.form['email']	
		if db.execute(
			"SELECT user_id FROM users WHERE username = :name", {"name": username}	).fetchone() is not None:
			print(f"User {username} is already registered.")
			flash(f"User {username} is already registered.", 'error')
			return render_template('register.html', title='Register', form=form)
		else:
			#sql="Insert into users (username, passwordhash,first_name,last_name, email) "
			#sql+=    "VALUES (%s, %s, %s, %s, %s)"
			password_hash=generate_password_hash(password)
			#recordToInsert=(username, password_hash, first_name,last_name,  email)
			db.execute("Insert into users (username, passwordhash,first_name,last_name, email) VALUES (:username, :password_hash, :first_name,:last_name, :email)",
				{"username": username, "password_hash": password_hash, "first_name": first_name, "last_name": last_name, "email": email})
			#db.execute(sql, recordToInsert)
			db.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/api/<string:isbn>')
def bookdetails_api(isbn):
	reviewcount=0
	averagerating=0
	booksql=f"Select * from books where isbn='{isbn}'"
	print(booksql)
	book = db.execute(booksql).fetchone()
	if book is None:
		error = ''
		flash(u'Book with ISBN not found.', 'error')
		return jsonify({"Error !!": "Invalid ISBN "}), 404   # Pass back 404
	else:
		reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book['book_id']}).fetchall()
		if  reviews is None:
			flash(u'No review found with this book ID', 'error')
		else:
			for review in reviews:
				reviewcount+=1
				averagerating=averagerating+int(review['rating'])
	if(reviewcount):
		if(averagerating):
			averagerating=averagerating/reviewcount
	
	return jsonify({
		"title": book['title'],
		"author": book['author'],
		"year":book['year'],
		"isbn": book['isbn'],
		"review_count": reviewcount,
		"average_score": averagerating
          })
					
