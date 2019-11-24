import uuid
from typing import Tuple
from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from flask_socketio import SocketIO
from pusher import Pusher
from sqlalchemy import PrimaryKeyConstraint
from datetime import datetime
from forms import RegistrationForm, LoginForm, PostForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/socialnetworking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)
pusher = Pusher(
    app_id='905427',
    key='ae6357ab6525e913a329',
    secret='cd36ff6a2322acf2c407',
    cluster='ap2',
    ssl=True
)


class Users(db.Model):
    user_id = db.Column(db.BIGINT, primary_key=True, nullable=False, autoincrement=True, )
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_picture_url = db.Column(db.String(255), nullable=False, default='/static/images'
                                                                            '/default.png')
    Posts = db.relationship('Posts', backref='author', lazy=True)

    def __repr__(self):
        return f"Users('{self.username}', '{self.email}', '{self.image_file}')"


class Posts(db.Model):
    post_id = db.Column(db.BIGINT, primary_key=True, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
                        nullable=False)
    likes = db.Column(db.BIGINT, nullable=False, default=0)

    def __repr__(self):
        return f"Posts('{self.title}', '{self.date_posted}')"


class Likes(db.Model):
    user_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
                        nullable=False)
    post_id = db.Column(db.BIGINT, db.ForeignKey('posts.post_id'),
                        nullable=False)
    __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'post_id', name='user_post'),)


class Friends(db.Model):
    user_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
                        nullable=False)
    friend_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
                          nullable=False)
    __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'friend_id', name='user_friend'),)


class Messages(db.Model):
    message_id = db.Column(db.BIGINT, nullable=False, autoincrement=True, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id_from = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
                             nullable=False)
    user_id_to = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
                           nullable=False)


class Comments(db.Model):
    comment_id = db.Column(db.BIGINT, nullable=False, autoincrement=True, primary_key=True)
    user_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
                        nullable=False)
    post_id = db.Column(db.BIGINT, db.ForeignKey('posts.post_id'),
                        nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@app.route("/")
def root():
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('newsfeed'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('Login.html', title='Login', form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.name.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('SignUp.html', title='SignUp', form=form)


@app.route('/newsfeed')
def newsfeed():
    posts = Posts.query.all()
    return render_template('newsfeed.html', posts=posts)


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
    post = Posts(date_posted=datetime.now(), content=data.get('content'), user_id=11111, likes=0)
    db.session.add(post)
    db.session.commit()
    pusher.trigger("blog", "post-added", data)
    jsonify(data)


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


@app.route('/chat')
def chat():
    messages = Messages.query.all()
    return render_template('newsfeed-messages.html', messages=messages)


def messageReceived():
    print('message was received!!!')


@socketio.on('my message')
def handle_my_custom_event(json):
    print('received message: ' + str(json))
    message = Messages(content=json['message'], date_created=datetime.now(), user_id_from=11111, user_id_to=22222)
    db.session.add(message)
    db.session.commit()
    socketio.emit('my response', json, callback=messageReceived)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
