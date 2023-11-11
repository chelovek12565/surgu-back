from flask import Flask, request
from data import db_session
from data.__all_models import *
from data.db_func import *
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

from socket_func import socketio
socketio.init_app(app, cors_allowed_origins="*")

db_session.global_init("./data/main.db")


@app.route("/new_message", methods=["POST"])
def main():
    '''
    json.keys: chat_id, text, user_id
    '''
    db_sess = db_session.create_session()
    new_message(
        db_sess=db_sess,
        **request.json
    )
    return "ok"


@app.route("/auth", methods=["POST"])
def auth():
    '''
    token
    '''
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.token == request.json["token"]).first()
    if not user:
        new_user(db_sess, **request.json)
    db_sess.commit()
    return "ok"


@app.route("/new_chat", methods=["POST"])
def add_chat():
    name, members, admin_id = request.json["name"], request.json["members"], request.json["admin_id"]
    members.append(admin_id)
    db_sess = db_session.create_session()
    generate_chat(name, members, admin_id, db_sess)
    return "ok"


# app.run(port=123)
socketio.run(app, port=5000, allow_unsafe_werkzeug=True)