from flask import Flask
from flask_login.utils import login_required
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/patri/Documents/Flask/flask-file-management-system/login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)

db.create_all()

#login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#routes
@app.route('/')
def index():
    user = User.query.filter_by(username='patricia').first()
    login_user(user)
    return 'You are now logged in!'

@app.route('/logout')
@login_required
def logout():
    return 'You are now logged out!'

@app.route('/home')
@login_required
def home():
    return 'The current user is {}'.format(current_user.username)

if __name__ == '__main__':
    app.run(debug=True)