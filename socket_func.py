from flask_socketio import SocketIO
from data.db_func import *
from data import db_session
from flask import request


socketio = SocketIO()
@socketio.on("connect")
def connect():
    print("Connected")


# @socketio.on("register")
# def register(username, token):
    # db_sess = db_session.create_session()
    # new_user(db_sess, username, token)
    # db_sess.commit()

    # create_session(db_sess, request.sid, )



