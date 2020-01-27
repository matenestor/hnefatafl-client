from enum import Enum


class ServerConnection(Enum):
    UP = 0
    PING = 1
    LOST = 2
    DOWN = 3
