from flask import Flask, g
from os.path import isfile
from typing import NoReturn

import sqlite3


DATABASE_ATTR_NAME = "_database"


def database(app: Flask) -> sqlite3.Connection | NoReturn:
    db_sqlite_path: str = app.config["DB_SQLITE_PATH"]
    if isfile(db_sqlite_path):
        if (connection := getattr(g, DATABASE_ATTR_NAME, None)) is None:
            connection = g._database = sqlite3.connect(app.config["DB_SQLITE_PATH"])
        return connection
    raise FileNotFoundError("database not found. run `flask create-database`")


def close_connection(_: Exception):
    if connection := getattr(g, DATABASE_ATTR_NAME, None):
        connection.close()


def load_schema(app: Flask) -> bool:
    db_schema_path: str = app.config["DB_SCHEMA_PATH"]

    if isfile(db_schema_path):
        connection = sqlite3.connect(app.config["DB_SQLITE_PATH"])
        with open(db_schema_path) as file:
            connection.executescript(file.read())
        connection.commit()
        return True

    return False
