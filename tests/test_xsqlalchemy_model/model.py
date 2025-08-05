from sqlalchemy import create_engine, Column, Integer, String

import xproject

# CREATE DATABASE `db` CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_unicode_ci';
engine = create_engine(
    f"mysql+pymysql://root:{xproject.xurl.quote('root', safe='')}@127.0.0.1:3306/db?charset=utf8mb4",
    echo=False
)


class Person(xproject.xspider.xmodels.xsqlalchemy_model.SqlalchemyModel):
    # __tablename__ = "person"
    __engine__ = engine
    __data_columns__ = ["name", "gender"]

    name = Column(String(50), comment="name")
    gender = Column(String(10), comment="gender")
    age = Column(Integer, comment="age")


Person.create_table()

__all__ = [
    "Person",
]
