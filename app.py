from flask import Flask, Response, g, request, render_template, jsonify
from hashlib import sha3_256
from os import urandom
from json import load
from os.path import isfile, realpath

import db

app = Flask(__name__)
app.config.from_file("./default-config.json", load=load)


# initialize the database if it does not exist yet
@app.cli.command("create-database")
def create_database():
    db.load_schema(app)


# check to see if our database exists yet
with app.app_context():
    db_sqlite_path = app.config["DB_SQLITE_PATH"]
    if not isfile(db_sqlite_path):
        print(f" ! Creating database '{realpath(db_sqlite_path)}'")
        db.load_schema(app)  # create it if it's not there yet

# make sure the database is found and properly closed
app.teardown_appcontext(db.close_connection)

# 32-bit secret key on startup (for encrypting cookies)
# this means that sessions will be invalidated on server
# restart
app.secret_key = urandom(32)


# most of the functionality is behind a JSON API
# pretty much every /api endpoint does a thing and returns JSON


# main index API point
@app.get("/api")
def index() -> Response:
    return jsonify(
        {
            "response format": {
                "status": {
                    "type": "boolean",
                    "description": "if the request was successful or not",
                },
                "data": {
                    "type": "list | dict",
                    "description": "requested data if relevant",
                },
            },
            "help": [
                {
                    "description": "create a user account",
                    "endpoint": "/api/signup",
                    "method": "POST",
                    "parameters": [
                        {"name": "username", "type": "string"},
                        {"name": "password", "type": "string"},
                    ],
                },
                {
                    "description": "query a user account based on its user ID",
                    "endpoint": "/api/account/<User ID>",
                    "method": "GET",
                },
            ],
        }
    )


# query user account by ID
@app.get("/api/account/<int:user_id>")
def account(user_id: int) -> Response:
    user: db.User | None = db.get_user(app, user_id)
    if not user:
        return jsonify({"status": False})

    return jsonify(
        {
            "status": True,
            "data": {
                "username": user.username,
                "password": user.password,
            },
        }
    )


# create a user row
@app.post("/api/signup")
def signup() -> Response:
    username: str = request.form["username"]
    password: str = request.form["password"]

    hashed_password: str = sha3_256(password.encode("utf-8")).hexdigest()

    db.add_user(app, username, hashed_password)

    return jsonify({"status": True})


# static web pages
@app.get("/")
@app.get("/<page>")
def web(page: str = "") -> Response:
    match page:
        case "signup":
            return render_template("signup.j2")
        case "account":
            return render_template("account.j2")

    return render_template("index.j2")
