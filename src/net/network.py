import re
import select
import sys
from threading import Condition, Thread

import logger
from net import protocol
from net.ups_session import Session
from net.server_connection import ServerConnection


class Network(Thread):
    # seconds before timeout on select
    _TIMEOUT = 5
    # size of buffer for receiving
    _BUFF_SIZE = 1024

    def __init__(self, cont):
        super().__init__(daemon=False)

        # application is controller of network
        self._controller = cont

        # condition variable for this thread to make it wait,
        # when waiting for ip and port values
        self.cv = Condition()

        # received bytes in total
        self.bytes_recv = 0
        # sent bytes in total
        self.bytes_send = 0
        # count of reconnection
        self.cnt_recn = 0

        # buffer to receive to
        self.buffer = ""

        # clients session to server
        self.sess = Session()

    def run(self):
        # while application is opened
        while self._controller.is_running:

            # if session has no connection, wait for user to input ip and port
            # values and click Connect button
            if self.sess.is_down():
                with self.cv:
                    self.cv.wait()

                # if application is not running after notify, break and end
                if not self._controller.is_running:
                    break

            # get socket from current session
            sock = self.sess.sock

            # the only socket to read from is server
            sources = [sock]

            # while connected to server, update self -- recv, send
            while self.sess.is_running() and self._controller.is_running:
                self.update(sock, sources)

                # if connection is lost, try to restart it
                # if fails, close the socket and force user
                # to reconnect with button in menu window
                if self.sess.is_lost():
                    self.sess.restart()

        # stop connection
        self.sess.stop()

    def connect(self, nick, ip, port):
        connected = False

        # connect only if no connected already
        if self.sess.status == ServerConnection.DOWN:
            # if connection is established, send Connect message
            connected = self.sess.start(ip, port)
            if connected:
                with self.cv:
                    self.cv.notify()
                self.send_msg(protocol.CC_CONN, nick)

        return connected

    def update(self, sock, sources):
        # block, until message from server is received
        fds_read, _, fds_except = select.select(sources, [], sources, Network._TIMEOUT)

        # socket went bad, some problem with server connection
        if sock in fds_except:
            self.sess.status = ServerConnection.DOWN

        # server send a message
        elif sock in fds_read:
            self.receive_msg()

        # timeout
        else:
            # server was already pinged and have not responded since
            if self.sess.status == ServerConnection.PING:
                # mark server as Lost
                self.sess.status = ServerConnection.LOST;
            # server did not send ping message for long time
            else:
                # ping server
                self.sess.status = ServerConnection.PING
                self.send_msg(protocol.OP_PING)

    def receive_msg(self):
        try:
            self.buffer = self.sess.sock.recv(Network._BUFF_SIZE).decode("utf8")
            logger.debug("received [{}] from [{}]".format(self.buffer, self.sess.sock.getpeername()))
        except ConnectionAbortedError:
            self.sess.stop()
            self.sess.status = ServerConnection.LOST
            logger.fatal("Unable to receive data from server.")

        # message from server
        if len(self.buffer) > 0:
            # if data in valid format
            if re.fullmatch(protocol.RGX_VALID_FORMAT, self.buffer):
                # parse data (length is > 1, when more messages were received on select
                data = re.findall(protocol.RGX_DATA, self.buffer)
                # and process data
                self.process(data)
            # wrong protocol format
            else:
                self.sess.stop()
                self.sess.status = ServerConnection.DOWN
                logger.fatal("Invalid data received from server.")

        # server logged out
        elif len(self.buffer) == 0:
            self.sess.stop()
            self.sess.status = ServerConnection.DOWN
            logger.error("Server disconnected.")

        # error while receiving
        else:
            self.sess.stop()
            self.sess.status = ServerConnection.LOST
            logger.fatal("Corrupted data received from server.")

    def send_msg(self, code, value=None):
        # opening tag
        msg = protocol.OP_SOH + code

        # if code has some value (c-connect, m-move), append it also
        if value is not None:
            msg += protocol.OP_INI + value

        # closing tag
        msg += protocol.OP_EOT

        try:
            # send message to server
            self.sess.sock.sendall(msg.encode("utf8"))
        except ConnectionAbortedError:
            self.sess.stop()
            self.sess.status = ServerConnection.LOST

    def process(self, data):
        # whole message in brackets {...} split with coma to get its elements
        for element in data:
            processed_data = re.split(protocol.RGX_ELMS, element)

            self.route_request(processed_data)

    def route_request(self, request):
        # TODO finish this
        # go through each element in request
        # eg. message was {ig,ty,on:nick} and now the 'request' list is ["ig", "ty", "on", "nick"]
        for element in request:
            if element == protocol.OP_PING:
                self.send_msg(protocol.OP_PONG)

            elif element == protocol.OP_PONG:
                self.sess.status = ServerConnection.UP

            elif element == protocol.SC_RESP_CONN:
                self._controller.send_to_menu("Connected.")

    def pr_statistics(self):
        logger.info("Bytes received in total: {}".format(self.bytes_recv))
        logger.info("Bytes sent in total: {}".format(self.bytes_send))
        logger.info("Count of reconnection in total: {}".format(self.cnt_recn))
