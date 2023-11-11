import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy.schema import CreateTable
from sqlalchemy import Column, MetaData, Table
from sqlalchemy import String, Integer, Float, BigInteger, DateTime


class ChatInfo(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chat_info'
    id = sqlalchemy.Column(sqlalchemy.Integer, unique=True, autoincrement=True, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    members = sqlalchemy.Column(sqlalchemy.String)
    admin_id = sqlalchemy.Column(sqlalchemy.Integer)

