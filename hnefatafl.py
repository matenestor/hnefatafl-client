from hnefatafl_square import Square
from ups_state import Click


class Hnefatafl:
    # size of playfield
    _SIZE = 11

    def __init__(self):
        # who is on turn
        self.on_turn = None
        # opponent's nick
        self.nick_opponent = ""
        # color of player
        self.black = None
        # state of game, after user's click
        self.game_state = None
        # playfield
        self.pf = None
        # movable stones
        self.allowed_squares = []

        # position, which is being moved from
        self.x_from = None
        self.y_from = None
        # position, which was moved to (last move)
        self.x_to = None
        self.y_to = None

        # logger.info("Game started with opponent [{}]".format(self.opponent))

    def new_game(self, turn, nick_opn):
        self.on_turn = turn
        self.nick_opponent = nick_opn
        # player has black color, if one starts the game
        self.black = turn
        self.game_state = Click.THINKING if turn else Click.WAITING
        self._reset_playfield()
        self.find_movables_stones()

    def quit_game(self):
        self.on_turn = ""
        self.nick_opponent = ""
        self.black = None
        self.game_state = None
        self._reset_playfield()

    def reset_game(self,  turn, nick_opn, pf):
        self.on_turn = turn
        self.nick_opponent = nick_opn
        # player has black color, if one starts the game
        self.black = turn
        self.game_state = Click.THINKING if turn else Click.WAITING
        self._recover_pf(pf)

        # find movable stones, if local player is on turn
        if turn:
            self.find_movables_stones()

    def _reset_playfield(self):
        self.pf = [
            [Square.F_ESCAPE, Square.F_EMPTY, Square.F_EMPTY, Square.S_BLACK, Square.S_BLACK, Square.S_BLACK, Square.S_BLACK, Square.S_BLACK, Square.F_EMPTY, Square.F_EMPTY, Square.F_ESCAPE],
            [Square.F_EMPTY,  Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.S_BLACK, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY],
            [Square.F_EMPTY,  Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY],
            [Square.S_BLACK,  Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.S_WHITE, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.S_BLACK],
            [Square.S_BLACK,  Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.S_WHITE, Square.S_WHITE, Square.S_WHITE, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.S_BLACK],
            [Square.S_BLACK,  Square.S_BLACK, Square.F_EMPTY, Square.S_WHITE, Square.S_WHITE, Square.S_KING,  Square.S_WHITE, Square.S_WHITE, Square.F_EMPTY, Square.S_BLACK, Square.S_BLACK],
            [Square.S_BLACK,  Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.S_WHITE, Square.S_WHITE, Square.S_WHITE, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.S_BLACK],
            [Square.S_BLACK,  Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.S_WHITE, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.S_BLACK],
            [Square.F_EMPTY,  Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY],
            [Square.F_EMPTY,  Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.S_BLACK, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY, Square.F_EMPTY],
            [Square.F_ESCAPE, Square.F_EMPTY, Square.F_EMPTY, Square.S_BLACK, Square.S_BLACK, Square.S_BLACK, Square.S_BLACK, Square.S_BLACK, Square.F_EMPTY, Square.F_EMPTY, Square.F_ESCAPE]
        ]

    def _recover_pf(self, pf):
        # convert ints to Enum values
        for i, square_val in enumerate(pf):
            pf[i] = Square(square_val)

        # reshape 1D list to 2D list
        self.pf = [pf[i:i + Hnefatafl._SIZE] for i in range(0, len(pf), Hnefatafl._SIZE)]

    def move(self, x_from, y_from, x_to, y_to):
        # move piece to new location
        self.pf[y_to][x_to] = self.pf[y_from][x_from]

        # restore field type after move
        # F_THRONE if King was moved from middle field
        # F_EMPTY else some piece was moved from normal field
        self.pf[y_from][x_from] = Square.F_THRONE \
            if y_from == Hnefatafl._SIZE // 2 and x_from == Hnefatafl._SIZE // 2 \
            else Square.F_EMPTY

        # set last move
        self.x_to = x_to
        self.y_to = y_to

        # change game state after move
        if self.on_turn:
            self.game_state = Click.WAITING
        else:
            self.game_state = Click.THINKING

        # change turn after move
        self.on_turn = not self.on_turn

    def find_movables_stones(self):
        if self.on_turn:

            # clear previous movables
            self.allowed_squares.clear()

            # find movable stones of black player
            if self.black:
                for i, row in enumerate(self.pf):
                    for j, field in enumerate(row):
                        if field == Square.S_BLACK:
                            self.allowed_squares.append((i, j))

            # find movable stones of white player
            else:
                for i, row in enumerate(self.pf):
                    for j, field in enumerate(row):
                        if field == Square.S_WHITE or field == Square.S_KING:
                            self.allowed_squares.append((i, j))

    def find_placeable_fields(self, x_pos, y_pos):

        def find_horizontal(idx, shift):
            while 0 <= idx < Hnefatafl._SIZE \
                    and self.pf[y_pos][idx] in (Square.F_EMPTY, Square.F_ESCAPE, Square.F_THRONE):

                # note: if moving field is warrior and current field is Escape or Throne, do nothing
                # King is being moved -- append everything in (Empty, Escape, Throne)
                if self.pf[y_pos][x_pos] == Square.S_KING:
                    self.allowed_squares.append((y_pos, idx))
                # else warrior is being moved and current field in scope is Empty
                elif self.pf[y_pos][idx] == Square.F_EMPTY:
                    self.allowed_squares.append((y_pos, idx))

                idx += shift

        def find_vertical(idx, shift):
            while 0 <= idx < Hnefatafl._SIZE \
                    and self.pf[idx][x_pos] in (Square.F_EMPTY, Square.F_ESCAPE, Square.F_THRONE):

                # note: if moving field is warrior and current field is Escape or Throne, do nothing
                # King is being moved -- append everything in (Empty, Escape, Throne)
                if self.pf[y_pos][x_pos] == Square.S_KING:
                    self.allowed_squares.append((idx, x_pos))
                # else warrior is being moved and current field in scope is Empty
                elif self.pf[idx][x_pos] == Square.F_EMPTY:
                    self.allowed_squares.append((idx, x_pos))

                idx += shift

        # if self.on_turn and self.game_state == Click.CLICKED:
        # right
        find_horizontal(x_pos+1, 1)
        # left
        find_horizontal(x_pos-1, -1)
        # down
        find_vertical(y_pos+1, 1)
        # up
        find_vertical(y_pos-1, -1)

    def check_captures(self):

        def is_surrounded_black(field_adjacent, field_ally):
            return field_adjacent == Square.S_BLACK \
                    and (field_ally == Square.S_WHITE
                         or field_ally == Square.F_THRONE
                         or field_ally == Square.F_ESCAPE)

        def is_surrounded_white(field_adjacent, field_ally):
            return field_adjacent == Square.S_WHITE and field_ally == Square.S_BLACK

        # note: capture of the King is checked by server
        # check captures of black player
        if self.pf[self.y_to][self.x_to] == Square.S_BLACK:
            # capture right
            if self.x_to + 2 < Hnefatafl._SIZE:
                if is_surrounded_white(self.pf[self.y_to][self.x_to + 1], self.pf[self.y_to][self.x_to + 2]):
                    self.pf[self.y_to][self.x_to + 1] = Square.F_EMPTY

            # capture left
            if self.x_to - 2 >= 0:
                if is_surrounded_white(self.pf[self.y_to][self.x_to - 1], self.pf[self.y_to][self.x_to - 2]):
                    self.pf[self.y_to][self.x_to - 1] = Square.F_EMPTY

            # capture down
            if self.y_to + 2 < Hnefatafl._SIZE:
                if is_surrounded_white(self.pf[self.y_to + 1][self.x_to], self.pf[self.y_to + 2][self.x_to]):
                    self.pf[self.y_to + 1][self.x_to] = Square.F_EMPTY

            # capture up
            if self.y_to - 2 >= 0:
                if is_surrounded_white(self.pf[self.y_to - 1][self.x_to], self.pf[self.y_to - 2][self.x_to]):
                    self.pf[self.y_to - 1][self.x_to] = Square.F_EMPTY

        # check captures of white player
        elif self.pf[self.y_to][self.x_to] == Square.S_WHITE:
            # capture right
            if self.x_to + 2 < Hnefatafl._SIZE:
                if is_surrounded_black(self.pf[self.y_to][self.x_to + 1], self.pf[self.y_to][self.x_to + 2]):
                    self.pf[self.y_to][self.x_to + 1] = Square.F_EMPTY

            # capture left
            if self.x_to - 2 >= 0:
                if is_surrounded_black(self.pf[self.y_to][self.x_to - 1], self.pf[self.y_to][self.x_to - 2]):
                    self.pf[self.y_to][self.x_to - 1] = Square.F_EMPTY

            # capture down
            if self.y_to + 2 < Hnefatafl._SIZE:
                if is_surrounded_black(self.pf[self.y_to + 1][self.x_to], self.pf[self.y_to + 2][self.x_to]):
                    self.pf[self.y_to + 1][self.x_to] = Square.F_EMPTY

            # capture up
            if self.y_to - 2 >= 0:
                if is_surrounded_black(self.pf[self.y_to - 1][self.x_to], self.pf[self.y_to - 2][self.x_to]):
                    self.pf[self.y_to - 1][self.x_to] = Square.F_EMPTY

        # reset last move to position
        self.x_to = None
        self.y_to = None

    def is_field(self, x_pos, y_pos):
        return self.pf[y_pos][x_pos] in (Square.F_EMPTY, Square.F_THRONE, Square.F_ESCAPE)

    def is_same_stone(self, x_pos, y_pos):
        return self.x_from == x_pos and self.y_from == y_pos
