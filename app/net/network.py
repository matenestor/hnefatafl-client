import select
import sys

from app import logger
from app.net import protocol
from app.net.ups_session import Session
from app.net.server_connection import ServerConnection


class Network:
    # seconds before timeout on select
    _TIMEOUT = 5

    def __init__(self, ip, port):
        # server default ip address
        self.addrIp = ip
        # server default port
        self.port = port

        # received bytes in total
        self.bytes_recv = 0
        # sent bytes in total
        self.bytes_send = 0
        # count of reconnection
        self.cnt_recn = 0

        # buffer to receive to
        self.buffer = ""
        # size of buffer for receiving
        self.buffSize = 1024

        # clients session to server
        self.sess = None

        logger.info("Client initialized.")

    def __del__(self):
        logger.info("Bytes received in total: {}".format(self.bytes_recv))
        logger.info("Bytes sent in total: {}".format(self.bytes_send))
        logger.info("Count of reconnection in total: {}".format(self.cnt_recn))

    def create_session(self):
        self.sess = Session(self.addrIp, self.port)

    def run(self):
        assert self.sess is not None, "Session is None"

        # get socket from current session
        sock = self.sess.get_sock()

        # the only socket to read from is server
        sources = [sock]

        while not self.sess.is_expired():
            # block, until message from server is received
            fds_read, _, fds_except = select.select(sources, [], sources, Network._TIMEOUT)

            # socket went bad, some problem with server connection
            if sock in fds_except:
                self.has_connection = False
                self.srv_status = ServerConnection.DOWN

        # server send a message
            elif sock in fds_read:
                self.receive_msg(self.sess)

            # timeout
            else:
                if self.srv_status == ServerConnection.PING:
                    self.srv_status = ServerConnection.LOST;
                    self.has_connection = False
                else:
                    self.srv_status = ServerConnection.PING
                    self.send_msg(self.sess, protocol.OP_PING)

    def receive_msg(self, sess):
        # TODO patch
        print(sys.stderr, 'received "%s" from %s' % (self.buffer, self.sock.getpeername()))

        try:
            buffer = sess.get_sock.recv(self.buffSize).decode("utf8")
        except:
            logger.debug("fucked on tryexc")

        if len(buffer) > 0:
            logger.debug(buffer)
        else:
            logger.debug("fucked")

    def send_msg(self, sess, _msg):
        # TODO surround with catch
        msg = protocol.OP_SOH + _msg + protocol.OP_EOT
        self.sock.sendall(msg.encode("utf8"))



    # ip, port = parse_args()
    # client = init(ip, port)
    # run(client)



    # def run(self, client):
    #     # create initial session
    #     client.create_session()
    #
    #     # run until user does not close this program (blocked by select in run() method)
    #     # looped if connection to server was lost
    #     while is_running:
    #         client.run()
    #
    #         if client.srv_status == UpsConnection.LOST:
    #             client.reconnect()
    #         elif client.srv_status == UpsConnection.DOWN:
    #             client.reset_session()



    # def myreceive(self):
    #     chunks = []
    #     bytes_recd = 0
    #     while bytes_recd < self.buffSize:
    #         chunk = self.sock.recv(min(self.buffSize - bytes_recd, 2048))
    #         if chunk == b'':
    #             raise RuntimeError("socket connection broken")
    #         chunks.append(chunk)
    #         bytes_recd = bytes_recd + len(chunk)
    #     return b''.join(chunks)


        # # cut move string according to protocol
        # x_from = move[:2]
        # y_from = move[2:4]
        # x_to = move[4:6]
        # y_to = move[6:]



#
# #!/usr/bin/env python3
# """Script for Tkinter GUI chat client."""
# from socket import AF_INET, socket, SOCK_STREAM
# from threading import Thread
# import tkinter
#
#
# def receive():
#     """Handles receiving of messages."""
#     while True:
#         try:
#             msg = client_socket.recv(BUFSIZ).decode("utf8")
#             msg_list.insert(tkinter.END, msg)
#         except OSError:  # Possibly client has left the chat.
#             break
#
#
# def send(event=None):  # event is passed by binders.
#     """Handles sending of messages."""
#     msg = my_msg.get()
#     my_msg.set("")  # Clears input field.
#     client_socket.send(bytes(msg, "utf8"))
#     if msg == "{quit}":
#         client_socket.close()
#         top.quit()
#
#
# def on_closing(event=None):
#     """This function is to be called when the window is closed."""
#     my_msg.set("{quit}")
#     send()
#
# top = tkinter.Tk()
# top.title("Chatter")
#
# messages_frame = tkinter.Frame(top)
# my_msg = tkinter.StringVar()  # For the messages to be sent.
# my_msg.set("Type your messages here.")
# scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# # Following will contain the messages.
# msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
# scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
# msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
# msg_list.pack()
# messages_frame.pack()
#
# entry_field = tkinter.Entry(top, textvariable=my_msg)
# entry_field.bind("<Return>", send)
# entry_field.pack()
# send_button = tkinter.Button(top, text="Send", command=send)
# send_button.pack()
#
# top.protocol("WM_DELETE_WINDOW", on_closing)
#
# #----Now comes the sockets part----
# HOST = input('Enter host: ')
# PORT = input('Enter port: ')
# if not PORT:
#     PORT = 33000
# else:
#     PORT = int(PORT)
#
# BUFSIZ = 1024
# ADDR = (HOST, PORT)
#
# client_socket = socket(AF_INET, SOCK_STREAM)
# client_socket.connect(ADDR)
#
# receive_thread = Thread(target=receive)
# receive_thread.start()
# tkinter.mainloop()  # Starts GUI execution.
