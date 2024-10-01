import can
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from typing import Any

from nhp10.ic_controller import ICController

socketio = SocketIO()


def create_app(controller: ICController) -> Flask:
    app = Flask(__name__)
    socketio.init_app(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    @socketio.on("update_speed")
    def handle_speed(data):
        speed = data["speed"]
        controller.update_speed(speed)
        emit("speed_updated", {"speed": speed}, broadcast=True)

    @socketio.on("update_shift")
    def handle_shift(data):
        shift = data["shift"]
        controller.update_shift(shift)
        emit("shift_updated", {"shift": shift}, broadcast=True)

    @socketio.on("update_ev_mode")
    def handle_ev_mode(data):
        ev_mode = data["ev_mode"]
        controller.update_ev(ev_mode)
        emit("ev_updated", {"ev_mode": ev_mode}, broadcast=True)

    return app
