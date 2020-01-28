import re
import select
from threading import Condition, Thread

import logger
from game.hnefatafl_quitgame import QuitGame
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

            # if session has no connection
            if self.sess.is_down():
                # make gui disconnected
                self._controller.gui_disconnected()

                # if user is playing, inform one about lost of connection
                if self._controller.is_in_game():
                    logger.error("Connection lost. User has to reconnect.")
                    self._controller.quit_game(QuitGame.SESSION_DISCONNECTED)

                # wait for user to input ip and port values and click Connect button
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
                self._update(sock, sources)

                # if connection is lost, try to restart it
                # if fails, close the socket and force user
                # to reconnect with button in menu window
                if self.sess.is_lost():
                    logger.warning("Connection lost, trying to reconnect")
                    self._controller.send_to_chat("Connection lost, trying to reconnect...", bot=True)
                    self.sess.restart()

        # stop connection
        self.sess.stop()

    def connect(self, nick, ip, port):
        logger.debug("CONNECTING {} {} {} {}".format(
            nick, ip, port, self.sess.status
        ))

        # connect only if no connected already
        if self.sess.status == ServerConnection.DOWN:
            # if connection is established, send Connect message
            if self.sess.start(ip, port):
                with self.cv:
                    self.cv.notify()
                self.send_msg(protocol.CC_CONN, nick)
            else:
                self._controller.send_to_menu("Unable to connect to server.")

    def _update(self, sock, sources):
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

            if self.buffer != "{<}" and self.buffer != "{>}":
                logger.debug("received [{}] from [{}]".format(self.buffer, self.sess.sock.getpeername()))

        except (ConnectionAbortedError, OSError, UnicodeDecodeError):
            self.sess.stop()
            self.sess.status = ServerConnection.LOST
            logger.error("Unable to receive data from server.")

        # message from server
        if len(self.buffer) > 0:
            # if data in valid format
            if re.fullmatch(protocol.RGX_VALID_FORMAT, self.buffer):
                # parse data (length is > 1, when more messages were received on select
                data = re.findall(protocol.RGX_DATA, self.buffer)
                # and process data
                self._process(data)
            # wrong protocol format
            else:
                self.sess.stop()
                self.sess.status = ServerConnection.DOWN
                logger.error("Invalid data received from server.")

        # server logged out
        elif len(self.buffer) == 0:
            self.sess.stop()
            self.sess.status = ServerConnection.DOWN
            logger.warning("Server disconnected.")

        # error while receiving
        else:
            self.sess.stop()
            self.sess.status = ServerConnection.LOST
            logger.error("Corrupted data received from server.")

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
        except (ConnectionAbortedError, OSError):
            self.sess.stop()
            self.sess.status = ServerConnection.LOST
            logger.error("Unable to send data to server.")

    def _process(self, data):
        # whole message in brackets {...} split with coma to get its elements
        for element in data:
            processed_data = re.split(protocol.RGX_ELMS, element)

            self._route_request(processed_data)

    def _route_request(self, request):
        # go through each element in request
        # eg. message was {ig,ty,on:nick} and now the 'request' list is ["ig", "ty", "on", "nick"]
        while len(request) > 0:
            # get first element
            element = request.pop(0)

            # ping
            if element == protocol.OP_PING:
                self.send_msg(protocol.OP_PONG)

            # pong
            elif element == protocol.OP_PONG:
                self.sess.status = ServerConnection.UP

            # connection successful
            elif element == protocol.SC_RESP_CONN:
                self._controller.gui_connected()

            # reconnection successful
            elif element == protocol.SC_RESP_RECN:
                self._controller.gui_connected()
                element = request.pop(0)

                # reconnection in lobby
                if element == protocol.SC_IN_LOBBY:
                    self._controller.send_to_menu("Reconnected, in Lobby.")

                # reconnection in game
                elif element == protocol.SC_IN_GAME:
                    self._controller.send_to_menu("Reconnected, in Game.")

                    # indexes according to the protocol
                    turn = request[0] == protocol.SC_TURN_YOU
                    nick_opn = request[2]
                    pf = request[4]

                    # reset game, thanks to message received from server
                    self._controller.reset_game(turn, nick_opn, pf)
                    break

            # game leave successful
            elif element == protocol.SC_RESP_LEAVE:
                self._controller.send_to_menu("Game left.")

            # in lobby message
            elif element == protocol.SC_IN_LOBBY:
                self._controller.send_to_menu("In Lobby.")

            # in game message, start of new game
            elif element == protocol.SC_IN_GAME:
                # indexes according to the protocol
                turn = request[0] == protocol.SC_TURN_YOU
                nick_opn = request[2]

                # start game, thanks to message received from server
                self._controller.start_game(turn, nick_opn)
                break

            # local move was valid
            elif element == protocol.SC_MV_VALID:
                self._controller.move_self()

            # game was won
            elif element == protocol.SC_GO_WIN:
                self._controller.quit_game(QuitGame.GAME_WIN)

            # game was lost
            elif element == protocol.SC_GO_LOSS:
                self._controller.quit_game(QuitGame.GAME_LOSS)

            # opponent's move
            elif element == protocol.SC_OPN_MOVE:
                move = request.pop(0)
                self._controller.move_opponent(int(move[:2]), int(move[2:4]), int(move[4:6]), int(move[6:]))

            # opponent left game
            elif element == protocol.SC_OPN_LEAVE:
                self._controller.quit_game(QuitGame.OPN_LEFT)

            # opponent is lost
            elif element == protocol.SC_OPN_LOST:
                self._controller.send_to_chat("Opponent lost connection, reconnection possible...", bot=True)

            # opponent disconnected
            elif element == protocol.SC_OPN_DISC:
                self._controller.send_to_chat("Opponent disconnected, reconnection possible...", bot=True)

            # opponent reconnected
            elif element == protocol.SC_OPN_RECN:
                self._controller.send_to_chat("Opponent reconnected.", bot=True)

            # opponent is gone from server
            elif element == protocol.SC_OPN_GONE:
                self._controller.quit_game(QuitGame.OPN_GONE)

            # too many players on server
            elif element == protocol.SC_MANY_CLNT:
                self._controller.gui_disconnected()
                self._controller.send_to_menu("Too many clients on server, try again later.")

            # nick already used
            elif element == protocol.SC_NICK_USED:
                self._controller.gui_disconnected()
                self._controller.send_to_menu("Nick already used, try different one.")

            # server kicked user
            elif element == protocol.SC_KICK:
                self._controller.gui_disconnected()
                self._controller.send_to_menu("You have been kicked from server.")
                self._controller.quit_game(QuitGame.SERVER_KICK)

            # server shutdown
            elif element == protocol.SC_SHDW:
                self._controller.gui_disconnected()
                self._controller.send_to_menu("Server shutdown.")
                self._controller.quit_game(QuitGame.SERVER_SHUTDOWN)

                # chat message from opponent
            elif element == protocol.OP_CHAT:
                msg = request.pop(0)
                self._controller.send_to_chat(msg, bot=False)

            # unknown, never should get here
            else:
                logger.warning("Invalid message processed.")

    def pr_statistics(self):
        logger.info("Bytes received in total: {}".format(self.bytes_recv))
        logger.info("Bytes sent in total: {}".format(self.bytes_send))
        logger.info("Count of reconnection in total: {}".format(self.cnt_recn))
