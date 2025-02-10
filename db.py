from flask import Flask, g
from os.path import isfile
from typing import NoReturn
from models.ship import Ship

import sqlite3
import json


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

def load_ships(app: Flask) -> bool:
    load_ship_data: str = app.config["LOAD_SHIP_DATA"]
    ships_added: int = 0

    if isfile(load_ship_data):
        with open(load_ship_data) as file:
            for entry in json.load(file):
                ship = Ship.create(app, entry["name"], entry["cost"])
                if ship:
                    ships_added += 1
                    print(f" * created ship {ship.name} with ID {ship.pk}")
    
    return ships_added