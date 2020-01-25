import tkinter as tk
from ups_state import HnefClick

F_EMPTY = 0
F_THRONE = 1
F_ESCAPE = 2
S_BLACK = 3
S_WHITE = 4
S_KING = 5

pf = [
    [F_ESCAPE, F_EMPTY, F_EMPTY, S_BLACK, S_BLACK, S_BLACK, S_BLACK, S_BLACK, F_EMPTY, F_EMPTY, F_ESCAPE],
    [F_EMPTY,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY],
    [F_EMPTY,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY],
    [S_BLACK,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_WHITE, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK],
    [S_BLACK,  F_EMPTY, F_EMPTY, F_EMPTY, S_WHITE, S_WHITE, S_WHITE, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK],
    [S_BLACK,  S_BLACK, F_EMPTY, S_WHITE, S_WHITE, S_KING,  S_WHITE, S_WHITE, F_EMPTY, S_BLACK, S_BLACK],
    [S_BLACK,  F_EMPTY, F_EMPTY, F_EMPTY, S_WHITE, S_WHITE, S_WHITE, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK],
    [S_BLACK,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_WHITE, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK],
    [F_EMPTY,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY],
    [F_EMPTY,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY],
    [F_ESCAPE, F_EMPTY, F_EMPTY, S_BLACK, S_BLACK, S_BLACK, S_BLACK, S_BLACK, F_EMPTY, F_EMPTY, F_ESCAPE]
]


class Game(tk.Frame):
    # sprites location
    __RES = "sprites/"
    __R_PF = __RES + "pf.gif"
    __R_EMPTY = __RES + "empty.gif"
    __R_ESCAPE = __RES + "escape.gif"
    __R_THRONE = __RES + "throne.gif"
    __R_MOVE = __RES + "move.gif"
    __R_BLACK = __RES + "black.gif"
    __R_WHITE = __RES + "white.gif"
    __R_KING = __RES + "king.gif"
    __R_BLACKEGG = __RES + "blackegg.gif"
    __R_WHITEEGG = __RES + "whiteegg.gif"
    __R_KINGEGG = __RES + "kingegg.gif"

    # border of playfield desk
    __OFFSET = 21
    __FIELD_SIZE = 69
    __WIDTH = 801
    __HEIGHT = 801

    def __init__(self, parent, controller):
        super().__init__(parent)

        # resources
        self.res_pf = tk.PhotoImage(file=self.__R_PF)
        self.res_empty = tk.PhotoImage(file=self.__R_EMPTY)
        self.res_escape = tk.PhotoImage(file=self.__R_ESCAPE)
        self.res_throne = tk.PhotoImage(file=self.__R_THRONE)
        self.res_move = tk.PhotoImage(file=self.__R_MOVE)
        self.img_black = tk.PhotoImage(file=self.__R_BLACK)
        self.img_white = tk.PhotoImage(file=self.__R_WHITE)
        self.img_king = tk.PhotoImage(file=self.__R_KING)
        self.img_blackegg = tk.PhotoImage(file=self.__R_BLACKEGG)
        self.img_whiteegg = tk.PhotoImage(file=self.__R_WHITEEGG)
        self.img_kingegg = tk.PhotoImage(file=self.__R_KINGEGG)

        # state flags
        self.state = HnefClick.THINKING
        self.on_turn = None
        self.egg = False

        # playfield
        self.canvas = tk.Canvas(self, width=self.__WIDTH, height=self.__HEIGHT)

        # chatting
        self.txt_chat = tk.Text(self, width=40, height=45, borderwidth=3, state=tk.DISABLED)
        self.ent_chat = tk.Entry(self)

        # buttons
        self.btn_chat = tk.Button(self, text="Send", command=self.chat)
        self.btn_leave = tk.Button(self, text="Leave", command=lambda: self.leave_game(controller))

        tk.Button(self, text="popup", command=lambda: controller.show_popup("leave game")).grid()

        self.setup_gui()

    def setup_gui(self):
        # canvas
        # self.canvas.grid(row=0, rowspan=3)
        self.canvas.bind("<Button-1>", self.move)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.res_pf)

        # chatting
        self.txt_chat.grid(row=0, column=1, columnspan=4)
        self.ent_chat.grid(row=1, column=1, columnspan=4, sticky="ew")
        self.ent_chat.bind("<Return>", self.chat)
        self.btn_chat.grid(row=2, column=1, columnspan=3, sticky="ew")

        # leave game button
        self.btn_leave.grid(row=2, column=4, sticky="ew")

        # draw rest of the board
        self.draw_hnef()

    def chat(self, _=None):
        msg = self.ent_chat.get()

        if msg == "iddqd":
            # TODO easteregg
            self.ent_chat.delete(0, tk.END)
            pass

        elif msg != "":
            # in order to insert into text widget, it has to be set to NORMAL at first
            self.txt_chat["state"] = tk.NORMAL
            self.txt_chat.insert(tk.END, msg + "\n")
            self.txt_chat["state"] = tk.DISABLED
            self.ent_chat.delete(0, tk.END)
            # TODO send chat msg

    def leave_game(self, cont):
        # TODO send msg about leaving
        cont.show_frame("Menu")

    def move(self, _):
        pass

    def draw_hnef(self):
        if self.egg:
            res_black = self.img_blackegg
            res_white = self.img_whiteegg
            res_king = self.img_kingegg
        else:
            res_black = self.img_black
            res_white = self.img_white
            res_king = self.img_king

        for i, row in enumerate(pf):
            for j, field in enumerate(row):
                pos_y = self.__OFFSET + i*self.__FIELD_SIZE
                pos_x = self.__OFFSET + j*self.__FIELD_SIZE

                if field == F_EMPTY:
                    self.canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self.res_empty)
                elif field == F_ESCAPE:
                    self.canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self.res_escape)
                elif field == F_THRONE:
                    self.canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=self.res_throne)
                elif field == S_BLACK:
                    self.canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=res_black)
                elif field == S_WHITE:
                    self.canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=res_white)
                elif field == S_KING:
                    self.canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=res_king)

    def btns_disable(self):
        self.btn_chat["state"] = tk.DISABLED
        self.btn_leave["state"] = tk.DISABLED
