from flask import Flask
from db import database
from hashlib import sha3_256
from sqlite3 import IntegrityError

from typing import Self


class User:
    __uid: str = "SELECT `username`, `password`, `is_admin` FROM `user` WHERE `id` = ?"
    __username: str = "SELECT `id`, `password`, `is_admin` FROM `user` WHERE `username` = ?"

    __create: str = "INSERT INTO `user` (`username`, `password`) VALUES (?, ?) RETURNING `id`"

    @staticmethod
    def hash(password: str) -> str:
        return sha3_256(password.encode("utf-8")).hexdigest()

    @classmethod
    def get_by_uid(cls, app: Flask, uid: int) -> Self | None:
        if row := database(app).execute(cls.__uid, [uid]).fetchone():
            username, password, is_admin = row
            return User(uid, username, password, is_admin)

    @classmethod
    def get_by_username(cls, app: Flask, username: str) -> Self | None:
        if row := database(app).execute(cls.__username, [username]).fetchone():
            uid, password, is_admin = row
            return User(uid, username, password, is_admin)

    @classmethod
    def create(cls, app: Flask, username: str, password: str, is_admin: bool = False) -> Self | None:
        try:
            connection = database(app)
            uid = connection.execute(
                User.__create, [username, cls.hash(password)]
            ).fetchone()[0]  # returns a tuple. need to de-sugar the id returned
            connection.commit()  # save the new user on creation

            return cls.get_by_uid(app, uid)  # should be in there now
        except IntegrityError:  # user tried to insert an identical username
            ...
        return None  # not a valid ID in the table

    def __init__(self, uid: int, username: str, password: str, is_admin: bool) -> None:
        self.uid: int = uid
        self.username: str = username
        self.password: str = password  # should be hashed before it gets here
        self.is_admin: bool = is_admin

    def get_public_data(self, app: Flask) -> dict[str, str]:
        return { 
            "id": str(self.uid), 
            "username": self.username, 
            "is_admin": self.is_admin 
        }
