from collections.abc import Callable, Awaitable
import threading
import time
import can


MIN_MSG_INTERVAL_SEC = 0.001


class ICController:
    def __init__(self, can_bus: can.interface.BusABC):
        self.can_bus = can_bus

        self.board = PeriodicMessageBoard()

        self.periodic_msg_thread = threading.Thread(target=self._send_msg_periodically)
        self.running = True
        self.periodic_msg_thread.start()

    def update_speed(self, speed: int):
        """Speed [km/h] (0 - 180)

        CAN ID: 0x0B4
        Speed [km/h]: Data[6] * 0xFF + Data[7] * (180 / 0x421F)
            (When Data[6] = 0x42, Data[7] = 0x1F, speed reaches 180 km/h)

        How to update: Periodically (1/ 100 ms) send the speed value to the CAN bus.
        """
        speed = min(max(speed, 0), 180)

        data5 = speed * 0x421F // 180 // 256
        data6 = speed * 0x421F // 180 % 256
        data = [0, 0, 0, 0, 0, data5, data6, 0]

        self.board.register(
            "speed",
            0.1,
            lambda: can.Message(arbitration_id=0x0B4, data=data, is_extended_id=False),
        )

    def update_shift(self, shift_position: str):
        """Shift position (P, R, N, D, B)

        CAN ID: 0x3BC
        Shift position (B/D):   Data[5] = 0x02 (B), 0x80 (D)
        Shift position (N/R/P): Data[1] = 0x08 (N), 0x10 (R), 0x20 (P)

        How to update: Periodically (1/ 3 sec) send the shift position to the CAN bus.
        """
        if shift_position not in ["B", "D", "N", "R", "P"]:
            shift_position = "P"

        if shift_position == "B":
            data = [0, 0, 0, 0, 0, 0x02, 0, 0]
        elif shift_position == "D":
            data = [0, 0, 0, 0, 0, 0x80, 0, 0]
        elif shift_position == "N":
            data = [0, 0x08, 0, 0, 0, 0, 0, 0]
        elif shift_position == "R":
            data = [0, 0x10, 0, 0, 0, 0, 0, 0]
        elif shift_position == "P":
            data = [0, 0x20, 0, 0, 0, 0, 0, 0]
        else:
            raise NotImplementedError

        self.board.register(
            "shift",
            3.0,
            lambda: can.Message(arbitration_id=0x3BC, data=data, is_extended_id=False),
        )

    def _send_msg_periodically(self):
        while self.running:
            current_time = time.time()
            for periodic_msg in self.board:
                if (
                    current_time - periodic_msg.last_send_time
                    >= periodic_msg.interval_sec
                ):
                    msg = periodic_msg.gen_msg(current_time)
                    self.can_bus.send(msg)
            time.sleep(MIN_MSG_INTERVAL_SEC)

    def stop(self):
        """Stop the periodic sending thread"""
        self.running = False
        self.periodic_msg_thread.join()


class PeriodicMessage:
    def __init__(
        self, msg_id: str, interval_sec: float, msg_generator: Callable[[], can.Message]
    ):
        self.msg_id = msg_id

        self.interval_sec = interval_sec
        self.last_send_time = 0.0  # to update soon after a control status changes

        self.msg_generator = msg_generator

    def gen_msg(self, current_time: float):
        self.last_send_time = current_time
        return self.msg_generator()


class PeriodicMessageBoard:
    """Registrar for periodic messages to be sent on the CAN bus."""

    def __init__(self):
        self._periodic_messages = {}

    def __iter__(self):
        return iter(self._periodic_messages.values())

    def register(
        self, msg_id: str, interval_sec: float, msg_generator: Callable[[], can.Message]
    ):
        """Upsert a periodic message to be sent on the CAN bus."""
        self._periodic_messages[msg_id] = PeriodicMessage(
            msg_id, interval_sec, msg_generator
        )
