from db import database
from flask import Flask


class Market:
    select_by_marketid = "SELECT `name` FROM market WHERE `id` = ?"
    select_by_name = "SELECT `id` FROM market WHERE `name` = ?"

    def __init__(self, marketid: int, name: str) -> None:
        self.marketid = marketid
        self.name = name


def create_market(app: Flask, name: str) -> int:
    database(app).execute("INSERT INTO market (`name`) VALUES (?)", (name,))


def create_user_market(app: Flask, userid: int, name: str) -> int:
    database(app).execute("INSERT INTO user_market (?, ?)", ())
