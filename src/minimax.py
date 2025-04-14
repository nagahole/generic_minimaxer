import time
import threading

from typing import TypeVar, Callable, Tuple, Optional

from .abstracts import Evaluator, Terminal
from .abstracts.gamestate import GameState, TMove


T = TypeVar("T", bound=GameState)  # for bounding gamestate and evaluator together

SharedMoveRef = list[Optional[TMove]]
SharedBoolRef = list[bool]

MoveFinder = Callable[[threading.Event, SharedMoveRef, SharedBoolRef], None]
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
        move, complete = search_with_timeout(searcher, timeout - elapsed)

        if move is not None:
            move_to_play = move

        if complete:
            break

        depth += 1

    return move_to_play


def search_with_timeout(searcher: Searcher,
                        timeout: float) -> Tuple[Optional[TMove], bool]:

    kill_flag = threading.Event()

    out_move = [None]
    out_complete_search = [False]  # entire game space searched

    thread = threading.Thread(
        target=searcher,
        args=(kill_flag, out_move, out_complete_search)
    )
    timer = threading.Timer(timeout, lambda: kill_flag.set())

    thread.start()
    timer.start()

    thread.join()
    timer.cancel()

    return out_move[0], out_complete_search[0]


# alpha beta set to None instead of infinity for init because of clash
# when score is also infinite
def prune(state: GameState,
          score: float,
          alpha: Optional[float],
          beta: Optional[float]) -> bool:

    return (state.maxxer_turn() and beta is not None and score >= beta) or \
        (state.minner_turn() and alpha is not None and score <= alpha)


def dfs_factory(state: T, evaluator: Evaluator[T],
                max_depth: int) -> MoveFinder:

    best_move = None
    all_terminals_reached = True  # set to false at first max_depth reached

    def dfs(cur: T,
            kill_flag: threading.Event,
            depth: int = 0,
            alpha: Optional[float] = None,
            beta: Optional[float] = None) -> Optional[float]:

        if kill_flag.is_set():
            return None

        cur_score = evaluator.evaluate(cur)

        if isinstance(cur_score, Terminal):
            return cur_score.value

        if depth == max_depth:
            nonlocal all_terminals_reached
            all_terminals_reached = False
            return cur_score

        best = None

        for move, nxt in cur.get_next_states():

            score = dfs(nxt, kill_flag, depth + 1, alpha, beta)

            if score is None:  # kill flag set
                return None

            if best is None or (
                (cur.maxxer_turn() and score > best) or
                (cur.minner_turn() and score < best)
            ):

                if prune(cur, score, alpha, beta):
                    return score

                best = score

                if cur.maxxer_turn():
                    alpha = score if alpha is None else max(alpha, score)
                else:
                    beta = score if beta is None else min(beta, score)

                if depth == 0:
                    nonlocal best_move
                    best_move = move

        return best

    def wrapper(kill_flag: threading.Event,
                output_move: SharedMoveRef,
                all_terminals_searchd: SharedBoolRef) -> None:

        dfs(state, kill_flag)
        output_move[0] = None if kill_flag.is_set() else best_move
        all_terminals_searchd[0] = all_terminals_reached

    return wrapper
