from flask import Flask, render_template, url_for, flash, redirect
from flask_socketio import SocketIO
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password''@localhost/socialnetworking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
socialnetworking = SQLAlchemy(app)
socketio = SocketIO(app)


class Users(socialnetworking.Model):
    user_id = socialnetworking.Column(socialnetworking.BIGINT, primary_key=True, nullable=False, autoincrement=True, )
    name = socialnetworking.Column(socialnetworking.String(50), nullable=False)
    email = socialnetworking.Column(socialnetworking.String(255), unique=True, nullable=False)
    password = socialnetworking.Column(socialnetworking.String(255), nullable=False)
    profile_picture_url = socialnetworking.Column(socialnetworking.String(255), nullable=False, default='')
    Posts = socialnetworking.relationship('Posts', backref='author', lazy=True)

    def __repr__(self):
        return f"Users('{self.username}', '{self.email}', '{self.image_file}')"


class Posts(socialnetworking.Model):
    post_id = socialnetworking.Column(socialnetworking.BIGINT, primary_key=True, nullable=False)
    date_posted = socialnetworking.Column(socialnetworking.DateTime, nullable=False, default=datetime.utcnow)
    content = socialnetworking.Column(socialnetworking.Text, nullable=False)
    user_id = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('users.user_id'),
                                      nullable=False)

    def __repr__(self):
        return f"Posts('{self.title}', '{self.date_posted}')"


class Messages(socialnetworking.Model):
    message_id = socialnetworking.Column(socialnetworking.BIGINT, nullable=False, autoincrement=True, primary_key=True)
    content = socialnetworking.Column(socialnetworking.Text, nullable=False)
    date_created = socialnetworking.Column(socialnetworking.DateTime, nullable=False, default=datetime.utcnow)
    user_id_from = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('users.user_id'),
                                           nullable=False)
    user_id_to = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('users.user_id'),
                                         nullable=False)


@app.route("/")
def root():
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('chat'))
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


@app.route('/newsfeed', methods=['GET', 'POST'])
def newsfeed():
    return "NEWSFEED"


@app.route('/chat')
def chat():
    messages = Messages.query.all()
    return render_template('newsfeed-messages.html', messages=messages)


def messageReceived():
    print('message eas received!!!')


@socketio.on('my message')
def handle_my_custom_event(json):
    print('received message: ' + str(json))
    message = Messages(content=json['message'], date_created=datetime.now(), user_id_from=11111, user_id_to=22222)
    socialnetworking.session.add(message)
    socialnetworking.session.commit()
    socketio.emit('my response', json, callback=messageReceived)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
