"""Column Alignment Sorter.

Sorts lines of whitespace-aligned text by a user-specified column index while
preserving the visual alignment of the remaining columns. This module
re-exports the public API of the library for convenient single-import usage.

Exports:
    ColumnSorter: class for sorting aligned text blocks.
    sort_lines: convenience function wrapping :class:`ColumnSorter`.
    ColumnSortError: exception raised for invalid input.
"""

from __future__ import annotations

from .core import ColumnSortError, ColumnSorter, sort_lines

__all__ = ["ColumnSortError", "ColumnSorter", "sort_lines"]
