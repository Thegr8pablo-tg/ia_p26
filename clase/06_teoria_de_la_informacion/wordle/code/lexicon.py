"""Word-list loading utilities (self-contained)."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path


_DIR = Path(__file__).resolve().parent
_MINI_PATH = _DIR / "data" / "mini_spanish_5.txt"


def _strip_accents(text: str) -> str:
    """Remove combining diacritical marks (á→a, ñ→n, ü→u, etc.)."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if unicodedata.category(ch) != "Mn")


def load_words(
    path: str | None = None,
    word_length: int = 5,
) -> list[str]:
    """Load a word list, filtered to *word_length*.

    Parameters
    ----------
    path : str or None
        Path to a text file with one word per line.
        If None, falls back to ``data/mini_spanish_5.txt``.
    word_length : int
        Only words of exactly this length are kept.

    Returns
    -------
    list[str]
        Sorted, deduplicated, lowercased words (accents stripped).
    """
    src = Path(path) if path is not None else _MINI_PATH
    if not src.exists():
        raise FileNotFoundError(f"Word list not found: {src}")

    pattern = re.compile(rf"^[a-z]{{{word_length}}}$")
    seen: set[str] = set()
    words: list[str] = []

    for raw_line in src.read_text(encoding="utf-8").splitlines():
        w = _strip_accents(raw_line.strip().lower())
        if not w or w in seen:
            continue
        if pattern.match(w):
            seen.add(w)
            words.append(w)

    words.sort()
    return words
