"""Auto-discovery of Strategy subclasses in this package."""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from strategy import Strategy


def discover_strategies() -> list[type[Strategy]]:
    """Import every module in this package and return all Strategy subclasses."""
    pkg_dir = Path(__file__).resolve().parent
    found: list[type[Strategy]] = []

    for info in pkgutil.iter_modules([str(pkg_dir)]):
        mod = importlib.import_module(f"strategies.{info.name}")
        for attr_name in dir(mod):
            obj = getattr(mod, attr_name)
            if (
                isinstance(obj, type)
                and issubclass(obj, Strategy)
                and obj is not Strategy
            ):
                found.append(obj)

    return found
