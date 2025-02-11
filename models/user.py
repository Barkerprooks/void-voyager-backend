from flask import Flask
from hashlib import sha3_256
from sqlite3 import IntegrityError

from typing import Self

from models.ship import Ship

import db


class User:
    __query_pk: str = "SELECT * FROM `user` WHERE `pk` = ?"
    __query_username: str = "SELECT * FROM `user` WHERE `username` = ?"

    __create: str = "INSERT INTO `user` (`username`, `password`, `is_admin`, `money`) VALUES (?, ?, ?, ?) RETURNING `pk`"

    __edit_money: str = "UPDATE `user` SET `money` = ? WHERE `pk` = ?"

    @staticmethod
    def hash(password: str) -> str:
        return sha3_256(password.encode("utf-8")).hexdigest()

    @classmethod
    def get_by_pk(cls, app: Flask, pk: int) -> Self | None:
        if row := db.database(app).execute(cls.__query_pk, [pk]).fetchone():
            return User(*row)

    @classmethod
    def get_by_username(cls, app: Flask, username: str) -> Self | None:
        if row := db.database(app).execute(cls.__query_username, [username]).fetchone():
            return User(*row)

    @classmethod
    def create(
        cls,
        app: Flask,
        username: str,
        password: str,
        is_admin: bool = False,
        money: int = 1000,
    ) -> Self | None:
        try:
            connection = db.database(app)
            pk = connection.execute(
                cls.__create, [username, cls.hash(password), is_admin, money]
            ).fetchone()[0]  # returns a tuple. need to de-sugar the id returned
            connection.commit()  # save the new user on creation

            return cls.get_by_pk(app, pk)  # should be in there now
        except IntegrityError:  # user tried to insert an identical username
            ...
        return None  # not a valid ID in the table

    def __init__(
        self,
        pk: int,
        username: str,
        password: str,
        is_admin: bool,
        money: int,
    ) -> None:
        self.pk: int = pk  # primary key
        self.username: str = username
        self.password: str = password  # should be hashed before it gets here
        self.is_admin: bool = is_admin
        self.money: int = money

    def get_public_data(self, app: Flask) -> dict[str, str]:
        return {
            "id": str(self.pk),
            "username": self.username,
            "is_admin": self.is_admin,
            "money": self.money,
            "ships": [
                {"id": ship.pk, "name": ship.name, "type": ship.get_type(app)}
                for ship in UserShip.get_user_ships(app, self.pk)
            ],
        }

    def set_money(self, app: Flask, money: int):
        connection = db.database(app)
        value = connection.execute(self.__edit_money, [money, self.pk]).fetchone()
        connection.commit()
        return value

    def buy_ship(self, app: Flask, pk: int) -> bool:
        ship: Ship = Ship.get_by_pk(app, pk)

        if ship and self.money - ship.cost >= 0:
            value = self.set_money(app, self.money - ship.cost)
            return (
                True
                if UserShip.create(app, ship.name, self.pk, pk) and value == self.money
                else False
            )

        return False

    def edit_ship(self, app: Flask, pk: int, name: str) -> bool:
        user_ship: UserShip = UserShip.get_by_pk(app, pk)
        return user_ship.set_name(app, name)

    def sell_ship(self, app: Flask, pk: int) -> bool:
        # give money back to user
        self.set_money(app, self.money + UserShip.get_by_pk(app, pk).get_type(app).cost)
        UserShip.remove(app, pk)

        return True  # TODO: properly implement this...


class UserShip:
    __query_pk = "SELECT * FROM `user_ship` WHERE `pk` = ?"
    __user_ships = "SELECT * FROM `user_ship` WHERE `user` = ?"

    __create: str = "INSERT INTO `user_ship` (`name`, `user`, `ship`) VALUES (?, ?, ?) RETURNING `pk`"
    __edit_name: str = (
        "UPDATE `user_ship` SET `name` = ? WHERE `pk` = ? RETURNING `name`"
    )
    __sell_ship: str = "DELETE FROM `user_ship` WHERE `pk` = ?"

    @classmethod
    def get_by_pk(cls, app: Flask, pk: int) -> Self | None:
        if row := db.database(app).execute(cls.__query_pk, [pk]).fetchone():
            return UserShip(*row)

    @classmethod
    def get_user_ships(self, app: Flask, user: int) -> list[Self]:
        if rows := db.database(app).execute(self.__user_ships, [user]).fetchall():
            return [UserShip(*row) for row in rows]
        return []

    @classmethod
    def create(cls, app: Flask, name: str, user: int, ship: int) -> Self | None:
        connection = db.database(app)
        pk = connection.execute(cls.__create, [name, user, ship]).fetchone()[0]
        connection.commit()
        return cls.get_by_pk(app, pk)

    @classmethod
    def remove(cls, app: Flask, pk: int):
        connection = db.database(app)
        connection.execute(cls.__sell_ship, [pk])
        connection.commit()

    def __init__(self, pk: int, name: str, user: int, ship: int):
        self.pk: int = pk
        self.name: str = name
        self.user: int = user
        self.ship: int = ship

    def set_name(self, app: Flask, name: str) -> bool:
        # make sure the new name matches what got put into the database
        connection = db.database(app)
        new_name = connection.execute(
            self.__edit_name,
            [name, self.pk],
        ).fetchone()[0]
        connection.commit()
        return new_name == name

    def get_user(self, app: Flask) -> User:
        return User.get_by_pk(app, self.user)

    def get_type(self, app: Flask) -> Ship:
        return Ship.get_by_pk(app, self.ship)
