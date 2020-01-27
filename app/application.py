import signal

from app import logger
from app.net import protocol
from app.net.network import Network
from app.gui.gui import Gui
from app.game.hnefatafl import Hnefatafl
from app.gui.click_state import Click


class Application:
    def __init__(self):
        # register ctrl+c event
        signal.signal(signal.SIGINT, self.signal_handler)

        # flag for activity before ctrl+c
        self.is_running = True

        # user's attributes
        self.nick = None
        self.ip = None
        self.port = None

        # create Hnefatafl
        self.hnef = Hnefatafl()

        # TODO start in thread
        # create client network
        # self.net = Network()

        # create gui
        self.gui = Gui(self)
        # start the application -- has to be last command,
        # because it runs, until the window is closed == everything else freezes
        self._start_game(True, "opponent")  # TODO remove this line
        self.gui.mainloop()

    def signal_handler(self, sig, frame):
        self.is_running = False
        logger.info("Closing client.")

    def hnef_connect(self, nick, ip, port):
        self.nick = nick
        self.ip = ip
        self.port = port

        pass
        # TODO connect to server ! if not connected already !
        #  on success disable connect button in Menu window
        #  on failure enable it

    def send_to_server(self, code, value=None):
        pass
        # TODO in Network class send to server

    def chat_opponent(self, msg):
        self.gui.chat_opponent(msg, self.hnef.nick_opponent)

    def _start_game(self, turn, opn_name):
        # start new game in Hnefatafl class
        self.hnef.new_game(turn, opn_name)
        # switch frame in GUI, so user can play
        self.gui.new_game(self.nick, self.hnef.game_state, self.hnef.pf, self.hnef.allowed_squares)

    def leave_game(self):
        self.hnef.quit_game()

    def reset_game(self, turn, nick_opn, pf):
        # reset game in Hnefatafl class
        self.hnef.reset_game(turn, nick_opn, pf)
        # not actually new game -- it has state like in received message from server
        self.gui.new_game(self.nick, self.hnef.game_state, self.hnef.pf, self.hnef.allowed_squares)

    def handle_click(self, x_pos, y_pos):
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
                # move with stone
                self.move_self(self.hnef.x_from, self.hnef.y_from, x_pos, y_pos)

                # send move message to server
                move = self.compose_move_msg([self.hnef.x_from, self.hnef.y_from, x_pos, y_pos])
                self.send_to_server(protocol.CC_MOVE, value=move)

                # reset position, which is being moved from
                self.hnef.x_from = None
                self.hnef.y_from = None

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
        self.gui.pf_update(self.hnef.game_state, self.hnef.pf, self.hnef.allowed_squares)

    def move_self(self, x_from, y_from, x_to, y_to):
        # move chosen stone
        self.hnef.move(x_from, y_from, x_to, y_to)
        # check captures of local player -- capturing white if local is black
        self.hnef.check_captures(self.hnef.is_surrounded_white if self.hnef.black else self.hnef.is_surrounded_black)
        # after move, player cannot move anything
        self.hnef.allowed_squares.clear()

    def _move_opponent(self, x_from, y_from, x_to, y_to):
        # move opponent's piece
        self.hnef.move(x_from, y_from, x_to, y_to)
        # check captures of opponent player -- capturing black if local is black
        self.hnef.check_captures(self.hnef.is_surrounded_black if self.hnef.black else self.hnef.is_surrounded_white)
        # get pieces of player, who is on turn now
        self.hnef.find_movables_stones()

        # update playfield in gui
        self.gui.pf_update(self.hnef.pf, self.hnef.allowed_squares)

    def compose_move_msg(self, coordinates):
        move = ""

        for coor in coordinates:
            # if number has only one place, so append 0 at beginning according to protocol
            # else it is 10 with two places
            move += "0" + str(coor) if coor < 10 else str(coor)

        return move
