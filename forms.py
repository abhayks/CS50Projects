from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo 

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[ Email()])
	first_name = StringField('first_name')
	last_name = StringField('last_name')
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

class BookSearchForm(FlaskForm):
	choices = [('title', 'Title'),
		('isbn', 'ISBN'),
		('year', 'Year'),
		('author', 'Author')]
	select = SelectField('Search books:', choices=choices)
	print(select)
	search = StringField( '')	
