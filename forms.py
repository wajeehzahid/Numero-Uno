from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, Form, TextAreaField
from wtforms.validators import Length, Email, EqualTo, InputRequired, ValidationError, DataRequired


class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[InputRequired()])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
