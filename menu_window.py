import re
import tkinter as tk


class Menu(tk.Frame):
    __IPADX = 120
    __PADX = 20
    __PADY = 10
    # 'localhost' is also available
    __REG_IP = r"^(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?!$)|$)){4}|localhost)$"
    # no '\w', in order to prevent diacritics
    __REG_NICK = r"[a-zA-Z0-9]{3,20}"
    __PORT_LOW = 1024
    __PORT_HIGH = 49151

    def __init__(self, parent, controller):
        # TO-DO longterm: i don't know why, but setting size of the frame has no effect
        # super().__init__(parent, width=480, height=400)

        super().__init__(parent)

        # access flags
        self.ok_nick = False
        self.ok_ip = False
        self.ok_port = False

        # nick
        self.grp_nick = tk.LabelFrame(self, text="Nick", padx=self.__PADX, pady=self.__PADY)
        self.ent_nick = tk.Entry(self.grp_nick)
        self.lbl_nick = tk.Label(self.grp_nick, text="Use only 3 to 20 letters.")

        # ip address
        self.grp_ip = tk.LabelFrame(self, text="IP address", padx=self.__PADX, pady=self.__PADY)
        self.ent_ip = tk.Entry(self.grp_ip)
        self.lbl_ip = tk.Label(self.grp_ip, text="Invalid IPv4 address.")

        # port
        self.grp_port = tk.LabelFrame(self, text="Port", padx=self.__PADX, pady=self.__PADY)
        self.ent_port = tk.Entry(self.grp_port)
        self.lbl_port = tk.Label(self.grp_port, text="Port range: 1024-49151.")

        # state label
        self.lbl_state = tk.Label(self)

        # buttons
        self.btn_connect = tk.Button(self, text="Connect", state=tk.DISABLED, command=self.hnef_connect)
        self.btn_play = tk.Button(self, text="Play", state=tk.DISABLED, command=lambda: controller.show_frame("Game"))
        self.btn_exit = tk.Button(self, text="Exit", command=self.set_state)

        self.setup_gui()

    def setup_gui(self):
        # nick
        self.grp_nick.pack(ipadx=self.__IPADX, pady=self.__PADY)
        self.ent_nick.pack(fill=tk.X, expand=True)
        self.ent_nick.bind("<FocusOut>", self.check_nick)

        # ip address
        self.grp_ip.pack(ipadx=self.__IPADX, pady=self.__PADY)
        self.ent_ip.pack(fill=tk.X, expand=True)
        self.ent_ip.bind("<FocusOut>", self.check_ip)

        # port
        self.grp_port.pack(ipadx=self.__IPADX, pady=self.__PADY)
        self.ent_port.pack(fill=tk.X, expand=True)
        self.ent_port.bind("<FocusOut>", self.check_port)

        # fill box
        tk.Frame(self).pack(fill=tk.Y, expand=True)

        # state label
        self.lbl_state.pack()

        # buttons
        self.btn_connect.pack(side="left", fill=tk.X, expand=True)
        self.btn_play.pack(side="left", fill=tk.X, expand=True)
        self.btn_exit.pack(side="left", fill=tk.X, expand=True)

    def hnef_connect(self):
        try:
            # check
            if re.fullmatch(self.__REG_NICK, self.ent_nick.get()) \
                    and re.fullmatch(self.__REG_IP, self.ent_ip.get()) \
                    and int(self.ent_port.get()):
                pass
                self.lbl_state["text"] = "connecting to server..."
                # TODO connect to server
            else:
                self.btns_disable()

        except ValueError:
            self.btns_disable()

    def set_state(self, msg):
        # self.lbl_state["text"] = msg
        self.lbl_state["text"] = "closing app"

    def check_nick(self, _):
        if re.fullmatch(self.__REG_NICK, self.ent_nick.get()):
            self.ok_nick = True
            self.lbl_nick.pack_forget()
            self.btns_enable()
        else:
            self.ok_nick = False
            self.lbl_nick.pack()
            self.btns_disable()

    def check_ip(self, _):
        if re.fullmatch(self.__REG_IP, self.ent_ip.get()):
            self.ok_ip = True
            self.lbl_ip.pack_forget()
            self.btns_enable()
        else:
            self.ok_ip = False
            self.lbl_ip.pack()
            self.btns_disable()

    def check_port(self, _):
        try:
            port = int(self.ent_port.get())
        except ValueError:
            port = -1

        if self.__PORT_LOW <= port <= self.__PORT_HIGH:
            self.ok_port = True
            self.lbl_port.pack_forget()
            self.btns_enable()
        else:
            self.ok_port = False
            self.lbl_port.pack()
            self.btns_disable()

    def btns_enable(self):
        if self.ok_nick and self.ok_ip and self.ok_port:
            self.btn_connect["state"] = tk.NORMAL
            self.btn_play["state"] = tk.NORMAL

    def btns_disable(self):
        self.btn_connect["state"] = tk.DISABLED
        self.btn_play["state"] = tk.DISABLED
