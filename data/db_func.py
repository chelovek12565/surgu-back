from .__all_models import *
from sqlalchemy.sql import text as sql_text
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable, DropTable, MetaData, Table
from sqlalchemy import Column
from sqlalchemy import String, Integer, Float, BigInteger, DateTime
import datetime
import requests


def new_user(db_sess: Session, token):
    user = User()
    r = requests.get("https://api.weeek.net/public/v1/user/me",
                     headers={
                         'Authorization': 'Bearer ' + token
                     })

    result = r.json()
    if result["success"] == "false":
        raise Exception("Аутентификация не пройдена")
    user.token = token
    name = [result['user']['firstName'], result['user']['lastName']]
    name = filter(lambda x: bool(x), name)

    user.username = " ".join(name)
    db_sess.add(user)


def get_sid_by_chat(chat_id, db_sess: Session):
    sids = list(map(lambda x: x.sid,
                db_sess.query(SocketSession).filter(SocketSession.chat_id == chat_id).all()))
    return sids


def get_username_by_id(user_id, db_sess: Session):
    username = db_sess.query(User).filter(User.id == user_id).first().username
    return username


def create_session(db_sess: Session, sid, chat_id, token):
    session = SocketSession()
    session.sid = sid
    session.chat_id = chat_id
    session.token = token
    db_sess.add(session)
    db_sess.commit()


def delete_session(db_sess: Session, sid):
    session = db_sess.query(SocketSession).filter(SocketSession.sid == sid).first()
    db_sess.delete(session)
    db_sess.commit()


def add_chat_members(db_sess: Session, members_id, chat_id):
    chat = db_sess.query(ChatInfo).where(ChatInfo.id == chat_id).first()
    members = chat.members.split()
    for mem_id in members_id:
        if str(mem_id) not in members:
            members.append(str(mem_id))
    chat.members = " ".join(sorted(members))
    db_sess.commit()


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


def get_user_by_id(user_id, db_sess: Session):
    user = db_sess.query(User).where(User.id == user_id).first()
    return user


def get_messages_in_chat(chat_id, db_sess: Session):
    result = db_sess.execute(sql_text(f"SELECT * FROM chat_{chat_id}")).all()
    return result


def new_message(chat_id, text, user_id, db_sess: Session):
    # print(meta.tables.keys())
    # table = meta.tables[f"chat_{chat_id}"]
    # sql_insert = table.insert(
        # user_id = user_id,
        # text = text,
        # datetime=datetime.datetime.now()
    # )
    members = db_sess.query(ChatInfo).where(ChatInfo.id == chat_id).first().members.split()
    if user_id not in members:
        raise Exception("Участник не состоит в чате")

    sql_insert = f'INSERT INTO chat_{chat_id} (user_id, text, datetime) VALUES ({user_id}, "{text}", "{datetime.datetime.now()}")'

    db_sess.execute(sql_text(sql_insert))
    db_sess.commit()

# def new_message()