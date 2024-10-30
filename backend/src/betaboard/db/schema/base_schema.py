import sqlalchemy
import sqlalchemy.orm

base = sqlalchemy.orm.declarative_base()

class BaseSchema(base):
    __abstract__ = True
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
