from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from .gamestate import GameState

T = TypeVar("T", bound=GameState)


class Evaluator(ABC, Generic[T]):

    @abstractmethod
    def evaluate(state: T) -> float:
        ...
