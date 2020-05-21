import os

from flask import Flask, session, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import LoginForm, RegistrationForm, BookSearchForm
from config import Config
from flask import render_template, request, redirect, url_for
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
			sql = f"Select * from books where {method} like '%{keywords}%'"
			#print(f" SQL going ot be executed {sql} ")
			books=db.execute(sql
			).fetchall()
			return render_template('books.html', title='Glenwood Public Library', books=books)
		return render_template('index.html', title='Glenwood Public Library', form=search )

@app.route("/books/<int:book_id>")
def book(book_id):
	return  redirect(url_for('login'))
      # Make sure flight exists.
      #flight = db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).fetchone()
      #if flight is None:
      #    return render_template("error.html", message="No such flight.")

      # Get all passengers.
      #passengers = db.execute("SELECT name FROM passengers WHERE flight_id = :flight_id",
      #                        {"flight_id": flight_id}).fetchall()
      #return render_template("flight.html", flight=flight, passengers=passengers)

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
			"SELECT passwordhash FROM users where username= :name", {"name": username}	).fetchone()
		if user is None:
			error = 'Incorrect username.'
			print(error)
		elif not check_password_hash(user['passwordhash'], password):
			error = 'Incorrect password.'
			print(error)
		if error is None:
			session['logged_in'] = True
			session['user']=username
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
		print(username)
		print(password)
		print(first_name)
		print(last_name)
		print(email)	
		if db.execute(
			"SELECT user_id FROM users WHERE username = :name", {"name": username}	).fetchone() is not None:
			print(f"User {username} is already registered.")
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
	#	flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/results')
def search_results(search):
	print(search)
	results = []
	search_string = search.data['search']
	print (search_string)
	return redirect(url_for('index'))

	
