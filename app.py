from flask import Flask, Response, request, redirect, session, render_template, jsonify
from os import urandom
from json import load
from os.path import isfile
from werkzeug.exceptions import BadRequest
from getpass import getpass

from typing import Any

from models.user import User, UserShip
from models.ship import Ship
import db

# prefer local first
SETTINGS_PATHS: list[str] = [
    "./settings.json",
    "./etc/settings.json",
    "/etc/void-voyager/settings.json",
    "/etc/void-voyager-ansible/settings.json",
    "/etc/void-voyager-backend/settings.json",
]

# dynamically pull in the most relevent settings file
valid_settings_paths: list[str] = [path for path in SETTINGS_PATHS if isfile(path)]

if not valid_settings_paths:
    raise FileNotFoundError(
        f"could not locate `settings.json` valid locations are: {SETTINGS_PATHS}"
    )

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
        print(" x error: could not find schema file")


@app.cli.command("create-user")
def create_user(username: str = "", password: str = ""):
    if not username:
        username = input("enter username: ")

    if not password:
        password = getpass("enter password: ")

    User.create(app, username, password, False)


@app.cli.command("create-admin")
def create_admin(username: str = "", password: str = ""):
    if not username:
        username = input("enter admin username: ")

    if not password:
        password = getpass("enter admin password: ")

    User.create(app, username, password, True)


@app.cli.command("load-ships")
def load_ships():
    print(f" * loaded {db.load_ships(app)} ships")


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


def store_session(pk: int):
    session["id"] = pk


def get_user_id() -> int:
    return session.get("id")


def clear_session() -> bool:
    if "id" in session:
        del session["id"]
    else:
        return False
    return "id" in session


# --------------------------------------------------------------------------------------
# API GET requests
# --------------------------------------------------------------------------------------
# query logged in user
@app.get("/api/account")
def account() -> Response:
    if not (pk := get_user_id()):
        return json_error(401)  # not logged in

    user: db.User | None = User.get_by_pk(app, pk)

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

    if user := User.create(app, username, password):
        session["id"] = user.pk  # login after creation
        return json_response({"id": user.pk})

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
        session["id"] = user.pk
        return json_response()

    return json_error(401)


# post request to make sure they really intend to log out
@app.post("/api/logout")
def logout() -> Response:
    if clear_session():
        return json_response()

    return json_error(500)  # weird if it gets here but whatever


# USER - BUY - SHIPS
@app.post("/api/user/buy/ship")
def buy_ship() -> Response:  # buy a personal ship
    if not (pk := get_user_id()):
        return json_error(401)  # not authorized to buy ships

    try:
        ship: str = request.json["ship"]
    except (KeyError, BadRequest):
        return json_error(400)

    user: User = User.get_by_pk(app, pk)

    if user.buy_ship(app, ship):
        return json_response({})

    return json_error()


# USER - EDIT - SHIPS
@app.post("/api/user/edit/ship/<int:ship>")
def edit_ship(ship: int) -> Response:
    if not (pk := get_user_id()):
        return json_error(401)

    try:
        name: str = request.json["name"]
    except (KeyError, BadRequest):
        return json_error(400)

    user: User = User.get_by_pk(app, pk)
    if user.edit_ship(app, ship, name):
        return json_response({})

    return json_error()


# USER - SELL - SHIPS
@app.post("/api/user/sell/ship/<int:ship>")
def sell_ship(ship: int) -> Response:
    if not (pk := get_user_id()):
        return json_error(401)

    user: User = User.get_by_pk(app, pk)

    if user.sell_ship(app, ship):
        return json_response({})

    return json_error()


# --------------------------------------------------------------------------------------
# WEB INTERFACE
# --------------------------------------------------------------------------------------
# static web pages
@app.get("/")
@app.get("/<page>")
def web(page: str = "") -> Response:
    context: dict[str, Any] = {"data": {}}
    template: str = "index.j2"

    match page:
        # account management
        case "login":
            template = "login.j2"
        case "signup":
            template = "signup.j2"
        # authenticated endpoints
        case "logout":  # just render the index but without a user id to query
            clear_session()
            return redirect("/")
        case "dashboard":  # make sure the user has a session ID before showing them
            if not get_user_id():
                return redirect("/")
            context["ships"] = Ship.get_all_ships(app)
            template = "dashboard.j2"

    if user := User.get_by_pk(app, session.get("id")):
        context["data"] = user.get_public_data(app)

    return render_template(template, **context)
