from flask import Flask, Response, request, session, render_template, jsonify
from os import urandom
from json import load
from os.path import isfile, realpath
from werkzeug.exceptions import BadRequest

from typing import Any

from models.user import User
import db

# prefer local first
SETTINGS_PATHS: list[str] = [
    "./settings.json",
    "./etc/settings.json",
    "/etc/void-voyager/settings.json",
    "/etc/void-voyager-backend/settings.json",
]

# dynamically pull in the most relevent settings file
valid_settings_paths: list[str] = [path for path in SETTINGS_PATHS if isfile(path)]

if not valid_settings_paths:
    print(" X error: could not locate `settings.json` valid locations are:")
    for path in SETTINGS_PATHS:
        print(path)
    exit(0)

settings_path: str = valid_settings_paths[0]


# setup the app
app: Flask = Flask(__name__)
app.config.from_file(settings_path, load=load)


# command to initialize the database if it does not exist yet
@app.cli.command("create-database")
def create_database():
    if db.load_schema(app):
        print(" * database created")
    else:
        print(" X error: could not find schema file")


# make sure the database is found and properly closed
app.teardown_appcontext(db.close_connection)

# 32-bit secret key on startup (for encrypting cookies)
# this means that sessions will be invalidated on server
# restart
app.secret_key = urandom(32)


# most of the functionality is behind a JSON API
# pretty much every /api endpoint does a thing and returns JSON


def json_response(data: dict[str, str] = {}) -> Response:
    if not data:
        return jsonify({"status": True})
    return jsonify({"status": True, "data": data})


def json_error(status_code: int = 500) -> Response:
    return jsonify({"status": False}), status_code


# --------------------------------------------------------------------------------------
# API GET requests
# --------------------------------------------------------------------------------------


# query logged in user
@app.get("/api/account")
def account() -> Response:
    if not (userid := session.get("userid")):
        return json_error(401)  # not logged in

    user: db.User | None = User.get_user_by_id(app, userid)

    if not user:
        del session["userid"]  # could not find user for some reason, remove bad ID
        return json_error(404)  # user does not exist

    return json_response(user.get_data(app))


# --------------------------------------------------------------------------------------
# API POST requests
# --------------------------------------------------------------------------------------


# create a user row
@app.post("/api/signup")
def signup() -> Response:
    try:
        username: str = request.json["username"]
        password: str = request.json["password"]
    except (KeyError, BadRequest):
        return json_error(400)

    if user := User.create_user(app, username, password):
        session["userid"] = user.userid  # login after creation
        return json_response({"userid": user.userid})

    return json_error(403)  # user already exists


# map user to a new session
@app.post("/api/login")
def login() -> Response:
    try:
        username: str = request.json["username"]
        password: str = request.json["password"]
    except (KeyError, BadRequest):
        return json_error(400)

    user: User = User.get_by_username(app, username)

    if user and user.password == User.hash(password):
        session["userid"] = user.userid
        return json_response()

    return json_error(401)


# post request to make sure they really intend to log out
@app.post("/api/logout")
def logout() -> Response:
    if "userid" in session:
        del session["userid"]
        return json_response()

    return json_error(500)  # weird if it gets here but whatever


# --------------------------------------------------------------------------------------
# WEB INTERFACE
# --------------------------------------------------------------------------------------


# static web pages
@app.get("/")
@app.get("/<page>")
def web(page: str = "") -> Response:
    template: str = "index.j2"

    match page:
        # account management
        case "login":
            template = "login.j2"
        case "signup":
            template = "signup.j2"
        # authenticated endpoints
        case "logout":  # just render the index but without a user id to query
            if "userid" in session:
                del session["userid"]
        case "dashboard":  # make sure the user has a session ID before showing them
            template = "dashboard.j2" if session.get("userid") else "index.j2"

    user: User = User.get_by_userid(app, session.get("userid"))
    data: dict[str, Any] = user.get_public_data(app) if user else {}

    return render_template(template, data=data)
