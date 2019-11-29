import os
import uuid
from typing import Tuple

from flask_openid import OpenID
from flask import Flask, render_template, url_for, flash, redirect, request, jsonify, g, session
from flask_socketio import SocketIO
from pusher import Pusher
from sqlalchemy import PrimaryKeyConstraint
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user, login_required
from flask_bcrypt import Bcrypt

basedir = os.path.abspath(os.path.dirname(__file__))
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
oid = OpenID(app, os.path.join(basedir, 'tmp'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


class Friends(db.Model):
    user_id = db.Column(db.BIGINT, db.ForeignKey('user.user_id'),
                        nullable=False)
    friend_id = db.Column(db.BIGINT, db.ForeignKey('user.user_id'),
                          nullable=False)
    __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'friend_id', name='user_friend'),)


class User(db.Model, UserMixin):
    user_id = db.Column(db.BIGINT, primary_key=True)
    fname = db.Column(db.String(20), nullable=False)
    lname = db.Column(db.String(20), default='')
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    image_file = db.Column(db.String(250), nullable=False, default="{{ url_for('static', "
                                                                   "filename='images/default.png') }}")
    Post = db.relationship('Post', backref="author", lazy=True)

    friend = db.relationship('User', secondary=Friends.__table__,
                             primaryjoin=(Friends.user_id == user_id),
                             secondaryjoin=(Friends.friend_id == user_id),
                             backref=db.backref('Friends', lazy='dynamic'),
                             lazy='dynamic')

    def get_id(self):
        return self.user_id

    def addFriend(self, user):
        if not self.is_friend(user):
            self.friend.append(user)
            return self

    def removeFriend(self, user):
        if self.is_friend(user):
            self.friend.remove(user)
            return self

    def is_friend(self, user):
        return self.friend.filter(Friends.friend_id == user.user_id).count() > 0

    def friend_posts(self):
        return Post.query.join(Friends, (Friends.friend_id == Post.user_id)).filter(
            Friends.user_id == self.id).order_by(Post.date_posted.desc())

    def __repr__(self):
        return f"User('{self.fname}', '{self.lname}' '{self.email}', '{self.phone}', '{self.image_file}')"


class Location(db.Model, UserMixin):
    location_id = db.Column(db.BIGINT, primary_key=True, autoincrement=True, nullable=False)
    city = db.Column(db.String(20), default='')
    country = db.Column(db.String(20), default='')
    user_id = db.Column(db.BIGINT, db.ForeignKey('user.user_id'), nullable=False)

    def __repr__(self):
        return f"Location('{self.city}', '{self.country}')"


class Post(db.Model):
    post_id = db.Column(db.BIGINT, primary_key=True, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.BIGINT, db.ForeignKey('user.user_id'),
                        nullable=False)
    likes = db.Column(db.BIGINT, nullable=False, default=0)

    # def get_name(self):
    #     return Post.query

    def __repr__(self):
        return f"Posts('{self.title}', '{self.date_posted}')"


class Likes(db.Model):
    user_id = db.Column(db.BIGINT, db.ForeignKey('user.user_id'),
                        nullable=False)
    post_id = db.Column(db.BIGINT, db.ForeignKey('post.post_id'),
                        nullable=False)
    __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'post_id', name='user_post'),)


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
@oid.loginhandler
def login():
    if current_user.is_authenticated:
        return redirect(url_for('newsfeed'))
    form = LoginForm()
    if form.validate_on_submit():
        new_user = User.query.filter_by(email=form.email.data).first()
        if new_user is None:
            flash('Email not registered, Sign Up to get yourself registered.', 'danger')
        elif new_user and bcrypt.check_password_hash(new_user.password, form.password.data):
            login_user(new_user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('newsfeed'))
        else:
            flash('Incorrect password', 'danger')
    return render_template('login.html', title='Login', form=form)


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.addFriend(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('newsfeed'))


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
        flash(f'Account created Successfully {form.fname.data} {form.lname.data}', 'success')
        return redirect(url_for('login'))
    return render_template('SignUp.html', title='SignUp', form=form)


@app.route('/newsfeed')
@login_required
def newsfeed():
    posts = Post.query.all()
    users = User.query.limit(5).all()
    profile = User.query.get(g.user.get_id())
    return render_template('newsfeed.html', profile=profile, users=users, posts=posts)


@app.route('/add/<user_id>')
@login_required
def befriend(user_id):
    user = User.query.get(user_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('newsfeed'))
    if user == g.user:
        flash('You can\'t befriend yourself!')
        return redirect(url_for('newsfeed'))
    u = g.user.addFriend(user)
    if u is None:
        flash('Cannot be friends with this person')
        return redirect(url_for('newsfeed'))
    db.session.add(u)
    db.session.commit()
    flash('You are now friends with ' + user.fname + user.lname + '!', 'success')
    return redirect(url_for('newsfeed'))


@app.route('/unfriend/<user_id>')
@login_required
def unfriend(user_id):
    user = User.query.get(user_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('newsfeed'))
    if user == g.user:
        flash('You can\'t unfriend yourself!')
        return redirect(url_for('newsfeed'))
    u = g.user.removeFriend(user)
    if u is None:
        flash('Cannot unfriend this person')
        return redirect(url_for('newsfeed'))
    db.session.add(u)
    db.session.commit()
    flash('You are no longer friends with ' + user.fname + user.lname + '!', 'danger')
    return redirect(url_for('newsfeed'))


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
        'name': request.form.get('fname'),
        'content': request.form.get('content'),
        'likes': 0,
        'time': str(datetime.now()),
        'status': 'active',
        'event_name': 'created'
    }
    post = Post(date_posted=datetime.now(), content=data.get('content'), user_id=g.user.user_id)
    db.session.add(post)
    db.session.commit()
    pusher.trigger("blog", "post-added", data)
    return jsonify(data)


@app.route('/comment', methods=['GET', 'POST'])
def addComment(post_id):
    data = {
        'id': "comment-{}".format(uuid.uuid4().hex),
        'post_id': post_id,
        'name': request.form.get('fname'),
        'content': request.form.get('content'),
        'likes': 0,
        'time': str(datetime.now()),
        'status': 'active',
        'event_name': 'created'
    }
    post = Post(date_posted=datetime.now(), content=data.get('content'), user_id=g.user.user_id)
    db.session.add(post)
    db.session.commit()
    pusher.trigger("blog", "post-added", data)
    return jsonify(data)


# update or delete post
@app.route('/post/<id>', methods=['PUT', 'DELETE'])
def updatePost(id):
    data = {'id': id}
    if request.method == 'DELETE':
        data['event_name'] = 'deleted'
        post = Post.query.all()
        db.session.delete(post)
        db.session.commit()
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
    message = Messages(content=json['message'], date_created=datetime.now(), user_id_from=g.user.user_id,
                       user_id_to=2)
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
