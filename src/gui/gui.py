import tkinter as tk

import logger
from game.hnefatafl_quitgame import QuitGame
from gui.game_window import Game
from gui.menu_window import Menu
from gui.popup_window import Popup


class Gui(tk.Tk):
    def __init__(self, cont):
        super().__init__()
        self.title("Hnefatafl (made by matenestor)")

        # application is controller of gui
        self._controller = cont

        # main container to keep other frames -- windows
        self._container = tk.Frame(self)
        self._container.pack()

        # available frames in application
        self._frames = {}

        # initialize frames
        for F in (Menu, Game):
            frame = F(self._container, self)
            self._frames[F.__name__] = frame

        # actual frame, used during switching to other frame
        self._actual_frame = self._frames["Menu"]
        # show main menu
        self.show_frame("Menu")

    def show_frame(self, cont):
        # forget actual frame
        self._actual_frame.pack_forget()

        # get frame to change to
        frame = self._frames[cont]
        assert frame is not None, f"Unknown frame to raise! '{cont}'"

        # set new actual frame
        self._actual_frame = frame
        # set new frame
        frame.pack()

    def _show_popup(self, msg):
        self._frames["Game"].btns_disable()
        Popup(msg, self)

    def hnef_connect(self, nick, ip, port):
        self._controller.hnef_connect(nick, ip, port)

    def make_connected(self):
        self._frames["Menu"].set_lbl_state("Connected.")
        self._frames["Menu"].btn_connect_disable()
        self._frames["Menu"].btn_play_enable()

    def make_disconnected(self):
        self._frames["Menu"].set_lbl_state("Not connected.")
        self._frames["Menu"].btn_connect_enable()
        self._frames["Menu"].btn_play_disable()

    def set_state(self, msg):
        self._frames["Menu"].set_lbl_state(msg)

    def send_to_server(self, code, value=None):
        self._controller.send_to_server(code, value)

    def chat_msg_server(self, msg, bot, chat_nick_opponent):
        # find out, who is sending the message
        who = Game.CH_BOT if bot else Game.CH_TMPL.format(chat_nick_opponent)
        self._frames["Game"].chat_insert(who + msg)

    def new_game(self, nick, game_state, pf, allowed_squares):
        self._frames["Game"].chat_nick_self = Game.CH_TMPL.format(nick)
        self._frames["Game"].chat_clear()
        self._frames["Game"].draw_hnef(game_state, pf, allowed_squares)
        self._frames["Game"].btns_enable()
        self.show_frame("Game")

    def leave_game(self):
        self._controller.leave_game()
        self.pf_update(0, [], [])
        self.show_frame("Menu")

    def quit_game(self, result):
        if result == QuitGame.GAME_WIN:
            msg = "You won the game!"
        elif result == QuitGame.GAME_LOSS:
            msg = "You lost the game!"
        elif result == QuitGame.OPN_LEFT:
            msg = "Opponent left the game!"
        elif result == QuitGame.OPN_GONE:
            msg = "Opponent is gone and can't reconnect!"
        elif result == QuitGame.SERVER_KICK:
            msg = "You have been kicked from server."
        elif result == QuitGame.SERVER_SHUTDOWN:
            msg = "Server shutdown."
        elif result == QuitGame.SESSION_DISCONNECTED:
            msg = "Connection lost definitely."
        else:
            # never should get here
            msg = "Unknown application state.."

        logger.trace("Quitting game: {}".format(msg))

        self._frames["Menu"].set_lbl_state(msg)
        self._show_popup(msg)

    def handle_click(self, x_pos, y_pos):
        self._controller.handle_click(x_pos, y_pos)

    def pf_update(self, game_state, pf, allowed_squares):
        self._frames["Game"].draw_hnef(game_state, pf, allowed_squares)
