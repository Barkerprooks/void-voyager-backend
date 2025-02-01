import sqlite3
from flask import Flask, g


DATABASE_ATTR_NAME = "_database"


class User:
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password


def get_connection(app: Flask):
    if (connection := getattr(g, DATABASE_ATTR_NAME, None)) is None:
        connection = g._database = sqlite3.connect(app.config["DB_SQLITE_PATH"])
    return connection


def close_connection(exception: Exception):
    if connection := getattr(g, DATABASE_ATTR_NAME, None):
        connection.close()


def load_schema(app: Flask) -> None:
    connection = get_connection(app)
    with open(app.config["DB_SCHEMA_PATH"]) as file:
        connection.executescript(file.read())
    connection.commit()


def add_user(app: Flask, username: str, password: str) -> None:
    get_connection(app).execute("INSERT INTO user VALUES (?, ?)", (username, password))


def get_user_by_id(app: Flask, user_id: int) -> User | None:
    if (
        row := (
            get_connection(app)
            .execute("SELECT `username`, `password` FROM user WHERE id = ?", (user_id,))
            .fetchone()
        )
    ) is None:
        return None

    username, password = row
    return User(username, password)


def get_user_by_username(app: Flask, username: str) -> User | None: ...


def user_login(app: Flask, username: str, password: str) -> bool:
    user: User = get_user_by_username(app, username)


def add_user_market(app: Flask, user: int, market: int) -> None:
    get_connection(app).execute("INSERT INTO user_market VALUES (?, ?)", (user, market))
