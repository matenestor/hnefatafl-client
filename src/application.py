import signal

import logger
from net import protocol
from net.network import Network
from gui.gui import Gui
from game.hnefatafl import Hnefatafl
from gui.click_state import Click


class Application:
    def __init__(self):
        # register signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # flag for activity before quit
        self.is_running = True
        self.is_sig = False

        # user's attributes
        self.nick = None
        self.ip = None
        self.port = None

        # create Hnefatafl
        self.hnef = Hnefatafl()

        # create client network
        self.net = Network(self)

        # create gui
        self.gui = Gui(self)

    def _signal_handler(self, sig, frame):
        self.is_running = False
        self.is_sig = True
        self.gui.destroy()
        logger.info("Closing client with signal.")

    def run(self):
        # start network
        self.net.start()

        # start the application -- has to be last command,
        # because it runs, until the window is closed == everything else freezes
        self.gui.mainloop()

        # if windows was closed with button or cross, set flag in standard way
        self.is_running = False

        if not self.is_sig:
            logger.info("Closing client standard way.")

        # notify network thread, in order to end it
        with self.net.cv:
            self.net.cv.notify()
        # join Network thread
        self.net.join()

        # print statistics through lifetime
        self.net.pr_statistics()

    def hnef_connect(self, nick, ip, port):
        self.nick = nick
        self.ip = "127.0.0.1" if ip == "localhost" else ip
        self.port = int(port)

        # connect to server
        self.net.connect(self.nick, self.ip, self.port)

    def gui_connected(self):
        self.gui.make_connected()

    def gui_disconnected(self):
        self.gui.make_disconnected()

    def send_to_server(self, code, value=None):
        self.net.send_msg(code, value)

    def send_to_chat(self, msg, bot):
        self.gui.chat_msg_server(msg, bot, self.hnef.nick_opponent)

    def send_to_menu(self, msg):
        self.gui.set_state(msg)

    def is_in_game(self):
        # True, if somebody is on turn -- means game is on
        return self.hnef.on_turn is not None

    def start_game(self, turn, opn_name):
        # start new game in Hnefatafl class
        self.hnef.new_game(turn, opn_name)
        # switch frame in GUI, so user can play
        self.gui.new_game(self.nick, self.hnef.game_state, self.hnef.pf, self.hnef.allowed_squares)
        # tell player, who is on turn
        self.send_to_chat("'{}' is black and on turn.".format(self.nick if turn else opn_name), bot=True)

    def leave_game(self):
        self.send_to_server(protocol.CC_LEAV)
        self.hnef.quit_game()

    def reset_game(self, turn, nick_opn, pf):
        # reset game in Hnefatafl class
        self.hnef.reset_game(turn, nick_opn, pf)
        # not actually new game -- it has state like in received message from server
        self.gui.new_game(self.nick, self.hnef.game_state, self.hnef.pf, self.hnef.allowed_squares)

    def quit_game(self, result):
        # quit game after game-over
        self.hnef.quit_game()
        self.gui.quit_game(result)

    def handle_click(self, x_pos, y_pos):
        redraw = True

        # playfield have not been clicked
        if self.hnef.game_state == Click.THINKING:
            # find fields where player may move after click on stone
            self.hnef.find_placeable_fields(x_pos, y_pos)

            # set position, which is being moved from
            self.hnef.x_from = x_pos
            self.hnef.y_from = y_pos
            # change state to clicked
            self.hnef.game_state = Click.CLICKED

        # playfield have been clicked
        elif self.hnef.game_state == Click.CLICKED:
            # field without stone have been clicked -- make a move
            if self.hnef.is_field(x_pos, y_pos):
                # send move message to server
                move = self.compose_move_msg([self.hnef.x_from, self.hnef.y_from, x_pos, y_pos])
                self.send_to_server(protocol.CC_MOVE, value=move)

                # save also position which is being moved to and move after server's confirmation of valid move
                self.hnef.x_to = x_pos
                self.hnef.y_to = y_pos

                # playfield is updated and redrawn after server's MOVE_VALID message
                redraw = False

            # field with same stone have been clicked -- go back to thinking state
            elif self.hnef.is_same_stone(x_pos, y_pos):
                # find stones, which player can move with
                self.hnef.find_movables_stones()

                # reset position, which is being moved from
                self.hnef.x_from = None
                self.hnef.y_from = None
                # change state to thinking
                self.hnef.game_state = Click.THINKING

            # field with other stone have been clicked -- find allowed squares again
            else:
                # find stones, which player can move with
                self.hnef.find_movables_stones()
                # find fields where player may move after click on stone
                self.hnef.find_placeable_fields(x_pos, y_pos)

                # set position, which is being moved from
                self.hnef.x_from = x_pos
                self.hnef.y_from = y_pos

        # update playfield in gui
        if redraw:
            self.gui.pf_update(self.hnef.game_state, self.hnef.pf, self.hnef.allowed_squares)

    def move_self(self):
        # move chosen stone (after server confirmation -- so use cached values)
        self.hnef.move(self.hnef.x_from, self.hnef.y_from, self.hnef.x_to, self.hnef.y_to)
        # check captures of local player -- capturing white if local is black
        self.hnef.check_captures(self.hnef.is_surrounded_white if self.hnef.black else self.hnef.is_surrounded_black)
        # after move, player cannot move anything
        self.hnef.allowed_squares.clear()

        # update playfield in gui
        self.gui.pf_update(self.hnef.game_state, self.hnef.pf, self.hnef.allowed_squares)

    def move_opponent(self, x_from, y_from, x_to, y_to):
        # move opponent's piece
        self.hnef.move(x_from, y_from, x_to, y_to)
        # check captures of opponent player -- capturing black if local is black
        self.hnef.check_captures(self.hnef.is_surrounded_black if self.hnef.black else self.hnef.is_surrounded_white)
        # get pieces of player, who is on turn now
        self.hnef.find_movables_stones()

        # update playfield in gui
        self.gui.pf_update(self.hnef.game_state, self.hnef.pf, self.hnef.allowed_squares)

    def compose_move_msg(self, coordinates):
        move = ""

        for coor in coordinates:
            # if number has only one place, so append 0 at beginning according to protocol
            # else it is 10 with two places
            move += "0" + str(coor) if coor < 10 else str(coor)

        return move
