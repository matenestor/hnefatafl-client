import logger


F_EMPTY = 0
F_THRONE = 1
F_ESCAPE = 2
S_BLACK = 3
S_WHITE = 4
S_KING = 5


class Hnefatafl:
    def __init__(self, opn, trn):
        # opponents name
        self.opponent = opn
        # who is on turn
        self.onTurn = trn
        # game state telling, if game is still in progress
        self.gameState = True
        # playfield
        self.pf = [
            [F_ESCAPE, F_EMPTY, F_EMPTY, S_BLACK, S_BLACK, S_BLACK, S_BLACK, S_BLACK, F_EMPTY, F_EMPTY, F_ESCAPE],
            [F_EMPTY,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY],
            [F_EMPTY,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY],
            [S_BLACK,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_WHITE, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK],
            [S_BLACK,  F_EMPTY, F_EMPTY, F_EMPTY, S_WHITE, S_WHITE, S_WHITE, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK],
            [S_BLACK,  S_BLACK, F_EMPTY, S_WHITE, S_WHITE, S_KING,  S_WHITE, S_WHITE, F_EMPTY, S_BLACK, S_BLACK],
            [S_BLACK,  F_EMPTY, F_EMPTY, F_EMPTY, S_WHITE, S_WHITE, S_WHITE, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK],
            [S_BLACK,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_WHITE, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK],
            [F_EMPTY,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY],
            [F_EMPTY,  F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, S_BLACK, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY, F_EMPTY],
            [F_ESCAPE, F_EMPTY, F_EMPTY, S_BLACK, S_BLACK, S_BLACK, S_BLACK, S_BLACK, F_EMPTY, F_EMPTY, F_ESCAPE]
        ]

        logger.info("Game started with opponent [{}]".format(self.opponent))
