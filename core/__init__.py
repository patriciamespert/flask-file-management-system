from flask import Flask, render_template, request, redirect, url_for
from flask.templating import render_template
from flask_login.utils import login_required
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Database
db = SQLAlchemy()

def create_app(config_obj=None):
    # Instantiation
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/patri/Documents/Flask/flask-file-management-system/login.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'thisissecret'

    
    db.init_app(app)

    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(30), unique=True)


    # Initialization
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    with app.app_context():
        db.create_all()

    #login_manager

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/signup')
    def signup():
        return render_template('signup.html')

    @app.route('/signup', methods=['POST'])
    def signup_post():
        username = request.form.get('username')

        user = User.query.filter_by(username=username).first() # if this returns a user, then the email already exists in database

        if user: # if a user is found, we want to redirect back to signup page so user can try again
            return redirect(url_for('signup'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(username=username)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    @app.route('/login')
    def login():
        return render_template('login.html')

    @app.route('/logmein', methods=['POST'])
    def logmein():
        username = request.form['username']

        user  = User.query.filter_by(username=username).first()

        print(user)

        if not user:
            return '<h1>User not found!</h1>'
        else:
            login_user(user)
            return '<h1>You are now logged in!</h1>'


    @app.route('/logout', methods=['GET'])
    @login_required
    def logout():  
        """Logout the current user."""
        user = current_user
        user.authenticated = False
        db.session.add(user)
        db.session.commit()
        logout_user()
        return 'You are now logged out!'

    @app.route('/home')
    @login_required
    def home():
        return 'The current user is {}'.format(current_user.username)
    
    return app



