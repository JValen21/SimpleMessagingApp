from curses import flash
from flask import g
from datetime import datetime
from http import HTTPStatus
import secrets
from flask import Flask, abort, request, send_from_directory, make_response, render_template, session
from werkzeug.datastructures import WWWAuthenticate
import flask
from forms import *
from base64 import b64decode
from apsw import Error
from threading import local
import dbManager

tls = local()
inject = "'; insert into messages (sender,message) values ('foo', 'bar');select '"

# Set up app
app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True, #The HttpOnly flag set to True prevents any client-side usage of the session cookie
    REMEMBER_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="lax", #We prevent cookies from being sent from any external requests by setting SESSION_COOKIE_SAMESITE to lax
)
# The secret key enables storing encrypted session data in a cookie (make a secure random key for this!)
app.secret_key = secrets.token_hex(16)


from security import *
from resources import *

# Add a login manager to the app
import flask_login
from flask_login import login_required, login_user, logout_user, current_user
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"


# Class to store user info
# UserMixin provides us with an `id` field and the necessary
# methods (`is_authenticated`, `is_active`, `is_anonymous` and `get_id()`)
class User(flask_login.UserMixin):
    pass
    
# This method is called whenever the login manager needs to get
# the User object for a given user id
@login_manager.user_loader
def user_loader(user_id):
    
    # For a real app, we would load the User from a database or something
    user = User()
    user.id = user_id
    return user

@app.route('/index.js')
def index_js():
    return send_from_directory(app.root_path, 'static/index.js', mimetype='text/javascript')

@app.route('/index.css')
def index_css():
    return send_from_directory(app.root_path, 'static/index.css', mimetype='text/css')

################################################################################################
################################################################################################

@app.route('/')
@app.route('/index.html')
@login_required
def index_html():
    return render_template("index.html", minetype='text/html')
    #return send_from_directory(app.root_path,
                        #'index.html', mimetype='text/html')

#Creating a new user in the system:
#Redirects to the login page if you successfully create a new user, if not, the page reloads.     
@app.route('/createUser', methods=["GET", "POST"])
def createUser():
    form = CreateUserForm()
    if form.is_submitted():
        print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')
        print(request.form)
    if form.validate_on_submit():
        #username = form.username.data
        #psw = form.password.data
        #pswRepeated = form.repeatPassword.data
        username = request.form["username"]
        psw = request.form["psw"]
        pswRepeated = request.form["psw-repeat"]
        try: 
            pswTuple = dbManager.hashPassword(psw) 
            pswHashed = pswTuple[0]
            salt = pswTuple[1]
            if (dbManager.usernameExists(username) or dbManager.wrongPassword(psw, pswRepeated)):
                return flask.redirect(flask.url_for('createUser', form = form))
            else:
                dbManager.createUser(username, pswHashed, salt)
            
                next = flask.request.args.get('next')
                
                if not is_safe_url(next):
                    return flask.abort(400)
                return flask.redirect(next or flask.url_for('login'))
            
        except Error as e:
            return f'ERROR: {e}'  
    return render_template("createUser.html", form = form)


################################## Functions for the login and logout process #################################


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if request.method == 'GET':
        return render_template('./login.html', form=form)
        
    if request.method == 'POST': 
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            session['user'] = username
            try: 
                isValid = dbManager.check_password(username, password) # and check_password(u.password, password)
            except IndexError as e:
                return render_template('./login.html', form=form)  
            if(isValid):
                user = user_loader(username)
                # automatically sets logged in session cookie
                session['logged_in'] = True
                login_user(user, remember=False)
        
                flask.flash('Logged in successfully.')
                next = flask.request.args.get('next')
                
                # is_safe_url checks if the url is safe for redirects.
                if not is_safe_url(next):
                    return flask.abort(400)

                return flask.redirect(next or flask.url_for('index_html'))              
    return render_template('./login.html', form=form)

#Logout funciton:
@app.route('/logout')
@login_required
def logout():
    print("Gets here")
    logout_user()
    session.pop('user', None)
    
    next = flask.request.args.get('next')
    if not is_safe_url(next):
                    return flask.abort(400)
                           
    return flask.redirect(flask.url_for('login')) 

from messaging import *

