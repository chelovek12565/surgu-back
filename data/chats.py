import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy.schema import CreateTable



class ChatInfo(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chat_info'
    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, autoincrement=True, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    members = sqlalchemy.Column(sqlalchemy.String)
    admin_id = sqlalchemy.Column(sqlalchemy.Integer)

