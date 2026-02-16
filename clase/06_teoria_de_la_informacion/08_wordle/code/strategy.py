"""Abstract base class for Wordle strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Strategy(ABC):
    """Interface that every Wordle strategy must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable strategy name (used in reports)."""
        ...

    def begin_game(self, word_length: int, vocabulary: list[str]) -> None:
        """Called at the start of each game.

        Use this for precomputation (e.g. building pattern tables).
        The default implementation does nothing.
        """

    @abstractmethod
    def guess(self, history: list[tuple[str, tuple[int, ...]]]) -> str:
        """Return the next guess given the history of (guess, feedback) pairs."""
        ...

    def end_game(self, secret: str, solved: bool, num_guesses: int) -> None:
        """Called at the end of each game.

        Use this for learning, logging, or statistics.
        The default implementation does nothing.
        """
