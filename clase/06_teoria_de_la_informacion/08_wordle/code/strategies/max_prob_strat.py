"""Max-probability strategy: always guess the first remaining candidate."""

from __future__ import annotations

from strategy import Strategy
from wordle_env import filter_candidates


class MaxProbStrategy(Strategy):
    """Always guess the first candidate (alphabetical order).

    With a uniform prior this is equivalent to guessing the
    "most probable" remaining word. A simple baseline that
    demonstrates the strategy interface.
    """

    @property
    def name(self) -> str:
        return "MaxProb"

    def begin_game(self, word_length: int, vocabulary: list[str]) -> None:
        self._candidates = sorted(vocabulary)

    def guess(self, history: list[tuple[str, tuple[int, ...]]]) -> str:
        candidates = self._candidates
        for g, pat in history:
            candidates = filter_candidates(candidates, g, pat)
        if not candidates:
            return self._candidates[0]
        return candidates[0]
