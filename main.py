# import pyglet

F_EMPTY = 0
F_THRONE = 999
F_ESCAPE = 999
S_BLACK = 1
S_WHITE = 2
S_KING = 3
S_WHITE_STONES = (S_WHITE, S_KING)

player_black = True

pf = [
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


def is_valid_move(p_black, start_x, start_y, end_x, end_y):
    if p_black and pf[start_y][start_x] == S_BLACK:
        return True
    elif not p_black and pf[start_y][start_x] in S_WHITE_STONES:
        return True
    else:
        return False


def move_stone(start_x, start_y, end_x, end_y):
    pf[end_y][end_x] = pf[start_y][start_x]
    pf[start_y][start_x] = F_EMPTY


def check_capture(pos_x, pos_y):
    pass


def check_escape(pos_x, pos_y):
    pass


def check_take(pos_x, pos_y):
    pass


def play():
    while True:

        if player_black:
            print("Black, make your move: ", end="")
            move = input()
            print(type(move))

        else:
            print("White, make your move: ", end="")
            move = input()
            print(type(move))

        player_black = not player_black

        print("Black" if player_black else "White", "player's turn.")


def main():
    play()


if __name__ == '__main__':
    main()
