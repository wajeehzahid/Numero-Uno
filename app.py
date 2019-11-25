from flask import Flask, render_template, url_for, flash, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user, login_required
from flask_bcrypt import Bcrypt


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

    def __repr__(self):
        return f"User('{self.fname}', '{self.lname}' '{self.email}', '{self.phone}', '{self.image_file}')"

class Location(db.Model, UserMixin):
    city = db.Column(db.String(20), default='')
    country = db.Column(db.String(20), default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)

    def __repr__(self):
        return f"Location('{self.city}', '{self.country}')"


from forms import RegistrationForm, LoginForm, UpdateAccountForm, LocationForm


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
    return render_template('newsfeed.html', title='Newsfeed')


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


@app.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    form = UpdateAccountForm()
    form2 = LocationForm()
    if form.validate_on_submit():
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


@app.route('/editpassword')
def editpassword():
    return render_template('EditPassword.html')


if __name__ == '__main__':
    app.run(debug=True)
