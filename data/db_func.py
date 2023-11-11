from .__all_models import *
from sqlalchemy.orm import Session



def new_user(db_sess: Session, data):
    user = User()
    user.username = data['username']
    user.email = data['email']
    user.password = data['password']
    db_sess.add(user)


def create_session(db_sess: Session, sid, chat_id, username):
    session = SocketSession()
    session.sid = sid
    session.chat_id = chat_id
    session.username = username
    db_sess.add(session)


def delete_session(db_sess: Session, sid):
    session = db_sess.query(SocketSession).filter(SocketSession.sid == sid)
    db_sess.delete(session)