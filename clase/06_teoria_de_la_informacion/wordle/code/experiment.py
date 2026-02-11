#!/usr/bin/env python3
"""Run a single strategy with detailed per-game output."""

from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

from lexicon import load_words
from strategy import Strategy
from strategies import discover_strategies
from wordle_env import WordleEnv, feedback, filter_candidates

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def _entropy_bits(n: int) -> float:
    """Entropy of a uniform distribution over *n* items (bits)."""
    return math.log2(n) if n > 1 else 0.0


def _find_strategy(name: str) -> type[Strategy]:
    for cls in discover_strategies():
        if cls().name.lower() == name.lower():
            return cls
    available = [cls().name for cls in discover_strategies()]
    print(f"Strategy '{name}' not found. Available: {available}", file=sys.stderr)
    sys.exit(1)


def run_experiment(
    strat: Strategy,
    vocabulary: list[str],
    word_length: int = 5,
    max_guesses: int = 6,
    num_games: int = 10,
    seed: int = 42,
    allow_non_words: bool = False,
    verbose: bool = False,
) -> list[dict]:
    rng = random.Random(seed)
    secrets = rng.sample(vocabulary, min(num_games, len(vocabulary)))

    env = WordleEnv(
        vocabulary=vocabulary,
        word_length=word_length,
        max_guesses=max_guesses,
        allow_non_words=allow_non_words,
    )

    logs: list[dict] = []

    for i, secret in enumerate(secrets, 1):
        env.reset(secret=secret)
        strat.begin_game(word_length, vocabulary)

        candidates = list(vocabulary)
        game_log: list[dict] = []

        if verbose:
            print(f"\n--- Game {i}/{len(secrets)} | Secret: {secret} ---")

        while not env.game_over():
            word = strat.guess(env.history)
            pat = env.guess(word)
            candidates = filter_candidates(candidates, word, pat)
            ent = _entropy_bits(len(candidates))

            step = {
                "guess": word,
                "feedback": pat,
                "remaining": len(candidates),
                "entropy_bits": round(ent, 3),
            }
            game_log.append(step)

            if verbose:
                pat_str = "".join(
                    {2: "\u2705", 1: "\U0001f7e8", 0: "\u2b1b"}[c] for c in pat
                )
                print(
                    f"  Guess {len(game_log)}: {word}  {pat_str}  "
                    f"remaining={len(candidates)}  H={ent:.2f} bits"
                )

        strat.end_game(secret, env.is_solved(), len(env.history))
        result = {
            "game": i,
            "secret": secret,
            "solved": env.is_solved(),
            "num_guesses": len(env.history),
            "steps": game_log,
        }
        logs.append(result)

        if verbose:
            status = "SOLVED" if env.is_solved() else "FAILED"
            print(f"  → {status} in {len(env.history)} guesses")

    return logs


def print_experiment_summary(logs: list[dict], strategy_name: str) -> None:
    n = len(logs)
    solved = sum(1 for g in logs if g["solved"])
    guesses = [g["num_guesses"] for g in logs]
    mean = sum(guesses) / n if n else 0
    guesses_sorted = sorted(guesses)
    median = (
        guesses_sorted[n // 2]
        if n % 2 == 1
        else (guesses_sorted[n // 2 - 1] + guesses_sorted[n // 2]) / 2
    )
    print(f"\n=== {strategy_name} — {n} games ===")
    print(f"  Solved: {solved}/{n} ({100 * solved / n:.1f}%)")
    print(f"  Guesses — mean: {mean:.2f}, median: {median:.1f}, max: {max(guesses)}")


def plot_distribution(logs: list[dict], strategy_name: str, path: Path | None = None) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed — skipping plot", file=sys.stderr)
        return

    guesses = [g["num_guesses"] for g in logs]
    mx = max(guesses) if guesses else 6
    bins = list(range(1, mx + 2))

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(guesses, bins=bins, edgecolor="black", align="left")
    ax.set_title(f"{strategy_name} — guess distribution")
    ax.set_xlabel("Guesses")
    ax.set_ylabel("Count")
    fig.tight_layout()

    dest = path or RESULTS_DIR / f"experiment_{strategy_name.lower()}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {dest}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Single-strategy Wordle experiment")
    parser.add_argument("--strategy", type=str, required=True, help="Strategy name")
    parser.add_argument("--words", type=str, default=None, help="Path to word list")
    parser.add_argument("--length", type=int, default=5, help="Word length")
    parser.add_argument("--max-guesses", type=int, default=6, help="Max guesses per game")
    parser.add_argument("--num-games", type=int, default=10, help="Number of games")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--allow-non-words", action="store_true")
    parser.add_argument("--verbose", action="store_true", help="Print per-game details")
    parser.add_argument("--plot", type=str, default=None, help="Save plot to this path")
    args = parser.parse_args()

    vocab = load_words(path=args.words, word_length=args.length)
    if not vocab:
        print(f"No words of length {args.length} found.", file=sys.stderr)
        sys.exit(1)
    print(f"Vocabulary: {len(vocab)} words of length {args.length}")

    cls = _find_strategy(args.strategy)
    strat = cls()
    print(f"Strategy: {strat.name}")

    logs = run_experiment(
        strat=strat,
        vocabulary=vocab,
        word_length=args.length,
        max_guesses=args.max_guesses,
        num_games=args.num_games,
        seed=args.seed,
        allow_non_words=args.allow_non_words,
        verbose=args.verbose,
    )

    print_experiment_summary(logs, strat.name)
    plot_path = Path(args.plot) if args.plot else None
    plot_distribution(logs, strat.name, plot_path)


if __name__ == "__main__":
    main()
