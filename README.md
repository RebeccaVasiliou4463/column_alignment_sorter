# Column Alignment Sorter

Sorts lines of whitespace-aligned text by a user-specified column index while
preserving the visual alignment of the remaining columns.

## Usage

```python
from column_alignment_sorter import sort_lines

lines = [
    "apple   2 fruit",
    "banana  1 fruit",
    "cherry  3 fruit",
]

# Sort by the numeric column (index 1), ascending.
sorted_lines = sort_lines(lines, 1, numeric=True)
print("\n".join(sorted_lines))
```

Exports:

- `ColumnSorter(column_index, *, descending=False, numeric=False, ignore_case=False)`
  — configurable sorter. Call `.sort(lines)` to get an ordered list.
- `sort_lines(lines, column_index, *, descending=False, numeric=False, ignore_case=False)`
  — one-shot convenience wrapper.
- `ColumnSortError` — raised on ragged input or non-numeric key values.

## Why this exists

Tabular text is often aligned with runs of spaces rather than a single
delimiter. A sorter that splits on whitespace runs and reassembles by column
index handles this without knowing the original column widths. The trade-off:
the library does not re-pad columns; it returns the original line objects in
the new order, so whatever alignment the input had is preserved exactly.

## Awkward edge

Numeric mode (`numeric=True`) coerces the key column to `float`. A blank value
in the key column is treated as positive infinity and sorts last in ascending
order. Non-numeric text in the key column raises `ColumnSortError` rather than
silently coercing to `nan`, which would poison any comparison.

Case folding (`ignore_case=True`) uses `str.lower` on the key text; it has no
effect when `numeric=True` is also set.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

