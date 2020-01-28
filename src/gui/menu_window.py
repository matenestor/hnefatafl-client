import re
import tkinter as tk

from net import protocol


class Menu(tk.Frame):
    _IPADX = 120
    _PADX = 20
    _PADY = 10
    # 'localhost' is also available
    _REG_IP = r"^(?:(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:\.(?!$)|$)){4}|localhost)$"
    # no '\w', in order to prevent diacritics and underscore
    _REG_NICK = r"[a-zA-Z0-9]{3,20}"
    _PORT_LOW = 1024
    _PORT_HIGH = 49151

    def __init__(self, parent, cont):
        # TO-DO longterm: i don't know why, but setting size of the frame has no effect
        # super().__init__(parent, width=480, height=400)

        super().__init__(parent)

        # controller of this class
        self._controller = cont

        # access flags
        self._ok_nick = False
        self._ok_ip = False
        self._ok_port = False

        # nick
        self._grp_nick = tk.LabelFrame(self, text="Nick", padx=Menu._PADX, pady=Menu._PADY)
        self._ent_nick = tk.Entry(self._grp_nick)
        self._lbl_nick = tk.Label(self._grp_nick, text="Use only 3 to 20 letters.")

        # ip address
        self._grp_ip = tk.LabelFrame(self, text="IP address", padx=Menu._PADX, pady=Menu._PADY)
        self._ent_ip = tk.Entry(self._grp_ip)
        self._lbl_ip = tk.Label(self._grp_ip, text="Invalid IPv4 address.")

        # port
        self._grp_port = tk.LabelFrame(self, text="Port", padx=Menu._PADX, pady=Menu._PADY)
        self._ent_port = tk.Entry(self._grp_port)
        self._lbl_port = tk.Label(self._grp_port, text="Port range: 1024-49151.")

        # state label
        self._lbl_state = tk.Label(self)

        # buttons
        self._btn_connect = tk.Button(self, text="Connect", state=tk.DISABLED, command=self.hnef_connect)
        self._btn_play = tk.Button(self, text="Play", state=tk.DISABLED, command=self.hnef_play)
        self._btn_exit = tk.Button(self, text="Exit", command=self._controller.destroy)

        self._setup_gui()

    def _setup_gui(self):
        # nick
        self._grp_nick.pack(ipadx=Menu._IPADX, pady=Menu._PADY)
        self._ent_nick.pack(fill=tk.X, expand=True)
        self._ent_nick.bind("<FocusOut>", self.check_nick)

        # ip address
        self._grp_ip.pack(ipadx=Menu._IPADX, pady=Menu._PADY)
        self._ent_ip.pack(fill=tk.X, expand=True)
        self._ent_ip.bind("<FocusOut>", self.check_ip)

        # port
        self._grp_port.pack(ipadx=Menu._IPADX, pady=Menu._PADY)
        self._ent_port.pack(fill=tk.X, expand=True)
        self._ent_port.bind("<FocusOut>", self.check_port)

        # state label
        self._lbl_state.pack()

        # buttons
        self._btn_connect.pack(side="left", fill=tk.X, expand=True)
        self._btn_play.pack(side="left", fill=tk.X, expand=True)
        self._btn_exit.pack(side="left", fill=tk.X, expand=True)

    def hnef_connect(self):
        try:
            nick = self._ent_nick.get()
            ip = self._ent_ip.get()
            port = self._ent_port.get()

            # check inputs once more
            if re.fullmatch(Menu._REG_NICK, nick) \
                    and re.fullmatch(Menu._REG_IP, ip) \
                    and int(port):
                # connect to server
                self.set_lbl_state("Connecting to server...")
                self._controller.hnef_connect(nick, ip, port)

            else:
                self.btn_connect_disable()

        except ValueError:
            self.btn_connect_disable()

    def hnef_play(self):
        self.set_lbl_state("Waiting for opponent...")
        self._controller.send_to_server(protocol.CC_READY)

    def set_lbl_state(self, msg):
        self._lbl_state["text"] = msg

    def check_nick(self, _):
        if re.fullmatch(Menu._REG_NICK, self._ent_nick.get()):
            self._ok_nick = True
            self._lbl_nick.pack_forget()
            self.btn_connect_enable()
        else:
            self._ok_nick = False
            self._lbl_nick.pack()
            self.btn_connect_disable()

    def check_ip(self, _):
        if re.fullmatch(Menu._REG_IP, self._ent_ip.get()):
            self._ok_ip = True
            self._lbl_ip.pack_forget()
            self.btn_connect_enable()
        else:
            self._ok_ip = False
            self._lbl_ip.pack()
            self.btn_connect_disable()

    def check_port(self, _):
        try:
            port = int(self._ent_port.get())
        except ValueError:
            port = -1

        if Menu._PORT_LOW <= port <= Menu._PORT_HIGH:
            self._ok_port = True
            self._lbl_port.pack_forget()
            self.btn_connect_enable()
        else:
            self._ok_port = False
            self._lbl_port.pack()
            self.btn_connect_disable()

    def btn_connect_enable(self):
        if self._ok_nick and self._ok_ip and self._ok_port:
            self._btn_connect["state"] = tk.NORMAL

    def btn_play_enable(self):
        self._btn_play["state"] = tk.NORMAL

    def btn_connect_disable(self):
        self._btn_connect["state"] = tk.DISABLED

    def btn_play_disable(self):
        self._btn_play["state"] = tk.DISABLED
