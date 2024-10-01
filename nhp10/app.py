import can
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from typing import Any

from nhp10.ic_controller import ICController

socketio = SocketIO()

def create_app(controller: ICController) -> Flask:
    app = Flask(__name__)
    socketio.init_app(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @socketio.on('update_speed')
    def handle_speed(data):
        speed = data['speed']
        controller.update_speed(speed)
        emit('speed_updated', {'speed': speed}, broadcast=True)

    @socketio.on('update_odo')
    def handle_odo(data):
        odo = data['odo']
        # Send ODO update via CAN bus
        message = can.Message(arbitration_id=0x124, data=[odo])
        can_bus.send(message)
        emit('odo_updated', {'odo': odo}, broadcast=True)

    @socketio.on('update_battery')
    def handle_battery(data):
        battery = data['battery']
        # Send battery update via CAN bus
        message = can.Message(arbitration_id=0x125, data=[battery])
        can_bus.send(message)
        emit('battery_updated', {'battery': battery}, broadcast=True)

    @socketio.on('update_gear')
    def handle_gear(data):
        gear = data['gear']
        # Send gear update via CAN bus
        message = can.Message(arbitration_id=0x126, data=[ord(gear)])
        can_bus.send(message)
        emit('gear_updated', {'gear': gear}, broadcast=True)

    @socketio.on('update_seatbelt')
    def handle_seatbelt(data):
        seatbelt = data['seatbelt']
        # Send seatbelt status update via CAN bus
        message = can.Message(arbitration_id=0x127, data=[int(seatbelt)])
        can_bus.send(message)
        emit('seatbelt_updated', {'seatbelt': seatbelt}, broadcast=True)

    @socketio.on('update_turn_signal')
    def handle_turn_signal(data):
        turn_signal = data['turn_signal']
        # Send turn signal status update via CAN bus
        message = can.Message(arbitration_id=0x128, data=[int(turn_signal)])
        can_bus.send(message)
        emit('turn_signal_updated', {'turn_signal': turn_signal}, broadcast=True)

    return app
