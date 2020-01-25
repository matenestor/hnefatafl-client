from enum import Enum


class UpsConnection(Enum):
    UP = 0
    PING = 1
    LOST = 2
    DOWN = 3


class HnefClick(Enum):
    THINKING = 0
    CLICKED = 1
    WAITING = 2
