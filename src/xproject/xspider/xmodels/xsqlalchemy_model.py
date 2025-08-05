from __future__ import annotations

import hashlib
import json
import re
from abc import ABCMeta
from collections.abc import Iterable
from datetime import datetime
from typing import Any, Self, TYPE_CHECKING, cast

from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, JSON
from sqlalchemy import Engine
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import Text, TypeDecorator

from xproject.xjson import JSONEncoder
from xproject.xspider.xenums.xdata_status_enum import DataStatusEnum
from xproject.xspider.xmodels.xmodel import Model
from xproject.xstring import camel_to_snake

if TYPE_CHECKING:
    from xproject.xspider.xitems.xitem import Item

Base = declarative_base()


class MediumText(TypeDecorator):
    impl = Text

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        if dialect.name == "mysql":
            # MEDIUMTEXT: Maximum length 16 MB (16,777,215 bytes)
            return dialect.type_descriptor(Text(length=16777215))
        return super().load_dialect_impl(dialect)


class LongText(TypeDecorator):
    impl = Text

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[Any]:
        if dialect.name == "mysql":
            # LONGTEXT: Maximum length 4 GB (4,294,967,295 bytes)
            return dialect.type_descriptor(Text(length=4294967295))
        return super().load_dialect_impl(dialect)


class SqlalchemyModelMeta(type(Base), ABCMeta):
    def __new__(mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> type:
        if attrs.get("__abstract__") is True:
            return super().__new__(mcs, name, bases, attrs)

        table_name = attrs.get("__tablename__")
        if table_name is None:
            table_name = camel_to_snake(name)
            attrs["__tablename__"] = table_name
        else:
            if not (isinstance(table_name, str) and table_name):
                raise ValueError(f"Illegal assignment {name}.__tablename__")

        engine = attrs.get("__engine__")
        if not isinstance(engine, Engine):
            raise ValueError(f"Illegal assignment {name}.__engine__")

        data_columns = attrs.get("__data_columns__")
        if not (isinstance(data_columns, list) and all(map(lambda x: isinstance(x, str), data_columns))):
            raise ValueError(f"Illegal assignment {name}.__data_columns__")

        session = attrs.get("__session__")
        if session is None:
            session = sessionmaker(bind=engine)()
            attrs["__session__"] = session
        else:
            if not isinstance(session, Session):
                raise ValueError(f"Illegal assignment {name}.__session__")

        return super().__new__(mcs, name, bases, attrs)


class SqlalchemyModel(Base, Model, metaclass=SqlalchemyModelMeta):
    __abstract__ = True

    __tablename__: str
    __engine__: Engine
    __data_columns__: list[str]
    __session__: Session

    id = Column(Integer, comment="id", primary_key=True, autoincrement=True)
    data_id = Column(String(64), comment="data id", nullable=False, unique=True)
    data_columns = Column(JSON, comment="data columns", nullable=False)
    data_status = Column(SmallInteger, comment="data status", default=DataStatusEnum.OK.value, index=True)
    data_create_time = Column(DateTime, comment="data create time", default=datetime.now)
    data_update_time = Column(DateTime, comment="data update time", default=datetime.now, onupdate=datetime.now)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} (id={self.id}, data_id={self.data_id})>"

    def to_row(self) -> dict[str, Any]:
        data = {column.name: getattr(self, column.name) for column in cast(Iterable, self.__table__.columns)}
        jsn = json.dumps(data, ensure_ascii=False, cls=JSONEncoder)
        row = json.loads(jsn)
        return row

    @classmethod
    def gen_data_id(cls, data: dict[str, Any] | Item) -> str:
        data_column_value_strs = []
        for data_column in cls.__data_columns__:
            if data_column in data:
                data_column_value_str = str(data[data_column])
                data_column_value_strs.append(data_column_value_str)
            else:
                raise ValueError(f"data must provide the '{data_column}' field")
        data_id = hashlib.sha256("".join(data_column_value_strs).encode()).hexdigest()
        return data_id

    @classmethod
    def get_data_id(cls, data: dict[str, Any] | Item) -> str:
        if "data_id" in data:
            if isinstance(data["data_id"], str) and re.match(r"^[0-9a-f]{32}$", data["data_id"]) is not None:
                return data["data_id"]
        return cls.gen_data_id(data)

    @classmethod
    def get_ins_by_data_id(cls, data: dict[str, Any] | Item) -> Self | None:
        session = cls.__session__
        data_id = cls.get_data_id(data)
        try:
            ins: Self = session.query(cls).filter_by(data_id=data_id).one()
        except NoResultFound:
            return None
        return ins

    @classmethod
    def get_row_by_data_id(cls, data: dict[str, Any] | Item) -> dict[str, Any] | None:
        ins = cls.get_ins_by_data_id(data)
        if ins is None:
            return None
        data = ins.to_row()
        return data

    @classmethod
    def save(cls, data: dict[str, Any] | Item) -> bool:
        session = cls.__session__

        ins = cls.get_ins_by_data_id(data)
        update = False if ins is None else True

        if not update:
            # insert
            ins = cls(
                data_id=cls.get_data_id(data),
                data_columns=cls.__data_columns__,
                **data
            )
            session.add(ins)
        else:
            # update
            if ins is None:
                ins = cls.get_ins_by_data_id(data)
            for k, v in data.items():
                setattr(ins, k, v)

        session.commit()

        return update

    @classmethod
    def create_table(cls) -> None:
        Base.metadata.create_all(cls.__engine__)

    @classmethod
    def columns(cls) -> list[str]:
        return [c.name for c in cast(Iterable, cls.__table__.columns)]
