from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from enum import Enum

from .gamestate import GameState

T = TypeVar("T", bound=GameState)


class Terminal(Enum):
    MINNER_WIN = float("-inf")
    DRAW = 0
    MAXXER_WIN = float("inf")


class Evaluator(ABC, Generic[T]):

    @abstractmethod
    def evaluate(state: T) -> float | Terminal:
        ...
