from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import Length, Email, EqualTo, InputRequired, ValidationError, DataRequired
from app import User
from flask_login import current_user
from flask_wtf.file import FileAllowed, FileField


class RegistrationForm(FlaskForm):
    fname = StringField('fname', validators=[InputRequired(), Length(min=2, max=20)])
    lname = StringField('lname')
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[InputRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email already exists')

    def validate_phone(self, phone):
        if len(phone.data) != 11:
            raise ValidationError('Invalid phone number length.')
        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('This phone number already exists')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    fname = StringField('First Name', validators=[InputRequired(), Length(min=2, max=20)])
    lname = StringField('Last Name', validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    phone = StringField('Phone', validators=[InputRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email already exists')

    def validate_phone(self, phone):
        if phone.data != current_user.phone:
            if len(phone.data) != 11:
                raise ValidationError('Invalid phone number length.')
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('This phone number already exists')


class LocationForm(FlaskForm):
    country = StringField('Country', validators=[InputRequired()])
    city = StringField('City', validators=[InputRequired()])
    submit = SubmitField('Update')


class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
