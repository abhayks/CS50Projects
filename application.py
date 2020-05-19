import os

from flask import Flask, session, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import LoginForm, RegistrationForm
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


@app.route("/")
def index():
	return "Project 1: TODO"


@app.route('/login' , methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		flash('Login requested for user {}, remember_me={}'.format(
			form.username.data, form.remember_me.data))
		username = request.form['username']
		password = request.form['password']
		print(username)
		print(password)
		passwordhash = db.execute(
			"SELECT passwordhash FROM users where username= :name", {"name": username}	).fetchone()
		print(passwordhash)	
		print (passwordhash.count("$"))
		if  check_password_hash(passwordhash, password):
			print ("Passwords match")
		else:
			print ("Passwords Do not match")
		return redirect(url_for('index'))
	return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
	error= None
	form=RegistrationForm()
	if form.validate_on_submit():
		username = request.form['username']
		password = request.form['password']
		session=Session()
		if session.execute(
			"SELECT user_id FROM user WHERE username = :name", {"name": username}	).fetchone() is not None:
			error = f"User {username} is already registered."
		else:
			session.execute(
				'INSERT INTO user (username, password) VALUES (?, ?)',
				(username, generate_password_hash(password))
			)
			session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

