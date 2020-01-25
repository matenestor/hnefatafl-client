import socket

from state import State


class Session:
    def __init__(self, ip, port):
        # server ip address for this session
        self.addrIp = ip
        # server port for this session
        self.port = port

        # flag indicating server connection
        self.has_connection = False
        # flag indicating server status
        self.srv_status = State.DOWN

        # create socket
        self.sock = None

    def socket_create(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get_sock(self):
        return self.sock

    def is_expired(self):
        return self.srv_status == State.DOWN
