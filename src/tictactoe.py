"""
Simple proof of concept with Tic Tac Toe
"""

import copy
from enum import Enum
from typing import Iterable, Tuple, Self

from .abstracts import Evaluator, GameState, Terminal


class Player(Enum):
    CIRCLE = 0
    CROSS = 1

    def maxxer(self) -> bool:
        return self == Player.CIRCLE

    def opposite(self) -> Self:
        if self == Player.CIRCLE:
            return Player.CROSS
        else:
            return Player.CIRCLE


PRINT_TBL = {Player.CIRCLE: "O", Player.CROSS: "X", None: " "}

# TODO would be cool to have a (non-essential) but helper generic grid class,
# since so many different games are played on grids

Move = Tuple[int, int]


class TicState(GameState):

    def __init__(self, to_play: Player, grid: list[list[Player | None]]):

        assert len(grid) == 3, "must be a 3x3 grid"
        assert all(len(row) == 3 for row in grid), "must be a 3x3 grid"

        self.to_play = to_play
        self.grid = copy.deepcopy(grid)

    def make_move(self, move: Move) -> None:
        self.set_square(move[0], move[1], self.to_play)
        self.to_play = self.to_play.opposite()

    def get_next_states(self) -> Iterable[Tuple[Move, Self]]:

        for row in range(3):
            for col in range(3):
                if self.grid[row][col] is None:

                    nxt = TicState(self.to_play, self.grid)
                    nxt.make_move((row, col))

                    yield ((row, col), nxt)

    def maxxer_turn(self) -> bool:
        return self.to_play.maxxer()

    def minner_turn(self) -> bool:
        return not self.to_play.maxxer()

    def get_square(self, row: int, col: int) -> Player | None:
        return self.grid[row][col]

    def set_square(self, row: int, col: int, val: Player | None) -> None:
        self.grid[row][col] = val

    def __str__(self) -> str:

        res = ""

        for i, row in enumerate(self.grid):
            res += "|".join(PRINT_TBL[v] for v in row) + "\n"
            if i < 2:
                res += "-----\n"

        return res


class TicEvaluator(Evaluator[TicState]):
    def evaluate(state: TicState) -> float:

        for player in (Player.CIRCLE, Player.CROSS):

            if (
                # 2 diagonals
                all(state.get_square(i, i) == player for i in range(3)) or
                all(state.get_square(i, 2 - i) == player for i in range(3)) or
                # horizontal or verticals
                any(
                    all(state.get_square(i, j) == player for i in range(3))
                    for j in range(3)
                ) or
                any(
                    all(state.get_square(j, i) == player for i in range(3))
                    for j in range(3)
                )
            ):
                if player.maxxer():
                    return Terminal.MAXXER_WIN
                else:
                    return Terminal.MINNER_WIN

        if all(state.get_square(i, j) is not None
               for i in range(3) for j in range(3)):
            return Terminal.DRAW

        return 0
