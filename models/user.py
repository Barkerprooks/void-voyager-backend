from flask import Flask
from db import database
from hashlib import sha3_256
from sqlite3 import IntegrityError

from typing import Self


class User:
    __query_pk: str = "SELECT * FROM `user` WHERE `pk` = ?"
    __query_username: str = "SELECT * FROM `user` WHERE `username` = ?"

    __create: str = "INSERT INTO `user` (`username`, `password`, `is_admin`) VALUES (?, ?, ?) RETURNING `pk`"

    @staticmethod
    def hash(password: str) -> str:
        return sha3_256(password.encode("utf-8")).hexdigest()

    @classmethod
    def get_by_pk(cls, app: Flask, pk: int) -> Self | None:
        if row := database(app).execute(cls.__query_pk, [pk]).fetchone():
            return User(*row)

    @classmethod
    def get_by_username(cls, app: Flask, username: str) -> Self | None:
        if row := database(app).execute(cls.__query_username, [username]).fetchone():
            return User(*row)

    @classmethod
    def create(
        cls,
        app: Flask,
        username: str,
        password: str,
        is_admin: bool = False,
    ) -> Self | None:
        try:
            connection = database(app)
            pk = connection.execute(
                cls.__create, [username, cls.hash(password), is_admin]
            ).fetchone()[0]  # returns a tuple. need to de-sugar the id returned
            connection.commit()  # save the new user on creation

            return cls.get_by_pk(app, pk)  # should be in there now
        except IntegrityError:  # user tried to insert an identical username
            ...
        return None  # not a valid ID in the table

    def __init__(self, pk: int, username: str, password: str, is_admin: bool) -> None:
        self.pk: int = pk  # primary key
        self.username: str = username
        self.password: str = password  # should be hashed before it gets here
        self.is_admin: bool = is_admin

    def get_public_data(self, app: Flask) -> dict[str, str]:
        return {
            "id": str(self.pk),
            "username": self.username,
            "is_admin": self.is_admin,
            "incorperations": {},
            "markets": {},
            "ships": {},
        }
