from flask import Flask, request
from data import db_session
from data.__all_models import *
from data.db_func import *


app = Flask(__name__)

from socket_func import socketio
socketio.init_app(app)

db_session.global_init()


# @app.route("/")
# def main():
    # return "ok"


@app.route("/add_user", methods=["POST"])
def add_user():
    db_sess = db_session.create_session()
    new_user(db_sess, request.json)
    db_sess.commit()
    return "ok"


@app.route("/auth", methods=["POST"])
def add_user():
    db_sess = db_session.create_session()
    new_user(db_sess, request.json)
    db_sess.commit()
    return "ok"


# app.run(port=123)
socketio.run(app, port=5000)