"""Core implementation of the Column Alignment Sorter.

The library operates on a single concrete data model: input is text split into
lines, columns are delimited by runs of whitespace (one or more spaces or tabs),
and the sort key is the textual content of a chosen column.

Design decisions (documented because they are not obvious):

* **Column definition**: a column is a maximal run of non-whitespace characters.
  Lines are split using :meth:`str.split` (default behaviour), which treats any
  run of whitespace as a single delimiter and strips leading and trailing
  whitespace. This is simpler than fixed-width parsing and is the natural model
  for text aligned with spaces. The trade-off: lines must be columnar in the
  sense that each line has the same number of fields, though padding is
  permitted.

* **Stability**: Python's :func:`sorted` is guaranteed stable. This library
  relies on that guarantee so that rows sharing a sort key retain their input
  order.

* **Type coercion**: comparison is always lexical (string comparison) to avoid
  surprises when a column contains mixed numeric and textual values. Numeric
  parsing would impose opinions about what counts as a number; lexical
  comparison is unambiguous and predictable.

* **Numeric key support**: a separate ``numeric=True`` flag coerces the key
  column to :class:`float`. A blank value is treated as positive infinity so
  it sorts last, which keeps the operation well-defined for ragged input.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple


class ColumnSortError(ValueError):
    """Raised when the input to the sorter is malformed.

    Inherits from :class:`ValueError` so callers catching broad value errors
    will still intercept it.
    """


class ColumnSorter:
    """Sort aligned text lines by a given column index.

    The sorter is stateless beyond its configuration; the same instance can be
    reused for multiple inputs.

    Args:
        column_index: Zero-based index of the column to sort by.
        descending: If ``True``, sort in descending order. Default ``False``.
        numeric: If ``True``, treat the key column as a number (parsed via
            :func:`float`). Blank key values sort as positive infinity, i.e.
            last in ascending order. Default ``False``.
        ignore_case: If ``True``, fold ASCII case when comparing string keys.
            Only affects textual comparison; ignored when ``numeric`` is
            ``True``. Default ``False``.
    """

    _infinity = float("inf")

    def __init__(
        self,
        column_index: int,
        *,
        descending: bool = False,
        numeric: bool = False,
        ignore_case: bool = False,
    ) -> None:
        if not isinstance(column_index, int) or isinstance(column_index, bool):
            raise TypeError("column_index must be an int")
        if column_index < 0:
            raise ValueError("column_index must be non-negative")
        self.column_index = column_index
        self.descending = bool(descending)
        self.numeric = bool(numeric)
        self.ignore_case = bool(ignore_case)

    def _extract_key(self, fields: Sequence[str]):
        """Return the sort key for one row's field list.

        When ``numeric`` is set we coerce the textual key to float so that
        ``"10"`` sorts after ``"2"``. A blank field is mapped to positive
        infinity: it is a missing value, and missing values should not
        pollute the ordering of present values. Non-numeric text raises
        :class:`ColumnSortError` rather than silently coercing.
        """
        if len(fields) <= self.column_index:
            if self.numeric:
                return self._infinity
            raise ColumnSortError(
                f"line has {len(fields)} field(s); need at least "
                f"{self.column_index + 1}"
            )
        text = fields[self.column_index]
        if self.numeric:
            stripped = text.strip()
            if stripped == "":
                return self._infinity
            try:
                return float(stripped)
            except ValueError as exc:
                raise ColumnSortError(
                    f"non-numeric value in column {self.column_index}: {text!r}"
                ) from exc
        if self.ignore_case:
            return text.lower()
        return text

    def sort(self, lines: Sequence[str]) -> List[str]:
        """Return a new list containing *lines* sorted by the configured column.

        Args:
            lines: Sequence of strings. Each line must contain at least
                ``column_index + 1`` whitespace-delimited fields. Leading and
                trailing whitespace on a line does not create phantom columns;
        :meth:`str.split` collapses runs of whitespace.

        Returns:
            A new list of the same strings, ordered by the key column.

        Raises:
            ColumnSortError: if a line has too few columns, or if ``numeric``
                is set and the key column contains text that is not parseable
                as a float.
            TypeError: if ``lines`` is not a sequence of strings.
        """
        if isinstance(lines, (str, bytes)):
            raise TypeError("lines must be a sequence of strings, not a string")
        try:
            iterator = iter(lines)
        except TypeError as exc:  # pragma: no cover - defensive
            raise TypeError("lines must be a sequence of strings") from exc

        parsed: List[Tuple[str, Sequence[str]]] = []
        for line in iterator:
            if not isinstance(line, str):
                raise TypeError("each line must be a string")
            fields = line.split()
            parsed.append((line, fields))

        return [
            line
            for line, _ in sorted(
                parsed,
                key=lambda pair: self._extract_key(pair[1]),
                reverse=self.descending,
            )
        ]


def sort_lines(
    lines: Sequence[str],
    column_index: int,
    *,
    descending: bool = False,
    numeric: bool = False,
    ignore_case: bool = False,
) -> List[str]:
    """Sort *lines* by *column_index*, returning a new list.

    This is a thin convenience wrapper around :class:`ColumnSorter` for callers
    who do not need to reuse configuration across multiple calls.

    Args:
        lines: Sequence of strings to sort.
        column_index: Zero-based column to sort by.
        descending: Sort descending if ``True``.
        numeric: Coerce the key column to :class:`float` if ``True``.
        ignore_case: Case-fold string keys if ``True`` (ignored when
            ``numeric`` is ``True``).

    Returns:
        A new list of strings ordered by the chosen column.
    """
    return ColumnSorter(
        column_index,
        descending=descending,
        numeric=numeric,
        ignore_case=ignore_case,
    ).sort(lines)
