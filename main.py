import sys

from src.tictactoe import TicEvaluator, TicState, Player
from src.minimax import minimax


PRINT_TBL = {Player.CIRCLE: "O", Player.CROSS: "X", None: " "}
PLAYING_AS = Player.CIRCLE

def main(args: list[str]) -> None:

    timeout = 2

    if len(args) >= 1:
        try:
            timeout = float(args[0])
        except ValueError:
            print("invalid timeout")

    board = [[None] * 3 for i in range(3)]

    state = TicState(PLAYING_AS, board)

    while TicEvaluator.evaluate(state) not in (float("inf"), float("-inf")):

        if state.to_play == PLAYING_AS:

            # print board
            for i, row in enumerate(state.grid):
                print("|".join(PRINT_TBL[v] for v in row))
                if i < 2:
                    print("-----")

            print("Play a move: x y, where bottom left is (1, 1)")

            valid = False
            first = True

            while not valid:

                if first:
                    first = False
                else:
                    print("enter a valid value plz")

                move = input().split()

                if len(move) != 2:
                    continue

                try:
                    x, y = int(move[0]), int(move[1])
                except ValueError:
                    continue

                if not 1 <= x <= 3 or not 1 <= y <= 3:
                    continue

                row = 3 - y
                col = x - 1

                if state.grid[row][col] is not None:
                    continue

                valid = True

            state.make_move((row, col))

        else:
            print("machine think !")
            move = minimax(state, TicEvaluator, timeout)
            if move is None:
                print("u broke da machine >:(")
                return
            state.make_move(move)

    if TicEvaluator.evaluate(state) == float("inf"):
        if PLAYING_AS.maxxer():
            print("You won!")
        else:
            print("You lost >:(")
    else:
        if PLAYING_AS.maxxer():
            print("u lost haha")
        else:
            print("You WON!")


if __name__ == "__main__":
    main(sys.argv[1:])
