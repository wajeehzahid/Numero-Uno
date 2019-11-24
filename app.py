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
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:Qwerty!99@localhost/social_network'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
social_network = SQLAlchemy(app)
socketio = SocketIO(app)
pusher = Pusher(
    app_id='905427',
    key='ae6357ab6525e913a329',
    secret='cd36ff6a2322acf2c407',
    cluster='ap2',
    ssl=True
)


class Users(social_network.Model):
    user_id = social_network.Column(social_network.BIGINT, primary_key=True, nullable=False, autoincrement=True, )
    name = social_network.Column(social_network.String(50), nullable=False)
    email = social_network.Column(social_network.String(255), unique=True, nullable=False)
    password = social_network.Column(social_network.String(255), nullable=False)
    profile_picture_url = social_network.Column(social_network.String(255), nullable=False, default='/static/images'
                                                                                                    '/default.png')
    Posts = social_network.relationship('Posts', backref='author', lazy=True)

    def __repr__(self):
        return f"Users('{self.username}', '{self.email}', '{self.image_file}')"


class Posts(social_network.Model):
    post_id = social_network.Column(social_network.BIGINT, primary_key=True, nullable=False)
    date_posted = social_network.Column(social_network.DateTime, nullable=False, default=datetime.utcnow)
    content = social_network.Column(social_network.Text, nullable=False)
    user_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
                                    nullable=False)

    def __repr__(self):
        return f"Posts('{self.title}', '{self.date_posted}')"


class Likes(social_network.Model):
    user_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
                                    nullable=False)
    post_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('posts.post_id'),
                                    nullable=False)
    __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'post_id', name='user_post'),)


class Friends(social_network.Model):
    user_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
                                    nullable=False)
    friend_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
                                      nullable=False)
    __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'friend_id', name='user_friend'),)


class Messages(social_network.Model):
    message_id = social_network.Column(social_network.BIGINT, nullable=False, autoincrement=True, primary_key=True)
    content = social_network.Column(social_network.Text, nullable=False)
    date_created = social_network.Column(social_network.DateTime, nullable=False, default=datetime.utcnow)
    user_id_from = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
                                         nullable=False)
    user_id_to = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
                                       nullable=False)


class Comments(social_network.Model):
    comment_id = social_network.Column(social_network.BIGINT, nullable=False, autoincrement=True, primary_key=True)
    user_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
                                    nullable=False)
    post_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('posts.post_id'),
                                    nullable=False)
    content = social_network.Column(social_network.Text, nullable=False)
    date_posted = social_network.Column(social_network.DateTime, nullable=False, default=datetime.utcnow)


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
    return render_template('newsfeed.html')


@app.route('/post', methods=['GET', 'POST'])
def addPost():
    data = {
        'id': "post-{}".format(uuid.uuid4().hex),
        'name': request.form.get('name'),
        'content': request.form.get('content'),
        'status': 'active',
        'event_name': 'created'
    }
    post = Posts(date_posted=datetime.now(), content=data.get('content'))
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
    return render_template('newsfeed-messages.html')


def messageReceived():
    print('message was received!!!')


@socketio.on('my message')
def handle_my_custom_event(json):
    print('received message: ' + str(json))
    message = Messages(content=json['message'], date_created=datetime.now(), user_id_from=11111, user_id_to=22222)
    social_network.session.add(message)
    social_network.session.commit()
    socketio.emit('my response', json, callback=messageReceived)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
