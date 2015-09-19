from kulka import request
from kulka.connection.exceptions import ConnectionLost
from kulka.connection import Connection


class Kulka(object):

    def __init__(self, addr):
        self._addr = addr
        self._connection = Connection.connect(addr)
        self._sequence = 0

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self._connection.close()

    def sequence(self):
        self._sequence = (self._sequence + 1) & 0xFF
        return self._sequence

    def _send(self, request):
        request.sequence = self.sequence()

        try:
            self._connection.send(request.tobytes())
            self._connection.recv(1024)
        except ConnectionLost:
            self._reconnect()

    def _reconnect(self):
        self._connection.close()
        self._connection = Connection.connect(self._addr)

    def set_inactivity_timeout(self, timeout):
        return self._send(request.SetInactivityTimeout(timeout))

    def set_rgb(self, red, green, blue, flag=0):
        return self._send(request.SetRGB(red, green, blue, flag))

    def roll(self, speed=0, heading=0, state=1):
        return self._send(request.Roll(speed, heading, state))

    def sleep(self, wakeup=0, macro=0, orb_basic=0):
        return self._send(request.Sleep(wakeup, macro, orb_basic))
