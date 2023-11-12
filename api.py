from flask import Flask, request, jsonify
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


@app.route("/parse_task")
def parse_task():
    token = request.json["token"]
    return jsonify(parse_card(token))


@app.route("/send_task")
def send_task():
    db_sess = db_session.create_session()

    token = request.json["token"]
    user = get_user_by_token(token, db_sess)
    task_id = request.json["task_id"]
    chat_id = request.json["chat_id"]
    task = parse_one_task(task_id, token)
    out = f"Эй! Мне нужна помощь с таском {task['title']}\n" \
    f"Проект: {task['project_name']}\n"
    if task['description']:
        out += f"Описание: {task['description']}\n"
    out += f"Дата: {task['date']}"

    new_message(chat_id, out, user.id, db_sess)
    db_sess.commit()
    socketio.emit("chat", {"text": out, "username": user.username}, to=str(chat_id))
    return "ok"


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


@app.route("/edit_chat_name", methods=["POST"])
def edit_chat():
    chat_id = request.json["chat_id"]
    new_name = request.json["new_name"]
    user_id = request.json["user_id"]

    db_sess = db_session.create_session()
    chat_info = get_chatinfo_by_chatid(chat_id, db_sess)

    if user_id == chat_info.admin_id:
        chat_info.name = new_name
        db_sess.commit()
    else:
        return "trying to change name as non-admin user"
    return "ok"


@app.route("/users_chats/<user_id>", methods=["GET"])
def users_chats(user_id):
    db_sess = db_session.create_session()
    user = get_user_by_id(user_id, db_sess)
    out = [get_chat_preview(chat_id, db_sess) for chat_id in map(int, user.chats.split())]
    return jsonify(out)


@app.route("/delete_from_chat", methods=["DELETE"])
def api_delete_from_chat():
    db_sess = db_session.create_session()
    chat_id = request.json["chat_id"]
    member_id = request.json["member_id"]
    delete_from_chat(chat_id, member_id, db_sess)
    chat_user_delete_message(chat_id, member_id, db_sess)
    socketio.emit("leaved_chat", {"user_id": member_id}, to=str(chat_id))
    return "ok"


@app.route("/user/by_token/<token>", methods=["GET"])
def api_user_by_token(token):
    db_sess = db_session.create_session()
    return jsonify(user_pretty(get_user_by_token(token, db_sess)))


@app.route("/user/by_id/<user_id>", methods=["GET"])
def api_user_by_id(user_id):
    db_sess = db_session.create_session()
    return jsonify(user_pretty(get_user_by_id(user_id, db_sess)))


@app.route("/chat/<chat_id>", methods=["GET"])
def chat_messages(chat_id):
    db_sess = db_session.create_session()
    messages = get_messages_in_chat(chat_id, db_sess)
    out = [list(row) for row in messages]
    return jsonify(out)


@app.route("/chat/members/<chat_id>")
def chat_members(chat_id):
    db_sess = db_session.create_session()
    chat_info = get_chatinfo_by_chatid(chat_id, db_sess)
    members = map(int, chat_info.members.split())
    out = [get_user_by_id(mem_id, db_sess).to_dict() for mem_id in members]
    return jsonify(out)


@app.route("/chat_short/<chat_id>", methods=["GET"])
def chat_short(chat_id):
    db_sess = db_session.create_session()
    return jsonify(get_chat_preview(chat_id, db_sess))


@app.route("/last_messages", methods=["POST"])
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
socketio.run(app, port=6000, allow_unsafe_werkzeug=True)