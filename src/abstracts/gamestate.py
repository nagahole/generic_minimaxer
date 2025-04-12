from typing import Self, Iterable, TypeVar
from abc import ABC, abstractmethod

TMove = TypeVar("TMove")

class GameState(ABC):

    @abstractmethod
    def make_move(self, move: TMove) -> None:
        ...

    @abstractmethod
    def get_next_states(self) -> Iterable[tuple[TMove, Self]]:
        ...

    @abstractmethod
    def maxxer_turn(self) -> bool:
        ...

    @abstractmethod
    def minner_turn(self) -> bool:
        ...
