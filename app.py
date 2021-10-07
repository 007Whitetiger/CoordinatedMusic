import time

from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import secrets


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(20)
socketIO = SocketIO(app)


starting_time = time.time()
started = False


@app.route('/')
def hello_world():
    return send_from_directory("./svelte-out", "index.html")


@app.route("/assets/<path:svelte_asset>.js")
def file_name_js(svelte_asset):
    return send_from_directory("./svelte-out/assets", f"{svelte_asset}.js", mimetype="text/javascript")


@app.route("/assets/<path:svelte_asset>.css")
def file_name_css(svelte_asset):
    return send_from_directory("./svelte-out/assets", f"{svelte_asset}.css", mimetype="text/css")


@app.route("/assets/<path:svelte_asset>")
def file_name(svelte_asset):
    return send_from_directory("./svelte-out/assets", f"{svelte_asset}")


@socketIO.on("connect")
def on_socket_connect():
    print("connected a socket!")


@socketIO.on("start")
def on_music_start():
    global started, starting_time
    if not started:
        started = True
        starting_time = time.time()

    update_all()


@socketIO.on("update")
def on_socket_update():
    emit('update', time.time() - starting_time)


def update_all():
    new_time = time.time()
    difference = new_time - starting_time
    emit("broadcast_update", difference, broadcast=True)


if __name__ == '__main__':
    socketIO.run(app, host="0.0.0.0", debug=True)
