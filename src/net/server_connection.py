from enum import Enum


class ServerConnection(Enum):
    UP = 0
    PING = 1
    LOST = 2
    DOWN = 3


class ConnectResult(Enum):
    CONN_SUCCESS = 0
    CONN_FAILURE = 1
