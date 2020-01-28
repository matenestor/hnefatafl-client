import tkinter as tk


class Popup(tk.Toplevel):
    def __init__(self, msg, cont):
        super().__init__()

        # controller of this class
        self._controller = cont

        # setup window
        self.title("Info message")
        self.geometry("320x160")
        self.resizable(False, False)
        self.overrideredirect(True)

        # message in popup window
        self._lbl_message = tk.Label(self, text=msg)
        self._lbl_message.pack(pady=10, padx=10)

        # button to go back to main menu
        self._btn_main_menu = tk.Button(self, text="Back to Main menu", command=self._main_menu)
        self._btn_main_menu.pack(side="bottom")

    def _main_menu(self):
        self._controller.show_frame("Menu")
        self.destroy()
