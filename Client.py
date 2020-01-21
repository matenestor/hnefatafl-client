import socket
import logger

# flag for activity before ctrl+c
is_client_alive = True


class Client:
    def __init__(self, ip=None, port=None):
        # server default ip address
        self.addrIp = ip if ip is not None else "0.0.0.0"
        # server default port
        self.port = port if port is not None else 4567
        # create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # size of buffer for receiving
        self.buffSize = 1024

        # received bytes in total
        self.bytes_recv = 0
        # sent bytes in total
        self.bytes_send = 0
        # count of reconnection
        self.cnt_recn = 0

        logger.info("Client initialized.")

    def __del__(self):
        logger.info("Bytes received in total: {}".format(self.bytes_recv))
        logger.info("Bytes sent in total: {}".format(self.bytes_send))
        logger.info("Count of reconnection in total: {}".format(self.cnt_recn))

    def init(self):
        pass

    def reset_socket(self):
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.addrIp, self.port))

    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < self.buffSize:
            chunk = self.sock.recv(min(self.buffSize - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

