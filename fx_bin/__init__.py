# -*- coding: utf-8 -*-

"""Top-level package for Python FX bin."""

try:
    from importlib.metadata import version
except ImportError:
    # Python < 3.8 compatibility
    from importlib_metadata import version  # type: ignore

__author__ = """Frank Xu"""
__email__ = 'frank@frankxu.me'

try:
    __version__ = version("fx-bin")
except Exception:
    # Fallback version in case package is not installed
    __version__ = "0.9.4"
