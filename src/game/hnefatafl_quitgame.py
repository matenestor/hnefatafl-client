from enum import Enum


class QuitGame(Enum):
    GAME_WIN = 0
    GAME_LOSS = 1
    OPN_LEFT = 2
    OPN_GONE = 3
    SERVER_KICK = 4
    SERVER_SHUTDOWN = 5
    SESSION_DISCONNECTED = 6
