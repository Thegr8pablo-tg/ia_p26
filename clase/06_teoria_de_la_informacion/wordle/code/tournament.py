#!/usr/bin/env python3
"""Run all discovered strategies on a shared set of secret words and compare."""

from __future__ import annotations

import argparse
import csv
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

from lexicon import load_words
from strategy import Strategy
from strategies import discover_strategies
from wordle_env import WordleEnv

RESULTS_DIR = Path(__file__).resolve().parent / "results"


# ------------------------------------------------------------------
# Result containers
# ------------------------------------------------------------------

@dataclass
class GameResult:
    strategy: str
    secret: str
    num_guesses: int
    solved: bool


@dataclass
class TournamentResults:
    games: list[GameResult] = field(default_factory=list)

    def to_csv(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["strategy", "secret", "num_guesses", "solved"])
            for g in self.games:
                writer.writerow([g.strategy, g.secret, g.num_guesses, int(g.solved)])

    def print_summary(self) -> None:
        from collections import defaultdict

        by_strat: dict[str, list[GameResult]] = defaultdict(list)
        for g in self.games:
            by_strat[g.strategy].append(g)

        print(f"\n{'Strategy':<20} {'Games':>6} {'Solved':>7} {'Mean':>6} {'Median':>7} {'Max':>5}")
        print("-" * 60)
        for name, results in sorted(by_strat.items()):
            n = len(results)
            solved = sum(1 for r in results if r.solved)
            guesses = [r.num_guesses for r in results]
            guesses_sorted = sorted(guesses)
            mean = sum(guesses) / n
            median = guesses_sorted[n // 2] if n % 2 == 1 else (
                guesses_sorted[n // 2 - 1] + guesses_sorted[n // 2]
            ) / 2
            mx = max(guesses)
            print(f"{name:<20} {n:>6} {solved:>6}{'':1} {mean:>6.2f} {median:>7.1f} {mx:>5}")
        print()

    def plot_histograms(self, path: str | Path | None = None) -> None:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not installed — skipping plot", file=sys.stderr)
            return

        from collections import defaultdict

        by_strat: dict[str, list[int]] = defaultdict(list)
        for g in self.games:
            by_strat[g.strategy].append(g.num_guesses)

        strats = sorted(by_strat.keys())
        n_strats = len(strats)
        if n_strats == 0:
            return

        fig, axes = plt.subplots(1, n_strats, figsize=(5 * n_strats, 4), squeeze=False)
        max_guess = max(g.num_guesses for g in self.games)
        bins = list(range(1, max_guess + 2))

        for ax, name in zip(axes[0], strats):
            ax.hist(by_strat[name], bins=bins, edgecolor="black", align="left")
            ax.set_title(name)
            ax.set_xlabel("Guesses")
            ax.set_ylabel("Count")

        fig.suptitle("Guess-count distribution by strategy")
        fig.tight_layout()
        dest = Path(path) if path else RESULTS_DIR / "tournament_histograms.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(dest, dpi=150)
        plt.close(fig)
        print(f"Histogram saved to {dest}")


# ------------------------------------------------------------------
# Tournament runner
# ------------------------------------------------------------------

def run_tournament(
    strategies: list[Strategy],
    vocabulary: list[str],
    secrets: list[str] | None = None,
    word_length: int = 5,
    max_guesses: int = 6,
    num_games: int | None = None,
    seed: int = 42,
    allow_non_words: bool = False,
) -> TournamentResults:
    rng = random.Random(seed)

    if secrets is None:
        secrets = list(vocabulary)
    if num_games is not None and num_games < len(secrets):
        secrets = rng.sample(secrets, num_games)

    env = WordleEnv(
        vocabulary=vocabulary,
        word_length=word_length,
        max_guesses=max_guesses,
        allow_non_words=allow_non_words,
    )

    results = TournamentResults()

    for strat in strategies:
        for secret in secrets:
            env.reset(secret=secret)
            strat.begin_game(word_length, vocabulary)
            while not env.game_over():
                word = strat.guess(env.history)
                env.guess(word)
            strat.end_game(secret, env.is_solved(), len(env.history))
            results.games.append(
                GameResult(
                    strategy=strat.name,
                    secret=secret,
                    num_guesses=len(env.history),
                    solved=env.is_solved(),
                )
            )

    return results


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Wordle strategy tournament")
    parser.add_argument("--words", type=str, default=None, help="Path to word list")
    parser.add_argument("--length", type=int, default=5, help="Word length")
    parser.add_argument("--max-guesses", type=int, default=6, help="Max guesses per game")
    parser.add_argument("--num-games", type=int, default=None, help="Limit number of games")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--allow-non-words", action="store_true", help="Allow non-vocabulary guesses")
    parser.add_argument("--csv", type=str, default=None, help="Save results CSV to this path")
    parser.add_argument("--plot", type=str, default=None, help="Save histogram to this path")
    args = parser.parse_args()

    vocab = load_words(path=args.words, word_length=args.length)
    if not vocab:
        print(f"No words of length {args.length} found.", file=sys.stderr)
        sys.exit(1)
    print(f"Vocabulary: {len(vocab)} words of length {args.length}")

    strat_classes = discover_strategies()
    if not strat_classes:
        print("No strategies found in strategies/", file=sys.stderr)
        sys.exit(1)

    strategies = [cls() for cls in strat_classes]
    print(f"Strategies: {[s.name for s in strategies]}")

    results = run_tournament(
        strategies=strategies,
        vocabulary=vocab,
        word_length=args.length,
        max_guesses=args.max_guesses,
        num_games=args.num_games,
        seed=args.seed,
        allow_non_words=args.allow_non_words,
    )

    results.print_summary()

    csv_path = args.csv or RESULTS_DIR / "tournament_results.csv"
    results.to_csv(csv_path)
    print(f"Results saved to {csv_path}")

    results.plot_histograms(args.plot)


if __name__ == "__main__":
    main()
