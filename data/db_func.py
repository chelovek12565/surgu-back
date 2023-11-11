from .__all_models import *
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable, DropTable



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
        ('id', BigInteger),
        ('text', String),
        ('user_id', Integer)
    ]

    TABLE_NAME = f'chat_{chat_id}'

    columns = [Column(n, t) for n, t in TABLE_SPEC]
    table = Table(TABLE_NAME, MetaData(), *columns)
    table_creation_sql = CreateTable(table)
    session.execute(table_creation_sql)
    session.commit()


def new_message()