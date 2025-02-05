from flask import Flask
from db import database
from hashlib import sha3_256
from sqlite3 import IntegrityError

from typing import Self


class User:
    userid_query: str = "SELECT `username`, `password` FROM `user` WHERE `id` = ?"
    username_query: str = "SELECT `id`, `password` FROM `user` WHERE `username` = ?"

    markets_query: str = "SELECT `market` FROM `user_market` WHERE `user` = ?"

    create_new: str = (
        "INSERT INTO `user` (`username`, `password`) VALUES (?, ?) RETURNING `id`"
    )

    @staticmethod
    def hash(password: str) -> str:
        return sha3_256(password.encode("utf-8")).hexdigest()

    @classmethod
    def get_by_userid(cls, app: Flask, userid: int) -> Self | None:
        if row := database(app).execute(cls.userid_query, [userid]).fetchone():
            username, password = row
            return User(userid, username, password)

    @classmethod
    def get_by_username(cls, app: Flask, username: str) -> Self | None:
        if row := database(app).execute(cls.username_query, [username]).fetchone():
            userid, password = row
            return Self(userid, username, password)

    @classmethod
    def create_user(cls, app: Flask, username: str, password: str) -> Self | None:
        try:
            connection = database(app)
            userid = connection.execute(
                User.create_new, [username, cls.hash(password)]
            ).fetchone()
            connection.commit()  # save the new user on creation

            return cls.get_by_userid(userid)  # should be in there now
        except IntegrityError:  # user tried to insert an identical username
            ...
        return None  # not a valid ID in the table

    def __init__(self, userid: int, username: str, password: str) -> None:
        self.userid: int = userid
        self.username: str = username
        self.password: str = password  # should be hashed before it gets here

    def __markets(self, app: Flask) -> list[int]:
        return database(app).execute(self.select_markets, [self.userid]).fetchall()

    def get_data(self, app: Flask) -> dict[str, str]:
        return {
            "id": str(self.userid),
            "username": self.username,
            "password": self.password,
            "markets": self.__markets(app),
        }
