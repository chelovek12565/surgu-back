from flask_socketio import SocketIO, emit, send, join_room, leave_room
from data.db_func import *
from data.db_func import new_message as db_new_message
from data import db_session
from flask import request

socketio = SocketIO()


@socketio.on("connect")
def connect():
    print("Connected")


@socketio.on("user_connect_chat")
def user_connect(token, chat_id):
    db_sess = db_session.create_session()
    create_session(
        db_sess=db_sess,
        sid=request.sid,
        chat_id=chat_id,
        token=token
    )
    join_room(str(chat_id))
    print("joined", chat_id)


@socketio.on("disconnect")
def user_disconnect():
    print(request.sid)
    db_sess = db_session.create_session()
    session = db_sess.query(SocketSession).filter(SocketSession.sid == request.sid).first()
    leave_room(str(session.chat_id))
    delete_session(db_sess=db_sess,
                   sid=request.sid)
    print("leaved", session.chat_id)


@socketio.on("new_message")
def new_message(chat_id, text, user_id):
    db_sess = db_session.create_session()
    db_new_message(
        db_sess=db_sess,
        chat_id=chat_id,
        text=text,
        user_id=user_id
    )
    # sids = get_sid_by_chat(chat_id, db_sess)
    # del sids[sids.index(request.sid)]
    # for sid in sids:
    emit("chat", {"text": text, "username": get_username_by_id(user_id, db_sess=db_sess), "user_id": user_id}, to=str(chat_id))




# @socketio.on("register")
# def register(username, token):
    # db_sess = db_session.create_session()
    # new_user(db_sess, username, token)
    # db_sess.commit()

    # create_session(db_sess, request.sid, )



