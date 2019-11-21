from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, Form
from wtforms.validators import Length, Email, EqualTo, InputRequired, ValidationError


class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    phone = StringField('Phone', validators=[InputRequired()])
    submit = SubmitField('Sign Up')

    # def validate_phone(form, field):
    #     if len(field.data) != 12:
    #         raise ValidationError('Invalid phone number length.')
    #     try:
    #         input_number = phonenumbers.parse(field.data)
    #         if not (phonenumbers.is_valid_number(input_number)):
    #             raise ValidationError('Invalid phone number length.')
    #     except:
    #         input_number = phonenumbers.parse("+92" + field.data)
    #         if not (phonenumbers.is_valid_number(input_number)):
    #             raise ValidationError('Invalid phone number length.')


class LoginForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')
