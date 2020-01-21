import signal
import sys

import Client
from Client import Client


def signal_handler(sig, frame):
    global is_client_alive
    is_client_alive = False


def init(ip, port):
    # register ctrl+c event
    signal.signal(signal.SIGINT, signal_handler)

    # create client
    client = Client(ip, port)
    client.connect()




