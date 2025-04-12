import time
import threading

from typing import TypeVar, Callable, Optional

from .abstracts.evaluator import Evaluator
from .abstracts.gamestate import GameState, TMove


T = TypeVar("T", bound=GameState)  # for bounding gamestate and evaluator together
SharedMoveRef = list[Optional[TMove]]
MoveFinder = Callable[[threading.Event, SharedMoveRef], None]
Searcher = Callable[[int, threading.Event], TMove]


def minimax(state: T, evaluator: Evaluator[T], timeout: float) -> TMove:

    def fac(max_depth: int) -> MoveFinder:
        return dfs_factory(state, evaluator, max_depth)

    return iterative_deepening_search(fac, timeout)


def iterative_deepening_search(dfs_factory: Searcher,
                               timeout: float) -> TMove:

    start = time.time()
    depth = 1
    move_to_play = None

    while (elapsed := time.time() - start) < timeout:
        searcher = dfs_factory(depth)
        move = search_with_timeout(searcher, timeout - elapsed)

        if move is not None:
            move_to_play = move

        depth += 1

    return move_to_play


def search_with_timeout(searcher: Searcher,
                        timeout: float) -> Optional[TMove]:

    kill_flag = threading.Event()

    out = [None]

    thread = threading.Thread(target=searcher, args=(kill_flag, out))
    timer = threading.Timer(timeout, lambda: kill_flag.set())

    thread.start()
    timer.start()

    thread.join()
    timer.cancel()

    return out[0]


def prune(state: GameState, score: float, alpha: float, beta: float) -> bool:

    return (state.maxxer_turn() and score >= beta) or \
        (state.minner_turn() and score <= alpha)


def dfs_factory(state: T, evaluator: Evaluator[T],
                max_depth: int) -> MoveFinder:

    best_move: Optional[TMove] = None

    def dfs(cur: T,
            kill_flag: threading.Event,
            depth: int = 0,
            alpha: float = float("-inf"),
            beta: float = float("inf")) -> Optional[float]:

        if kill_flag.is_set():
            return None

        cur_score = evaluator(cur)

        if (
            depth == max_depth or
            cur_score in (float("inf"), float("-inf"))  # someone won
        ):
            return cur_score

        best = None

        for move, nxt in cur.get_next_states():
            score = dfs(nxt, kill_flag, depth + 1, alpha, beta)

            if score is None:
                return None

            if best is None or (
                (nxt.maxxer_turn() and score > best) or
                (nxt.minner_turn() and score < best)
            ):

                if prune(cur, score, alpha, beta):
                    return score

                best = score

                if cur.maxxer_turn():
                    alpha = max(alpha, score)
                else:
                    beta = min(beta, score)

                if depth == 0:
                    nonlocal best_move
                    best_move = move

    def wrapper(kill_flag: threading.Event, output_move: SharedMoveRef) -> None:
        dfs(state, kill_flag)
        output_move[0] = None if kill_flag.is_set() else best_move

    return wrapper
