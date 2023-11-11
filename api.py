from flask import Flask, request, jsonify
from data import db_session
from data.__all_models import *
from data.db_func import *
from flask_cors import CORS, cross_origin
from flask_socketio import emit

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

from socket_func import socketio
socketio.init_app(app, cors_allowed_origins="*")

db_session.global_init("./data/main.db")


@app.route("/invite", methods=["POST"])
def invite():
    """
    members_id, chat_id, by
    """
    db_sess = db_session.create_session()
    add_chat_members(db_sess, request.json["members_id"], request.json["chat_id"])
    by_username = get_username_by_id(request.json["by"], db_sess)
    for mem_id in request.json["members_id"]:
        socketio.emit("invite", {"who": get_username_by_id(mem_id, db_sess), "by": by_username},
             to=str(request.json["chat_id"]))
    return "ok"


@app.route("/delete_from_chat", methods=["DELETE"])
def api_delete_from_chat():
    db_sess = db_session.create_session()
    chat_id = request.json["chat_id"]
    member_id = request.json["member_id"]
    delete_from_chat(chat_id, member_id, db_sess)
    ch
    socketio.emit("leaved_chat", {"user_id": member_id})


@app.route("/user/by_token/<token>", methods=["GET"])
def api_user_by_token(token):
    db_sess = db_session.create_session()
    return jsonify(get_user_by_token(token, db_sess).to_dict())


@app.route("/user/by_id/<user_id>", methods=["GET"])
def api_user_by_id(user_id):
    db_sess = db_session.create_session()
    return jsonify(get_user_by_id(user_id, db_sess).to_dict())


@app.route("/chat/<chat_id>", methods=["GET"])
def chat_messages(chat_id):
    db_sess = db_session.create_session()
    messages = get_messages_in_chat(chat_id, db_sess)
    out = [list(row) for row in messages]
    return jsonify(out)


@app.route("/last_messages", methods=["GET"])
def last_messages():
    """
    index - отсчет с нуля
    chat_id

    вывод:
    [
        [id, text, user_id, datetime]
    ]
    """
    db_sess = db_session.create_session()

    index = request.json["index"]
    chat_id = request.json["chat_id"]
    messages = list(reversed(get_messages_in_chat(chat_id, db_sess)))
    out = [list(row) for row in messages[index * 100: (index + 1) * 100 - 1]]
    # print(out)
    return jsonify(out)


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
    if admin_id not in members:
        members.append(admin_id)
    db_sess = db_session.create_session()
    generate_chat(name, members, admin_id, db_sess)
    return "ok"


# app.run(port=123)
socketio.run(app, port=5000, allow_unsafe_werkzeug=True)