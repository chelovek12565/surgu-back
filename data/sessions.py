import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class SocketSession(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'sessions'
    sid = sqlalchemy.Column(sqlalchemy.String, unique=True, primary_key=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer)
    token = sqlalchemy.Column(sqlalchemy.String)