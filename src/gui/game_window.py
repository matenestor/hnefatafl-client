import re
import tkinter as tk
try:
    import os
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame
    pygame.mixer.init()
    MIXER = True
except (ImportError, ModuleNotFoundError, pygame.error):
    MIXER = False

import logger
from net import protocol
from game.hnefatafl_square import Square
from gui.click_state import Click


class Game(tk.Frame):
    # sprites location
    _RES = "../resources/"
    _R_PF = _RES + "pf.gif"
    _R_EMPTY = _RES + "empty.gif"
    _R_ESCAPE = _RES + "escape.gif"
    _R_THRONE = _RES + "throne.gif"
    _R_MOVE_EMPTY = _RES + "move_empty.gif"
    _R_MOVE_ESCAPE = _RES + "move_escape.gif"
    _R_MOVE_THRONE = _RES + "move_throne.gif"
    _R_BLACK = _RES + "black.gif"
    _R_WHITE = _RES + "white.gif"
    _R_KING = _RES + "king.gif"
    _R_BLACKEGG = _RES + "blackegg.gif"
    _R_WHITEEGG = _RES + "whiteegg.gif"
    _R_KINGEGG = _RES + "kingegg.gif"
    _R_BAZINGA = _RES + "bazinga.wav"

    # chat template for nicks
    CH_TMPL = "[{}]: "
    # chat name for system messages
    CH_BOT = CH_TMPL.format("BOT")

    # border of playfield desk
    _OFFSET = 21
    _FIELD_SIZE = 69
    _WIDTH = 801
    _HEIGHT = 801

    def __init__(self, parent, cont):
        super().__init__(parent)

        # controller of this class
        self._controller = cont

        # resources
        self._res_pf = tk.PhotoImage(file=Game._R_PF)
        self._res_empty = tk.PhotoImage(file=Game._R_EMPTY)
        self._res_escape = tk.PhotoImage(file=Game._R_ESCAPE)
        self._res_throne = tk.PhotoImage(file=Game._R_THRONE)
        self._res_move_empty = tk.PhotoImage(file=Game._R_MOVE_EMPTY)
        self._res_move_escape = tk.PhotoImage(file=Game._R_MOVE_ESCAPE)
        self._res_move_throne = tk.PhotoImage(file=Game._R_MOVE_THRONE)
        self._img_black = tk.PhotoImage(file=Game._R_BLACK)
        self._img_white = tk.PhotoImage(file=Game._R_WHITE)
        self._img_king = tk.PhotoImage(file=Game._R_KING)
        self._img_blackegg = tk.PhotoImage(file=Game._R_BLACKEGG)
        self._img_whiteegg = tk.PhotoImage(file=Game._R_WHITEEGG)
        self._img_kingegg = tk.PhotoImage(file=Game._R_KINGEGG)

        # prepare sound for easter egg
        if MIXER:
            self.baz = pygame.mixer.Sound(Game._R_BAZINGA)
        else:
            self.baz = None

        # state flags
        self._egg = False

        # chat name
        self.chat_nick_self = None

        # playfield
        self._canvas = tk.Canvas(self, width=Game._WIDTH, height=Game._HEIGHT)

        # chatting
        self._txt_chat = tk.Text(self, width=38, height=45, borderwidth=3, state=tk.DISABLED)
        self._ent_chat = tk.Entry(self)

        # buttons
        self._btn_chat = tk.Button(self, text="Send", command=self._chat)
        self._btn_leave = tk.Button(self, text="Leave", command=self.leave_game)

        self._setup_gui()

    def _setup_gui(self):
        # canvas
        self._canvas.grid(row=0, rowspan=3)

        # chatting
        self._txt_chat.grid(row=0, column=1, columnspan=4)
        self._ent_chat.grid(row=1, column=1, columnspan=4, sticky="ew")
        self._ent_chat.bind("<Return>", self._chat)
        self._btn_chat.grid(row=2, column=1, columnspan=3, sticky="ew")

        # leave game button
        self._btn_leave.grid(row=2, column=4, sticky="ew")

    def _chat(self, _=None):
        # get text from entry
        msg = self._ent_chat.get()
        # filter from unwanted characters
        msg = re.sub(r"[^a-zA-Z0-9\s.!?]+", " ", msg).strip()

        if msg == "iddqd":
            self._egg = not self._egg
            self._ent_chat.delete(0, tk.END)

            # play bazinga sound
            if self._egg and self.baz is not None:
                self.baz.play()

        elif msg != "":
            self.chat_insert(self.chat_nick_self + msg)
            self._ent_chat.delete(0, tk.END)
            self._controller.send_to_server(protocol.OP_CHAT, value=msg)

    def chat_insert(self, msg):
        # in order to insert into text widget, it has to be set to NORMAL at first
        self._txt_chat["state"] = tk.NORMAL
        self._txt_chat.insert(tk.END, msg + "\n")
        self._txt_chat["state"] = tk.DISABLED
        logger.trace("Chat message: {}".format(msg))

    def chat_clear(self):
        self._txt_chat.delete(1.0, tk.END)
        self.chat_insert(Game.CH_BOT + "Only letters, numbers and _.!? characters allowed during chatting.")

    def leave_game(self):
        self._controller.leave_game()
        logger.trace("Local player {} leaves the game.".format(self.chat_nick_self))

    def _click(self, event):
        # calculate position of field from clicked place on screen
        x_pos = (event.x - Game._OFFSET) // Game._FIELD_SIZE
        y_pos = (event.y - Game._OFFSET) // Game._FIELD_SIZE
        self._controller.handle_click(x_pos, y_pos)

    def draw_hnef(self, game_state, pf, allowed_squares):
        # set sprites from resources, according to easter-egg
        if self._egg:
            res_black = self._img_blackegg
            res_white = self._img_whiteegg
            res_king = self._img_kingegg
        else:
            res_black = self._img_black
            res_white = self._img_white
            res_king = self._img_king

        # draw board
        self._canvas.create_image(0, 0, anchor=tk.NW, image=self._res_pf)

        # draw squares
        for i, row in enumerate(pf):
            for j, field in enumerate(row):
                pos_y = Game._OFFSET + i * Game._FIELD_SIZE
                pos_x = Game._OFFSET + j * Game._FIELD_SIZE

                if field == Square.F_EMPTY:
                    # after player clicked on stone, draw move field sprites, else draw normal one
                    id_img = self._canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self._res_move_empty) \
                        if (i, j) in allowed_squares and game_state == Click.CLICKED \
                        else self._canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self._res_empty)

                elif field == Square.F_ESCAPE:
                    # draw also move escape field sprite for King
                    id_img = self._canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self._res_move_escape) \
                        if (i, j) in allowed_squares and game_state == Click.CLICKED \
                        else self._canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self._res_escape)

                elif field == Square.F_THRONE:
                    # and throne field sprite
                    id_img = self._canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self._res_move_throne) \
                        if (i, j) in allowed_squares and game_state == Click.CLICKED \
                        else self._canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self._res_throne)

                elif field == Square.S_BLACK:
                    id_img = self._canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=res_black)
                elif field == Square.S_WHITE:
                    id_img = self._canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=res_white)
                elif field == Square.S_KING:
                    id_img = self._canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=res_king)
                else:
                    # never should get here
                    id_img = -1

                # bind squares, which player can click on
                if (i, j) in allowed_squares:
                    self._canvas.tag_bind(id_img, "<Button-1>", self._click)

    def btns_enable(self):
        self._btn_chat["state"] = tk.NORMAL
        self._btn_leave["state"] = tk.NORMAL

    def btns_disable(self):
        self._btn_chat["state"] = tk.DISABLED
        self._btn_leave["state"] = tk.DISABLED
