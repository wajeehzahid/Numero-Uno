from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import PIL
from flask import Flask, render_template, url_for, flash, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user, login_required
from flask_bcrypt import Bcrypt
import secrets
from PIL import Image
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\sqlite\project.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://newuser:''@localhost/newdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'flask.testing2@gmail.com'
app.config['MAIL_PASSWORD'] = 'Flask123'
mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), default='')
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.fname}', '{self.lname}' '{self.email}', '{self.phone}', '{self.image_file}')"


class Location(db.Model, UserMixin):
    city = db.Column(db.String(20), default='')
    country = db.Column(db.String(20), default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)

    def __repr__(self):
        return f"Location('{self.city}', '{self.country}')"


from forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm,  LocationForm, UpdatePasswordForm


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('newsfeed'))
    form = LoginForm()
    if form.validate_on_submit():
        new_user = User.query.filter_by(email=form.email.data).first()
        if new_user and bcrypt.check_password_hash(new_user.password, form.password.data):
            login_user(new_user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successfully', 'success')
            return redirect(next_page) if next_page else redirect(url_for('newsfeed'))
        else:
            flash('Login Failed', 'danger')
    return render_template('Login.html', title='Login', form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('newsfeed'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(fname=form.fname.data, email=form.email.data, password=hashed_password, phone=form.phone.data)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Account created Successfully {form.fname.data}', 'success')
        return redirect(url_for('login'))
    return render_template('SignUp.html', title='SignUp', form=form)


@app.route('/newsfeed', methods=['GET', 'POST'])
@login_required
def newsfeed():
    form = UpdateAccountForm()
    return render_template('newsfeed.html', title='Newsfeed', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/timeline')
@login_required
def timeline():
    return render_template('timeline.html', title='Timeline')


@app.route('/messages')
def messages():
    return render_template('newsfeed-messages.html', title='Messages')


@app.route('/friends')
def friends():
    return render_template('newsfeed-friends.html', title='Friends')


@app.route('/images')
def images():
    return render_template('newsfeed-images.html', title='Images')


@app.route('/videos')
def videos():
    return render_template('newsfeed-videos.html', title='Videos')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/users', picture_fn)
    form_picture.save(picture_path)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    form = UpdateAccountForm()
    form2 = LocationForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.fname = form.fname.data
        current_user.lname = form.lname.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash(f'Personal Details Successfully Updated', 'success')
        return redirect(url_for('editprofile'))
    elif request.method == 'GET':
        form.fname.data = current_user.fname
        form.lname.data = current_user.lname
        form.email.data = current_user.email
        form.phone.data = current_user.phone
    image_file = url_for('static', filename='images/users/' + current_user.image_file)
    return render_template('Edit Profile.html', title='Account', image_file=image_file, form=form, form2=form2)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f''' To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be done. 
'''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return  redirect(url_for('login'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An Email has been send with instructions of password reset')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or Expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been update!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form, title='Reset Token')


@app.route('/editpassword', methods=['GET', 'POST'])
@login_required
def editpassword():
    form2 = RegistrationForm()
    form = UpdatePasswordForm()
    user = User.query.filter_by(email=current_user.email).first()
    if form.validate_on_submit():
        temp = user.password
        flag = bcrypt.check_password_hash(temp, form.oldPassword.data)
        if flag:
            hashed_password = bcrypt.generate_password_hash(form.newPassword.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash(f'Your password has been update!', 'success')
            return redirect(url_for('editpassword'))
        elif request.method == 'GET':
            flash(f'Your password has not been changed!', 'danger')
            return redirect(url_for('editpassword'))
    return render_template('EditPassword.html', form=form, title='Edit Password')


if __name__ == "__main__":
    app.run(debug=True)
