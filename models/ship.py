from flask import Flask
from sqlite3 import IntegrityError

from typing import Any, Self

import db


class Ship:
    __query_pk: str = "SELECT * FROM `ship` WHERE pk = ?"
    __query_all: str = "SELECT * FROM `ship`"

    __create: str = "INSERT INTO `ship` (`name`, `cost`) VALUES (?, ?) RETURNING `pk`"

    @classmethod
    def get_by_pk(cls, app: Flask, pk: int) -> Self | None:
        if row := db.database(app).execute(cls.__query_pk, [pk]).fetchone():
            return Ship(*row)

    @classmethod
    def get_all_ships(cls, app: Flask):
        if rows := db.database(app).execute(cls.__query_all).fetchall():
            return [Ship(*row) for row in rows]

    @classmethod
    def create(cls, app: Flask, name: str, cost: int = 0) -> Self | None:
        try:
            connection = db.database(app)
            pk = connection.execute(cls.__create, [name, cost]).fetchone()[0]
            connection.commit()

            return cls.get_by_pk(app, pk)
        except IntegrityError:
            ...
        return None

    def __init__(self, pk: int, name: str, cost: int):
        self.pk: int = pk
        self.name: str = name
        self.cost: int = cost  # base price before market adjustments

    def get_public_data(self, app: Flask) -> dict[str, Any]:
        return {"id": str(self.pk), "name": self.name, "cost": self.cost}
