from flask_socketio import SocketIO


socketio = SocketIO()
@socketio.on("connect")
def connect():
    print("Client connected")


