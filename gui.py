import tkinter as tk

from menu_window import Menu
from game_window import Game
from popup_window import Popup


class Hnefatafl(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hnefatafl (made by matenestor)")

        # main container to keep other frames -- windows
        container = tk.Frame(self)
        container.pack()

        # available frames in application
        self.frames = {}

        # initialize frames
        for F in (Menu, Game):
            frame = F(container, self)
            self.frames[F] = frame

        # actual frame, used during switching to other frame
        self.actual_frame = self.frames[Menu]
        # show main menu
        self.show_frame("Menu")
        # start the application
        self.mainloop()

    def show_frame(self, cont):
        # forget actual frame
        self.actual_frame.pack_forget()

        if cont == "Menu":
            frame = self.frames[Menu]
        elif cont == "Game":
            frame = self.frames[Game]
        else:
            frame = None
        assert frame is not None, f"Unknown frame to raise! {cont}"

        # set new actual frame
        self.actual_frame = frame
        # set new frame
        frame.pack()

    def show_popup(self, msg):
        # TODO disable chat and leave button
        Popup(msg, self)


hnef = Hnefatafl()
