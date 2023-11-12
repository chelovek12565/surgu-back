from .__all_models import *
from sqlalchemy.sql import text as sql_text
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable, DropTable, MetaData, Table
from sqlalchemy import Column
from sqlalchemy import String, Integer, Float, BigInteger, DateTime
import datetime
import requests


def user_pretty(user: User):
    out = user.to_dict()
    chats = out["chats"]
    out["chats"] = list(map(int, chats.split()))
    return out


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

    user.chats = ""
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
        if mem_id not in members:
            members.append(str(mem_id))
            user = get_user_by_id(mem_id, db_sess)
            user.chats = " ".join(user.chats.split() + [str(chat_id)])
    chat.members = " ".join(sorted(members))
    db_sess.commit()


def add_chat_to_user(db_sess: Session, user_id, chat_id):
    user = get_user_by_id(user_id, db_sess)
    if str(chat_id) in user.chats.split():
        return
    user.chats = " ".join(user.chats.split() + [str(chat_id)])
    db_sess.commit()


def generate_chat(name, members, admin_id, session: Session):
    chat_info = ChatInfo()
    chat_info.name = name
    chat_info.members = " ".join(map(str, members))
    chat_info.admin_id = admin_id

    session.add(chat_info)
    session.commit()

    chat_id = chat_info.id

    for mem_id in members:
        add_chat_to_user(session, mem_id, chat_id=chat_id)

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


def get_user_by_token(token, db_sess: Session):
    user = db_sess.query(User).where(User.token == token).first()
    return user


def get_last_message(chat_id, db_sess: Session):
    sql_insert = f"SELECT * FROM chat_{chat_id}"
    result = db_sess.execute(sql_text(sql_insert)).all()
    if not result:
        return None
    return list(result[-1])


def get_messages_in_chat(chat_id, db_sess: Session):
    result = db_sess.execute(sql_text(f"SELECT * FROM chat_{chat_id}")).all()
    return result


def get_chatinfo_by_chatid(chat_id, db_sess: Session):
    chat_info = db_sess.query(ChatInfo).where(ChatInfo.id == chat_id).first()
    return chat_info


def chat_user_delete_message(chat_id, member_id, db_sess: Session):
    sql_insert = f"INSERT INTO chat_{chat_id} (user_id, text, datetime) VALUES " \
                 f'(0, "{get_username_by_id(member_id, db_sess)} вышел из чата",' \
                 f'"{datetime.datetime.now()}")'
    db_sess.execute(sql_text(sql_insert))
    db_sess.commit()


def chat_user_invite_message(chat_id, member_id, db_sess: Session):
    sql_insert = f"INSERT INTO chat_{chat_id} (user_id, text, datetime) VALUES " \
                 f'(0, "{get_username_by_id(member_id, db_sess)} присоединился к чату",' \
                 f'"{datetime.datetime.now()}")'
    db_sess.execute(sql_text(sql_insert))
    db_sess.commit()


def delete_from_chat(chat_id, member_id, db_sess: Session):
    chat_info = db_sess.query(ChatInfo).where(ChatInfo.id == chat_id).first()
    if chat_info.admin_id == member_id:
        raise Exception("Вы пытаетесь выгнать админа, то есть, скорее всего, самого себя")
    members = chat_info.members.split()
    del members[members.index(str(member_id))]
    chat_info.members = " ".join(members)
    db_sess.commit()


def new_message(chat_id, text, user_id, db_sess: Session):
    # print(meta.tables.keys())
    # table = meta.tables[f"chat_{chat_id}"]
    # sql_insert = table.insert(
        # user_id = user_id,
        # text = text,
        # datetime=datetime.datetime.now()
    # )
    members = db_sess.query(ChatInfo).where(ChatInfo.id == chat_id).first().members.split()
    if str(user_id) not in members:
        raise Exception("Участник не состоит в чате")

    sql_insert = f'INSERT INTO chat_{chat_id} (user_id, text, datetime) VALUES ({user_id}, "{text}", "{datetime.datetime.now()}")'

    db_sess.execute(sql_text(sql_insert))
    db_sess.commit()

# def new_message()