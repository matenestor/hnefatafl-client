import tkinter as tk

from game_window import Game
from menu_window import Menu
from popup_window import Popup


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

    def show_popup(self, msg):
        self._frames["Game"].btns_disable()
        Popup(msg, self)

    def hnef_connect(self, nick, ip, port):
        self._controller.hnef_connect(nick, ip, port)

    def send_to_server(self, code, value=None):
        self._controller.send_to_server(code, value)

    def chat_opponent(self, msg, chat_nick_opponent):
        self._frames["Game"].chat_insert(chat_nick_opponent + msg)

    def new_game(self, nick, game_state, pf, allowed_squares):
        self._frames["Game"].chat_nick_self = Game.CH_TMPL.format(nick)
        self._frames["Game"].draw_hnef(game_state, pf, allowed_squares)
        self._frames["Game"].btns_enable()
        self.show_frame("Game")

    def handle_click(self, x_pos, y_pos):
        self._controller.handle_click(x_pos, y_pos)

    def pf_update(self, game_state, pf, allowed_squares):
        self._frames["Game"].draw_hnef(game_state, pf, allowed_squares)

    def leave_game(self):
        self._controller.leave_game()
        self.pf_update(0, [], [])
        self.show_frame("Menu")
