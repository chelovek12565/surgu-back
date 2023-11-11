from .__all_models import *
from sqlalchemy.sql import text as sql_text
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable, DropTable, MetaData, Table
from sqlalchemy import Column
from sqlalchemy import String, Integer, Float, BigInteger, DateTime
import datetime


def new_user(db_sess: Session, username, token):
    user = User()
    user.username = username
    user.token = token
    db_sess.add(user)


def create_session(db_sess: Session, sid, chat_id, username):
    session = SocketSession()
    session.sid = sid
    session.chat_id = chat_id
    session.token = token
    db_sess.add(session)


def delete_session(db_sess: Session, sid):
    session = db_sess.query(SocketSession).filter(SocketSession.sid == sid)
    db_sess.delete(session)


def generate_chat(name, members, admin_id, session: Session):

    chat_info = ChatInfo()
    chat_info.name = name
    chat_info.members = " ".join(map(str, members))
    chat_info.admin_id = admin_id
    session.add(chat_info)
    session.commit()
    chat_id = chat_info.id

    TABLE_SPEC = [
        ('text', String),
        ('user_id', Integer),
        ('datetime', DateTime)
    ]

    TABLE_NAME = f'chat_{chat_id}'
    columns = [Column('id', Integer, unique=True, autoincrement=True, primary_key=True)]
    columns.extend([Column(n, t) for n, t in TABLE_SPEC])
    table = Table(TABLE_NAME, MetaData(), *columns)
    table_creation_sql = CreateTable(table)
    session.execute(table_creation_sql)
    session.commit()


def new_message(chat_id, text, user_id, db_sess: Session):
    meta = MetaData()
    print(meta.tables.keys())
    # table = meta.tables[f"chat_{chat_id}"]
    # sql_insert = table.insert(
        # user_id = user_id,
        # text = text,
        # datetime=datetime.datetime.now()
    # )

    sql_insert = f'INSERT INTO chat_{chat_id} (user_id, text, datetime) VALUES ({user_id}, "{text}", "{datetime.datetime.now()}")'

    db_sess.execute(sql_text(sql_insert))
    db_sess.commit()

# def new_message()