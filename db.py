from hashlib import sha3_256
from flask import Flask, g
from os.path import isfile

import sqlite3


DATABASE_ATTR_NAME = "_database"


def get_connection(app: Flask):
    if (connection := getattr(g, DATABASE_ATTR_NAME, None)) is None:
        connection = g._database = sqlite3.connect(app.config["DB_SQLITE_PATH"])
    return connection


def close_connection(_: Exception):
    if connection := getattr(g, DATABASE_ATTR_NAME, None):
        connection.close()


def load_schema(app: Flask) -> bool:
    db_schema_path: str = app.config['DB_SCHEMA_PATH']

    if isfile(db_schema_path):
        connection = get_connection(app)
        with open(db_schema_path) as file:
            connection.executescript(file.read())
        connection.commit()

    return False





class User:
    select_by_id: str = "SELECT `username`, `password` FROM `user` WHERE `id` = ?"
    select_by_username: str = "SELECT `id`, `password` FROM `user` WHERE `username` = ?"

    select_markets: str = "SELECT `market` FROM `user_market` WHERE `user` = ?"

    insert_new: str = "INSERT INTO `user` (`username`, `password`) VALUES (?, ?) RETURNING `id`"

    @staticmethod
    def hash(password: str) -> str:
        return sha3_256(password.encode("utf-8")).hexdigest()

    def __init__(self, userid: int, username: str, password: str) -> None:
        self.userid: int = userid
        self.username: str = username
        self.password: str = password # should be hashed before it gets here

    def __markets(self, app: Flask) -> list[int]:
        return (
            get_connection(app)
            .execute(self.select_markets, [self.userid])
            .fetchall()
        )

    def get_data(self, app: Flask) -> dict[str, str]:
        return {
            "id": str(self.userid),
            "username": self.username,
            "password": self.password,
            "markets": self.__markets(app)
        }


def create_user(app: Flask, username: str, password: str) -> int:
    try:
        connection = get_connection(app)
        user_id = (
            connection
            .execute(User.insert_new, [username, User.hash(password)])
            .fetchone()
        )
        connection.commit() # save the new user on creation

        return user_id[0]
    except sqlite3.IntegrityError: # user tried to insert an identical username
        ...
    return 0 # not a valid ID in the table


def get_user_by_id(app: Flask, userid: int) -> User | None:
    if (
        row := (
            get_connection(app)
            .execute(User.select_by_id, [userid])
            .fetchone()
        )
    ) is None:
        return None

    username, password = row
    return User(userid, username, password)


def get_user_by_username(app: Flask, username: str) -> User | None:
    if (
        row := (
            get_connection(app)
            .execute(User.select_by_username, [username])
            .fetchone()
        )
    ) is None:
        return None
    
    userid, password = row
    return User(userid, username, password)


def check_user_password(app: Flask, username: str, password: str) -> bool:
    user: User = get_user_by_username(app, username)
    return user.password == User.hash(password)