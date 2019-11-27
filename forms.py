from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, Form, TextAreaField
from wtforms.validators import Length, Email, EqualTo, InputRequired, ValidationError, DataRequired
# from .app import Users


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

#
# class EditForm(Form):
#     nickname = StringField('nickname', validators=[DataRequired()])
#     about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
#
#     def __init__(self, original_nickname, *args, **kwargs):
#         Form.__init__(self, *args, **kwargs)
#         self.original_nickname = original_nickname
#
#     def validate(self):
#         if not Form.validate(self):
#             return False
#         if self.nickname.data == self.original_nickname:
#             return True
#         user = Users.query.filter_by(nickname=self.nickname.data).first()
#         if user is not None:
#             self.nickname.errors.append('This nickname is already in use. '
#                                         'Please choose another one.')
#             return False
#         return True
