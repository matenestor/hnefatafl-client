import tkinter as tk


class Popup(tk.Toplevel):
    def __init__(self, msg, controller):
        super().__init__()

        self.title("Info message")
        self.geometry("320x160")
        self.resizable(False, False)

        # message in popup window
        lbl_message = tk.Label(self, text=msg)
        lbl_message.pack(pady=10, padx=10)

        # button to go back to main menu
        btn_main_menu = tk.Button(self, text="Back to Main menu", command=lambda: self.main_menu(controller))
        btn_main_menu.pack(side="bottom")

    def main_menu(self, controller):
        controller.show_frame("Menu")
        self.destroy()
