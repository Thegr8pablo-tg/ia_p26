"""Auto-discovery of Strategy subclasses.

Scans two locations:
  1. Built-in strategies in this ``strategies/`` package.
  2. Student submissions under ``estudiantes/<user>/wordle/``.
"""

from __future__ import annotations

import importlib
import importlib.util
import pkgutil
import sys
from pathlib import Path

from strategy import Strategy

_PKG_DIR = Path(__file__).resolve().parent
# strategies/ -> code/ -> wordle/ -> 06_*/ -> clase/ -> repo root
_REPO_ROOT = _PKG_DIR.parents[4]
_STUDENTS_DIR = _REPO_ROOT / "estudiantes"


def _subclasses_in_module(mod) -> list[type[Strategy]]:  # type: ignore[type-arg]
    found: list[type[Strategy]] = []
    for attr_name in dir(mod):
        obj = getattr(mod, attr_name)
        if (
            isinstance(obj, type)
            and issubclass(obj, Strategy)
            and obj is not Strategy
        ):
            found.append(obj)
    return found


def _discover_builtin() -> list[type[Strategy]]:
    """Import all .py files in this package."""
    found: list[type[Strategy]] = []
    for info in pkgutil.iter_modules([str(_PKG_DIR)]):
        mod = importlib.import_module(f"strategies.{info.name}")
        found.extend(_subclasses_in_module(mod))
    return found


def _discover_students() -> list[type[Strategy]]:
    """Scan ``estudiantes/*/wordle/`` for strategy files."""
    found: list[type[Strategy]] = []
    if not _STUDENTS_DIR.is_dir():
        return found

    for user_dir in sorted(_STUDENTS_DIR.iterdir()):
        wordle_dir = user_dir / "wordle"
        if not wordle_dir.is_dir():
            continue
        for py_file in sorted(wordle_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            mod_name = f"student_{user_dir.name}_{py_file.stem}"
            try:
                spec = importlib.util.spec_from_file_location(mod_name, py_file)
                if spec is None or spec.loader is None:
                    continue
                mod = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = mod
                spec.loader.exec_module(mod)  # type: ignore[union-attr]
                found.extend(_subclasses_in_module(mod))
            except Exception as exc:
                print(f"  [warn] failed to load {py_file}: {exc}")

    return found


def discover_strategies() -> list[type[Strategy]]:
    """Return all Strategy subclasses (built-in + student submissions)."""
    return _discover_builtin() + _discover_students()
