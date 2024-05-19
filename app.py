'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, session, jsonify
from flask_socketio import SocketIO
import db
import secrets
from hashlib import sha256
from datetime import timedelta
import ssl
#hiii

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)
app.secret_key = "bob"

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
app.config['SESSION_COOKIE_HTTPONLY'] = True # ensire JavaScript cannot access the session cookie.

socketio = SocketIO(app)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    if not username.isalnum():
        return "Error: Invalid user"
    
    user =  db.get_user(username)
    if user is None:
        return "Error: User does not exist!"

    if user.password != password:
        return "Error: Password does not match!"

    session["user"] = username

    return url_for('home')
    
    # return url_for('home', username=username)

@app.route("/logout")
def logout():
    session.clear()  # clears session data
    return index()

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")
    
    if not username.isalnum() or len(username) > 12:
        return "Please only use letters or numbers for your username."
    
    if db.get_user(username) is None:
        db.insert_user(username, password)
        return url_for('home', username=username)
    return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

@app.route("/fetch_friends")
def fetch_friends(username: str):
    return db.get_friendships(username)

# home page, where the messaging app is
@app.route("/home")
def home():

    if "user" in session: 
        user = session["user"]
    else:
        return render_template("index.jinja")

    friends = db.get_friendships(user) # get friends
    requests = db.get_friend_requests(user) # get friend requests
    return render_template("home.jinja", username=user, friend_list = friends, requests=requests)

@app.route("/articles")
def articles():

    if "user" in session: 
        user = session["user"]
    else:
        return render_template("index.jinja")
          
    return render_template("articles.jinja", username=user)

@app.route("/account")
def account():

    if "user" in session: 
        user = session["user"]
    else:
        return render_template("index.jinja")
          
    return render_template("account.jinja", username=user)

@app.route("/friends")
def friends():

    if "user" in session: 
        user = session["user"]
    else:
        return render_template("index.jinja")
    
    friends = db.get_friendships(user) # get friends
    requests = db.get_friend_requests(user) # get friend requests

    return render_template("friends.jinja", username=user, friend_list = friends, requests=requests)

@app.route("/settings")
def settings():

    if "user" in session: 
        user = session["user"]
    else:
        return render_template("index.jinja")
          
    return render_template("settings.jinja", username=user)

@app.route("/articles/add_post", methods=["POST"])
def add_post():
    if not request.is_json:
        abort(404)

    username = request.json.get('username')
    title = request.json.get("title")
    content = request.json.get("content")

    # Check if title already exists
    if db.check_title(title):
        return "Error: Title already exists!"

    # Add the post
    db.add_post(username, title, content)

    return "Success!"

@app.route("/articles/edit_post", methods=["POST"])
def edit_post():
    if not request.is_json:
        abort(404)

    title = request.json.get("title")
    content = request.json.get("content")

    db.edit_post(title, content)
    return "Success!"


@app.route("/articles/delete_post", methods=["POST"])
def delete_post():
    if not request.is_json:
        abort(404)

    title = request.json.get("title")

    if not db.check_title(title):
        return "Error: Title does not exist!"

    db.delete_post(title)

    return f"Deleted post '{title}'"

@app.route("/articles/get_post_titles", methods=["GET"])
def get_post_titles():
    titles = db.get_post_titles()
    return titles

@app.route("/articles/get_post_content", methods=["POST"])
def get_post_content():
    if not request.is_json:
        abort(404)

    title = request.json.get("title")

    content = db.get_post_content(title)

    if content is None:
        return "Error: Title does not exist!"
    
    return jsonify(content)

if __name__ == '__main__':
    socketio.run(app)
    #app.run(ssl_context=("localhost+2.pem", "localhost+2-key.pem"))
    

