import socket

import logger
from net.server_connection import ServerConnection


class Session:
    def __init__(self):
        # server ip address for this session
        self.ip_addr = ""
        # server port for this session
        self.port = 0

        # flag indicating connection status
        self.status = ServerConnection.DOWN

        # create socket
        self.sock = None

    def start(self, ip, port):
        # set connection values
        self.ip_addr = ip
        self.port = port

        # create socket and connect with it
        self._socket_create()
        self._connect_to_server()

        # return True if start was successful
        return self.sock is not None

    def restart(self):
        # restart socket and connect again
        self._socket_restart()
        self._connect_to_server()

    def stop(self):
        self._socket_close()

    def _socket_create(self):
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    def _socket_restart(self):
        self._socket_close()
        self._socket_create()

    def _socket_close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def _connect_to_server(self):
        try:
            self.sock.connect((self.ip_addr, self.port))
            self.status = ServerConnection.UP

            logger.info("Connected on socket with local ip [{}] on port [{}].".format(self.sock.getsockname()[0], self.sock.getsockname()[1]))
            logger.info("Connected to server with ip [{}] on port [{}].".format(self.sock.getpeername()[0], self.sock.getpeername()[1]))

        except ConnectionRefusedError:
            self._socket_close()
            self.status = ServerConnection.DOWN
            logger.info("Connection to server with ip [{}] on port [{}] refused.".format(self.ip_addr, self.port))

        except InterruptedError:
            self._socket_close()
            self.status = ServerConnection.DOWN
            logger.info("Connection to server with ip [{}] on port [{}] interrupted.".format(self.ip_addr, self.port))

    def is_running(self):
        return self.status == ServerConnection.UP or self.status == ServerConnection.PING

    def is_lost(self):
        return self.status == ServerConnection.LOST

    def is_down(self):
        return self.status == ServerConnection.DOWN
