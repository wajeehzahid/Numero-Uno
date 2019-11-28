import uuid
from typing import Tuple
from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from flask_socketio import SocketIO
from pusher import Pusher
from sqlalchemy import PrimaryKeyConstraint
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user, login_required
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:Qwerty!99@localhost/social_network'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
socketio = SocketIO(app)
pusher = Pusher(
    app_id='905427',
    key='ae6357ab6525e913a329',
    secret='cd36ff6a2322acf2c407',
    cluster='ap2',
    ssl=True
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    user_id = db.Column(db.BIGINT, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), default='')
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    Post = db.relationship('Post', backref="author", lazy=True)

    def __repr__(self):
        return f"User('{self.fname}', '{self.lname}' '{self.email}', '{self.phone}', '{self.image_file}')"


class Location(db.Model, UserMixin):
    location_id = db.Column(db.BIGINT, primary_key=True, autoincrement=True, nullable=False)
    city = db.Column(db.String(20), default='')
    country = db.Column(db.String(20), default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __repr__(self):
        return f"Location('{self.city}', '{self.country}')"


class Post(db.Model):
    post_id = db.Column(db.BIGINT, primary_key=True, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.BIGINT, db.ForeignKey('user.user_id'),
                        nullable=False)
    likes = db.Column(db.BIGINT, nullable=False, default=0)

    def __repr__(self):
        return f"Posts('{self.title}', '{self.date_posted}')"


class Likes(db.Model):
    user_id = db.Column(db.BIGINT, db.ForeignKey('user.user_id'),
                        nullable=False)
    post_id = db.Column(db.BIGINT, db.ForeignKey('post.post_id'),
                        nullable=False)
    __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'post_id', name='user_post'),)


class Friends(db.Model):
    user_id = db.Column(db.BIGINT, db.ForeignKey('user.user_id'),
                        nullable=False)
    friend_id = db.Column(db.BIGINT, db.ForeignKey('user.user_id'),
                          nullable=False)
    __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'friend_id', name='user_friend'),)


class Messages(db.Model):
    message_id = db.Column(db.BIGINT, nullable=False, autoincrement=True, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id_from = db.Column(db.BIGINT, db.ForeignKey('user.user_id'),
                             nullable=False)
    user_id_to = db.Column(db.BIGINT, db.ForeignKey('user.user_id'),
                           nullable=False)


class Comments(db.Model):
    comment_id = db.Column(db.BIGINT, nullable=False, autoincrement=True, primary_key=True)
    user_id = db.Column(db.BIGINT, db.ForeignKey('user.user_id'),
                        nullable=False)
    post_id = db.Column(db.BIGINT, db.ForeignKey('post.post_id'),
                        nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


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
        new_user = User(fname=form.fname.data, lname=form.lname.data, email=form.email.data, password=hashed_password,
                        phone=form.phone.data)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Account created Successfully {form.fname.data}', 'success')
        return redirect(url_for('login'))
    return render_template('SignUp.html', title='SignUp', form=form)


@app.route('/newsfeed', methods=['GET', 'POST'])
@login_required
def newsfeed():
    posts = Post.query.all()
    return render_template('newsfeed.html', posts=posts)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/timeline')
@login_required
def timeline():
    return render_template('timeline.html', title='Timeline')


@app.route('/post', methods=['GET', 'POST'])
def addPost():
    data = {
        'id': "post-{}".format(uuid.uuid4().hex),
        'name': request.form.get('name'),
        'content': request.form.get('content'),
        'likes': 0,
        'status': 'active',
        'event_name': 'created'
    }
    post = Post(date_posted=datetime.now(), content=data.get('content'), user_id=11111, likes=0)
    db.session.add(post)
    db.session.commit()
    pusher.trigger("blog", "post-added", data)
    jsonify(data)


@app.route('/messages')
def messages():
    return render_template('newsfeed-messages.html', title='Messages')


# update or delete post
@app.route('/post/<id>', methods=['PUT', 'DELETE'])
def updatePost(id):
    data = {'id': id}
    if request.method == 'DELETE':
        data['event_name'] = 'deleted'
        pusher.trigger("blog", "post-deleted", data)
    else:
        data['event_name'] = 'deactivated'
        pusher.trigger("blog", "post-deactivated", data)
    return jsonify(data)


@app.route('/friends')
def friends():
    return render_template('newsfeed-friends.html', title='Friends')


@app.route('/chat')
def chat():
    messages = Messages.query.all()
    return render_template('newsfeed-messages.html', messages=messages)


@app.route('/images')
def images():
    return render_template('newsfeed-images.html', title='Images')


def messageReceived():
    print('message was received!!!')


@app.route('/videos')
def videos():
    return render_template('newsfeed-videos.html', title='Videos')


@socketio.on('my message')
def handle_my_custom_event(json):
    print('received message: ' + str(json))
    message = Messages(content=json['message'], date_created=datetime.now(), user_id_from=11111, user_id_to=22222)
    db.session.add(message)
    db.session.commit()
    socketio.emit('my response', json, callback=messageReceived)


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
    app.run(debug=True, host='0.0.0.0', port='5000')
