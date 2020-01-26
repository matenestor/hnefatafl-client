import select
import socket
import sys

import logger
import protocol
from ups_session import Session
from ups_state import UpsConnection


class Client:
    def __init__(self, ip=None, port=None):
        # seconds before timeout on select
        self.TIMEOUT = 5

        # server default ip address
        self.addrIp = ip if ip is not None else "0.0.0.0"
        # server default port
        self.port = port if port is not None else 4567

        # received bytes in total
        self.bytes_recv = 0
        # sent bytes in total
        self.bytes_send = 0
        # count of reconnection
        self.cnt_recn = 0

        # buffer to receive to
        self.buffer = ""
        # size of buffer for receiving
        self.buffSize = 1024

        # clients session to server
        self.sess = None

        logger.info("Client initialized.")

    def __del__(self):
        logger.info("Bytes received in total: {}".format(self.bytes_recv))
        logger.info("Bytes sent in total: {}".format(self.bytes_send))
        logger.info("Count of reconnection in total: {}".format(self.cnt_recn))

    def create_session(self):
        self.sess = Session(self.addrIp, self.port)

    def run(self):
        assert self.sess is not None, "Session is None"

        # get socket from current session
        sock = self.sess.get_sock()

        # the only socket to read from is server
        sources = [sock]

        while not self.sess.is_expired():
            # block, until message from server is received
            fds_read, _, fds_except = select.select(sources, [], sources, self.TIMEOUT)

            # socket went bad, some problem with server connection
            if sock in fds_except:
                self.has_connection = False
                self.srv_status = UpsConnection.DOWN

        # server send a message
            elif sock in fds_read:
                self.receive_msg(self.sess)

            # timeout
            else:
                if self.srv_status == UpsConnection.PING:
                    self.srv_status = UpsConnection.LOST;
                    self.has_connection = False
                else:
                    self.srv_status = UpsConnection.PING
                    self.send_msg(self.sess, protocol.OP_PING)

    def receive_msg(self, sess):
        # TODO patch
        print(sys.stderr, 'received "%s" from %s' % (self.buffer, self.sock.getpeername()))

        try:
            buffer = sess.get_sock.recv(self.buffSize).decode("utf8")
        except:
            logger.debug("fucked on tryexc")

        if len(buffer) > 0:
            logger.debug(buffer)
        else:
            logger.debug("fucked")

    def send_msg(self, sess, _msg):
        # TODO surround with catch
        msg = protocol.OP_SOH + _msg + protocol.OP_EOT
        self.sock.sendall(msg.encode("utf8"))


    # def myreceive(self):
    #     chunks = []
    #     bytes_recd = 0
    #     while bytes_recd < self.buffSize:
    #         chunk = self.sock.recv(min(self.buffSize - bytes_recd, 2048))
    #         if chunk == b'':
    #             raise RuntimeError("socket connection broken")
    #         chunks.append(chunk)
    #         bytes_recd = bytes_recd + len(chunk)
    #     return b''.join(chunks)

