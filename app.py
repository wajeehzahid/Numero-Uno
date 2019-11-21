from flask import Flask, render_template, url_for, flash, redirect
from flask_socketio import SocketIO
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/demo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)


# class Database:
#     def __init__(self):
#         host = "127.0.0.1"
#         user = "test"
#         password = "password"
#         db = "employees"
#         self.con = pymysql.connect(host=host, user=user, password=password, db=db, cursorclass=pymysql.cursors.
#                                    DictCursor)
#         self.cur = self.con.cursor()
#
#     def list_employees(self):
#         self.cur.execute("SELECT first_name, last_name, gender FROM employees LIMIT 50")
#         result = self.cur.fetchall()
#

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
    return render_template('newsfeed-messages.html')


def messageReceived():
    print('message eas received!!!')


@socketio.on('my event')
def handle_my_custom_event(json):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
