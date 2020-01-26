import socket

from app import logger
from app.net.server_connection import ServerConnection


class Session:
    def __init__(self, ip, port):
        # server ip address for this session
        self.addrIp = ip
        # server port for this session
        self.port = port

        # flag indicating connection status
        self.status = ServerConnection.DOWN

        # create socket
        self.sock = None

    def socket_create(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get_sock(self):
        return self.sock

    def is_expired(self):
        return self.status == ServerConnection.DOWN

    def connect_to_server(self):
        # TODO also patch
        try:
            self.sock.connect((self.addrIp, self.port))
            self.status = ServerConnection.UP

            logger.info("Connected on socket with local ip [{}] on port [{}].".format(self.sock.getsockname()[0], self.sock.getsockname()[1]))
            logger.info("Connected to server with ip [{}] on port [{}].".format(self.sock.getpeername()[0], self.sock.getpeername()[1]))

        except ConnectionRefusedError:
            self.status = ServerConnection.DOWN
            logger.error("Server is not available.")

    def reset_socket(self):
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
