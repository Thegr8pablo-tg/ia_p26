#!/usr/bin/env python3
"""Run all discovered strategies and compare them.

Features:
  - Auto-discovers built-in strategies AND student submissions.
  - Runs strategies in parallel (one process per strategy).
  - Supports two probability modes: ``uniform`` and ``frequency``.
  - Outputs summary table, CSV, and histogram.
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

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

        print(f"\n{'Strategy':<25} {'Games':>6} {'Solved':>7} {'Rate':>6} "
              f"{'Mean':>6} {'Median':>7} {'Max':>5}")
        print("-" * 72)
        # Sort by mean guesses (ascending = best first)
        ranking = sorted(by_strat.items(), key=lambda kv: sum(r.num_guesses for r in kv[1]) / len(kv[1]))
        for name, results in ranking:
            n = len(results)
            solved = sum(1 for r in results if r.solved)
            guesses = sorted(r.num_guesses for r in results)
            mean = sum(guesses) / n
            median = guesses[n // 2] if n % 2 == 1 else (
                guesses[n // 2 - 1] + guesses[n // 2]
            ) / 2
            mx = max(guesses)
            rate = 100 * solved / n
            print(f"{name:<25} {n:>6} {solved:>6}  {rate:>5.1f}% "
                  f"{mean:>6.2f} {median:>7.1f} {mx:>5}")
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

        cols = min(n_strats, 4)
        rows = (n_strats + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows), squeeze=False)
        max_guess = max(g.num_guesses for g in self.games)
        bins = list(range(1, max_guess + 2))

        for idx, name in enumerate(strats):
            ax = axes[idx // cols][idx % cols]
            ax.hist(by_strat[name], bins=bins, edgecolor="black", align="left")
            ax.set_title(name, fontsize=10)
            ax.set_xlabel("Guesses")
            ax.set_ylabel("Count")

        # Hide unused axes
        for idx in range(n_strats, rows * cols):
            axes[idx // cols][idx % cols].set_visible(False)

        fig.suptitle("Guess-count distribution by strategy")
        fig.tight_layout()
        dest = Path(path) if path else RESULTS_DIR / "tournament_histograms.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(dest, dpi=150)
        plt.close(fig)
        print(f"Histogram saved to {dest}")


# ------------------------------------------------------------------
# Worker function (runs in a child process)
# ------------------------------------------------------------------

def _run_strategy_worker(
    strat_cls_info: tuple[str, str],  # (module_file_or_builtin, class_name)
    vocabulary: list[str],
    secrets: list[str],
    word_length: int,
    max_guesses: int,
    allow_non_words: bool,
) -> list[GameResult]:
    """Run a single strategy against all secrets. Executed in a subprocess."""
    import importlib
    import importlib.util
    import sys as _sys
    from pathlib import Path as _Path

    # We need to make the code directory importable in the worker
    code_dir = str(_Path(__file__).resolve().parent)
    if code_dir not in _sys.path:
        _sys.path.insert(0, code_dir)

    from strategy import Strategy as _Strategy
    from wordle_env import WordleEnv

    source, cls_name = strat_cls_info

    # Reconstruct the class
    if source == "__builtin__":
        # Built-in: discover again in this process
        from strategies import _discover_builtin
        for cls in _discover_builtin():
            if cls.__name__ == cls_name:
                break
        else:
            raise RuntimeError(f"Built-in strategy class {cls_name} not found")
    else:
        # Student file
        spec = importlib.util.spec_from_file_location(f"_worker_{cls_name}", source)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load {source}")
        mod = importlib.util.module_from_spec(spec)
        _sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        cls = None
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type) and issubclass(obj, _Strategy) and obj is not _Strategy and obj.__name__ == cls_name:
                cls = obj
                break
        if cls is None:
            raise RuntimeError(f"Class {cls_name} not found in {source}")

    strat = cls()
    env = WordleEnv(
        vocabulary=vocabulary,
        word_length=word_length,
        max_guesses=max_guesses,
        allow_non_words=allow_non_words,
    )

    results: list[GameResult] = []
    for secret in secrets:
        env.reset(secret=secret)
        strat.begin_game(word_length, vocabulary)
        while not env.game_over():
            word = strat.guess(env.history)
            env.guess(word)
        strat.end_game(secret, env.is_solved(), len(env.history))
        results.append(GameResult(
            strategy=strat.name,
            secret=secret,
            num_guesses=len(env.history),
            solved=env.is_solved(),
        ))

    return results


# ------------------------------------------------------------------
# Tournament runner
# ------------------------------------------------------------------

def run_tournament(
    vocabulary: list[str],
    secrets: list[str] | None = None,
    word_length: int = 5,
    max_guesses: int = 6,
    num_games: int | None = None,
    seed: int = 42,
    allow_non_words: bool = False,
    max_workers: int | None = None,
) -> TournamentResults:
    from strategies import discover_strategies, _discover_builtin, _discover_students, _PKG_DIR, _STUDENTS_DIR

    rng = random.Random(seed)
    if secrets is None:
        secrets = list(vocabulary)
    if num_games is not None and num_games < len(secrets):
        secrets = rng.sample(secrets, num_games)

    # Prepare strategy descriptors for workers
    strat_infos: list[tuple[tuple[str, str], str]] = []  # ((source, cls_name), display_name)

    for cls in _discover_builtin():
        inst = cls()
        strat_infos.append((("__builtin__", cls.__name__), inst.name))

    for cls in _discover_students():
        inst = cls()
        # Find the source file
        src_file = sys.modules.get(cls.__module__)
        if src_file and hasattr(src_file, "__file__") and src_file.__file__:
            strat_infos.append(((src_file.__file__, cls.__name__), inst.name))
        else:
            strat_infos.append((("__builtin__", cls.__name__), inst.name))

    if not strat_infos:
        print("No strategies found.", file=sys.stderr)
        return TournamentResults()

    print(f"Running {len(strat_infos)} strategies on {len(secrets)} words "
          f"(parallel workers: {max_workers or 'auto'}) ...")

    results = TournamentResults()

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for info, display_name in strat_infos:
            fut = executor.submit(
                _run_strategy_worker,
                info,
                vocabulary,
                secrets,
                word_length,
                max_guesses,
                allow_non_words,
            )
            futures[fut] = display_name

        for fut in as_completed(futures):
            name = futures[fut]
            try:
                game_results = fut.result()
                results.games.extend(game_results)
                solved = sum(1 for g in game_results if g.solved)
                mean = sum(g.num_guesses for g in game_results) / len(game_results)
                print(f"  {name:<25} done — {solved}/{len(game_results)} solved, "
                      f"mean {mean:.2f}")
            except Exception as exc:
                print(f"  {name:<25} FAILED: {exc}", file=sys.stderr)

    return results


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Wordle strategy tournament",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  python tournament.py                                  # mini lexicon, uniform
  python tournament.py --mode frequency                 # frequency-weighted
  python tournament.py --mode both                      # run both modes
  python tournament.py --words data/spanish_5letter.csv # big downloaded list
  python tournament.py --length 6 --max-guesses 8       # 6-letter variant
  python tournament.py --num-games 100                  # subsample 100 secrets
""",
    )
    parser.add_argument("--words", type=str, default=None, help="Path to word list (.txt or .csv)")
    parser.add_argument("--length", type=int, default=5, help="Word length (default: 5)")
    parser.add_argument("--max-guesses", type=int, default=6, help="Max guesses per game (default: 6)")
    parser.add_argument("--num-games", type=int, default=None, help="Limit number of secret words to test")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--allow-non-words", action="store_true", help="Allow non-vocabulary guesses")
    parser.add_argument("--mode", choices=["uniform", "frequency", "both"], default="uniform",
                        help="Probability mode (default: uniform)")
    parser.add_argument("--workers", type=int, default=None, help="Max parallel workers (default: auto)")
    parser.add_argument("--csv", type=str, default=None, help="Save results CSV path")
    parser.add_argument("--plot", type=str, default=None, help="Save histogram path")
    args = parser.parse_args()

    from lexicon import load_lexicon

    modes = ["uniform", "frequency"] if args.mode == "both" else [args.mode]

    for mode in modes:
        print(f"\n{'='*60}")
        print(f"  MODE: {mode}")
        print(f"{'='*60}\n")

        lex = load_lexicon(path=args.words, word_length=args.length, mode=mode)
        print(f"Vocabulary: {len(lex.words)} words of length {args.length} "
              f"(source: {'CSV' if args.words and args.words.endswith('.csv') else 'txt'}, "
              f"mode: {lex.mode})")

        t0 = time.time()
        results = run_tournament(
            vocabulary=lex.words,
            word_length=args.length,
            max_guesses=args.max_guesses,
            num_games=args.num_games,
            seed=args.seed,
            allow_non_words=args.allow_non_words,
            max_workers=args.workers,
        )
        elapsed = time.time() - t0

        results.print_summary()
        print(f"Elapsed: {elapsed:.1f}s")

        suffix = f"_{mode}" if len(modes) > 1 else ""
        csv_path = args.csv or str(RESULTS_DIR / f"tournament{suffix}.csv")
        results.to_csv(csv_path)
        print(f"CSV saved to {csv_path}")

        plot_path = args.plot or str(RESULTS_DIR / f"tournament{suffix}.png")
        results.plot_histograms(plot_path)


if __name__ == "__main__":
    main()
