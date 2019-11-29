from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Length, Email, EqualTo, InputRequired, ValidationError, DataRequired
from app import User
from flask_login import current_user
from flask import flash
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
    fname = StringField('Frist Name', validators=[InputRequired(), Length(min=2, max=20)])
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
    country = StringField('Country')
    city = StringField('City')
    submit = SubmitField('Update')


class UpdatePasswordForm(FlaskForm):
    oldPassword = PasswordField('Old Password', validators=[InputRequired()])
    newPassword = PasswordField('New Password', validators=[InputRequired()])
    confirmPassword = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('newPassword')])
    submit = SubmitField('Update')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Reset')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with this email.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')