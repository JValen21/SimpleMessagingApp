from curses import flash
import datetime
from http import HTTPStatus
import re
import unicodedata
from flask import Flask, abort, request, send_from_directory, make_response, render_template, session, url_for
from urlparse import urlparse, urljoin
from werkzeug.datastructures import WWWAuthenticate
import flask
from login_form import LoginForm
from createUser_form import CreateUserForm
from json import dumps, loads
from base64 import b64decode
import sys
import apsw
import jwt
from apsw import Error
from pygments import highlight
from pygments.lexers import SqlLexer
from pygments.formatters import HtmlFormatter
from pygments.filters import NameHighlightFilter, KeywordCaseFilter
from pygments import token;
from threading import local
from markupsafe import escape
from database import * 
from flask_wtf.csrf import CSRFProtect



tls = local()
inject = "'; insert into messages (sender,message) values ('foo', 'bar');select '"
cssData = HtmlFormatter(nowrap=True).get_style_defs('.highlight')
conn = None

conn = initDatabase() #Initialize the databse. 

# Set up app
app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True, #The HttpOnly flag set to True prevents any client-side usage of the session cookie
    REMEMBER_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict", #We also prevented cookies from being sent from any external requests by setting SESSION_COOKIE_SAMESITE to Strict

)


# The secret key enables storing encrypted session data in a cookie (make a secure random key for this!)
app.secret_key = secrets.token_hex(16)


# Add a login manager to the app
import flask_login
from flask_login import login_required, login_user, logout_user, current_user
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"


csrf = CSRFProtect() #CSRF attack protection.
csrf.init_app(app)


users = {'alice' : {'password' : 'password123', 'token' : 'tiktok'}, #Dårlig
         'Bob' : {'password' : 'bananas'}
         }

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

#A function that ensures that a redirect target will lead to the same server:
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

# This method is called to get a User object based on a request,
# for example, if using an api key or authentication token rather
# than getting the user name the standard way (from the session cookie)
@login_manager.request_loader
def request_loader(request):
    # Even though this HTTP header is primarily used for *authentication*
    # rather than *authorization*, it's still called "Authorization".
    auth = request.headers.get('Authorization')

    # If there is not Authorization header, do nothing, and the login
    # manager will deal with it (i.e., by redirecting to a login page)
    if not auth:
        return

    (auth_scheme, auth_params) = auth.split(maxsplit=1)
    auth_scheme = auth_scheme.casefold()
    if auth_scheme == 'basic':  # Basic auth has username:password in base64
        (uid,passwd) = b64decode(auth_params.encode(errors='ignore')).decode(errors='ignore').split(':', maxsplit=1)
        print(f'Basic auth: {uid}:{passwd}')
        u = users.get(uid)
        if u: # and check_password(u.password, passwd):
            return user_loader(uid)
    elif auth_scheme == 'bearer': # Bearer auth contains an access token;
        # an 'access token' is a unique string that both identifies
        # and authenticates a user, so no username is provided (unless
        # you encode it in the token – see JWT (JSON Web Token), which
        # encodes credentials and (possibly) authorization info)
        print(f'Bearer auth: {auth_params}')
        for uid in users:
            if users[uid].get('token') == auth_params:
                return user_loader(uid)
    # For other authentication schemes, see
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication

    # If we failed to find a valid Authorized header or valid credentials, fail
    # with "401 Unauthorized" and a list of valid authentication schemes
    # (The presence of the Authorized header probably means we're talking to
    # a program and not a user in a browser, so we should send a proper
    # error message rather than redirect to the login page.)
    # (If an authenticated user doesn't have authorization to view a page,
    # Flask will send a "403 Forbidden" response, so think of
    # "Unauthorized" as "Unauthenticated" and "Forbidden" as "Unauthorized")
    abort(HTTPStatus.UNAUTHORIZED, www_authenticate = WWWAuthenticate('Basic realm=inf226, Bearer'))

def pygmentize(text):
    if not hasattr(tls, 'formatter'):
        tls.formatter = HtmlFormatter(nowrap = True)
    if not hasattr(tls, 'lexer'):
        tls.lexer = SqlLexer()
        tls.lexer.add_filter(NameHighlightFilter(names=['GLOB'], tokentype=token.Keyword))
        tls.lexer.add_filter(NameHighlightFilter(names=['text'], tokentype=token.Name))
        tls.lexer.add_filter(KeywordCaseFilter(case='upper'))
    return f'<span class="highlight">{highlight(text, tls.lexer, tls.formatter)}</span>'

@app.route('/favicon.ico')
def favicon_ico():
    return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/favicon.png')
def favicon_png():
    return send_from_directory(app.root_path, 'favicon.png', mimetype='image/png')

@app.route('/index.js')
def index_js():
    return send_from_directory(app.root_path, 'index.js', mimetype='text/javascript')

@app.route('/index.css')
def index_css():
    return send_from_directory(app.root_path, 'index.css', mimetype='text/css')

################################################################################################
################################################################################################

@app.route('/')
@app.route('/index.html')
@login_required
def index_html():
    return render_template("index.html", minetype='text/html')
    #return send_from_directory(app.root_path,
                        #'index.html', mimetype='text/html')


#Add CSP header:
@app.after_request
def add_security_headers(resp):
    resp.headers['Content-Security-Policy']='default-src \'self\''
    return resp

################################# Functions for the createUser process ###############################

#Function for generating hashed passwords with salt. 
#Returns a tuple with the hashed password and the salt.
def hashPassword(password):
    salt = secrets.token_hex(16) #Add salt
    dataBase_password = password + salt
    # Hashing the password
    hashed = hashlib.sha512(dataBase_password.encode())
    return (hashed.hexdigest(), salt)
   

#A function that checks if a username already exists in the database.
#Returns true if the username existst in the database.
def usernameExists(username): 
    isInDatabase = False
    c = conn.execute('SELECT username FROM users').fetchall()
    if (username,) in c:
        isInDatabase = True
    return isInDatabase   

#Check if we write correct password twice and that its at least 12 characters long.
#Returns true if its something wrong with the password.
def wrongPassword(psw, pswRepeated):
    #Password must be typed correct twice and be longer than 12 characters. Return true if not. 
    return(psw != pswRepeated or len(psw) < 12)
    

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
            pswTuple = hashPassword(psw) 
            pswHashed = pswTuple[0]
            salt = pswTuple[1]
            if (usernameExists(username) or wrongPassword(psw, pswRepeated)):
                return flask.redirect(flask.url_for('createUser', form = form))
            else:
                conn.execute('INSERT INTO users (username, password, salt) VALUES (?, ?, ?)', (username, pswHashed, salt))
            
                next = flask.request.args.get('next')
                
                if not is_safe_url(next):
                    return flask.abort(400)
                return flask.redirect(next or flask.url_for('login'))
            
        except Error as e:
            return f'ERROR: {e}'  
    return render_template("createUser.html", form = form)


################################## Functions for the login process #################################

#Returns hashed password with salt so that we can check if provided password is the same as we have in the database.
def checkHashedPassword(password, salt):
    dataBase_password = password + salt
    return hashlib.sha512(dataBase_password.encode()).hexdigest()
   

#Function to check that the username and password entered is correct in the login process:
def check_password(username, password):
    dataBase_Password = conn.execute('SELECT password FROM users WHERE username=?', (username,)).fetchall()[0][0]
    salt = conn.execute('SELECT salt FROM users WHERE username=?', (username,)).fetchall()[0][0]
    password = checkHashedPassword(password, salt)
    return (password == dataBase_Password)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if request.method == 'GET':
        return render_template('./login.html', form=form)
        
    if request.method == 'POST': 
        if form.is_submitted():
            print(f'Received form: {"invalid" if not form.validate() else "valid"} {form.form_errors} {form.errors}')
            print(request.form)
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            session['username'] = username
            try: 
                isValid = check_password(username, password) # and check_password(u.password, password)
            except IndexError as e:
                return render_template('./login.html', form=form)  
            if(isValid):
                user = user_loader(username)
                # automatically sets logged in session cookie
                session['logged_in'] = True
                login_user(user)
        
                flask.flash('Logged in successfully.')
                next = flask.request.args.get('next')
                # is_safe_url should check if the url is safe for redirects.
                # See http://flask.pocoo.org/snippets/62/ for an example.
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
    session.pop('username', None)
                
    return flask.redirect(flask.url_for('login')) 

#Make user log out after 20 minutes of inactivity:
@app.before_request
def before_request():
    flask.session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=1)
    flask.session.modified = True

################################# Messaging system #################################

@app.get('/showInbox')
def showInbox():
    #query = request.args.get('q') or request.form.get('q') or '*'
    receiver = request.args.get('sender') or request.form.get('sender')
    stmt = f"SELECT * FROM messages WHERE receiver = '{receiver}'"
    result = f"Query: {pygmentize(stmt)}\n"
    try:
        #c = conn.execute(stmt)
        c = conn.execute('SELECT * FROM messages WHERE receiver=?', (receiver,)) #Prepared statement to avoid sql injection. 
        rows = c.fetchall()
        result = result + 'You have '+ str(len(rows)) + ' messages:\n'
        for row in rows:
            result = f'{result}    {dumps(row)}\n'
        c.close()
        return result
    except Error as e:
        return f'ERROR: {e}'

@app.route('/send', methods=['POST','GET'])
def send():
    try:
        sender = request.args.get('sender') or request.form.get('sender')
        message = request.args.get('message') or request.args.get('message')
        receiver = request.args.get('receiver') or request.args.get('receiver')
        if not sender or not message or not receiver:
            return f'ERROR: missing sender, message or receiver'
        #Fixing SQL injection vulnerability:
        conn.execute('INSERT INTO messages (sender, message, receiver) VALUES (?, ?, ?)', (sender, message, receiver))
        return f'ok'
    except Error as e:
        return f'ERROR: {e}'
    
        #Previous code:
        #stmt = f"INSERT INTO messages (sender, message) values ('{sender}', '{message}');"
        #result = f"Query: {pygmentize(stmt)}\n"
        #conn.execute(stmt)
        #return f'{result}ok'
    #except Error as e:
     #   return f'{result}ERROR: {e}'

@app.get('/announcements')
def announcements():
    try:
        stmt = f"SELECT author,text FROM announcements;"
        c = conn.execute(stmt)
        anns = []
        for row in c:
            anns.append({'sender':escape(row[0]), 'message':escape(row[1])})
        return {'data':anns}
    except Error as e:
        return {'error': f'{e}'}

@app.get('/coffee/')
def nocoffee():
    abort(418)

@app.route('/coffee/', methods=['POST','PUT'])
def gotcoffee():
    return "Thanks!"

@app.get('/highlight.css')
def highlightStyle():
    resp = make_response(cssData)
    resp.content_type = 'text/css'
    return resp




