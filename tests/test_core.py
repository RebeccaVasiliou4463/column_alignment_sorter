"""Tests for :mod:`column_alignment_sorter.core`.

These tests exercise the documented behaviour only. Awkward cases covered:
multi-space alignment, tab delimiters, descending order, numeric coercion with
blank and non-numeric values, case folding, ragged input rejection, and
stability of rows sharing a key.
"""

from __future__ import annotations

import unittest

from column_alignment_sorter import ColumnSortError, ColumnSorter, sort_lines


class TestColumnSorter(unittest.TestCase):
    def test_sort_by_second_column_ascending(self):
        lines = [
            "alpha   2 first",
            "beta    1 second",
            "gamma   3 third",
        ]
        result = sort_lines(lines, 1)
        self.assertEqual(
            result,
            [
                "beta    1 second",
                "alpha   2 first",
                "gamma   3 third",
            ],
        )

    def test_sort_by_first_column(self):
        lines = ["banana yellow", "apple red", "cherry dark"]
        self.assertEqual(
            sort_lines(lines, 0),
            ["apple red", "banana yellow", "cherry dark"],
        )

    def test_descending_order(self):
        lines = ["a 1", "b 3", "c 2"]
        result = sort_lines(lines, 1, descending=True)
        self.assertEqual([row.split()[0] for row in result], ["b", "c", "a"])

    def test_numeric_sort_treats_values_as_numbers(self):
        lines = ["row1 10", "row2 2", "row3 1"]
        result = sort_lines(lines, 1, numeric=True)
        self.assertEqual(
            [row.split()[0] for row in result],
            ["row3", "row2", "row1"],
        )

    def test_stable_order_for_equal_keys(self):
        lines = [
            "first  1 keep",
            "second 1 drop",
            "third  1 change",
        ]
        result = sort_lines(lines, 1)
        self.assertEqual(result, lines)

    def test_case_insensitive_sort(self):
        lines = ["Banana 1", "apple 2", "Cherry 3"]
        result = sort_lines(lines, 0, ignore_case=True)
        self.assertEqual([row.split()[1] for row in result], ["2", "1", "3"])

    def test_case_sensitive_default(self):
        lines = ["banana 1", "Apple 2", "cherry 3"]
        result = sort_lines(lines, 0)
        self.assertEqual([row.split()[1] for row in result], ["2", "1", "3"])

    def test_blank_numeric_key_sorts_last(self):
        lines = ["a 3", "b ", "c 1"]
        result = sort_lines(lines, 1, numeric=True)
        self.assertEqual([row.split()[0] for row in result], ["c", "a", "b"])

    def test_non_numeric_value_raises(self):
        lines = ["a 1", "b two"]
        with self.assertRaises(ColumnSortError):
            sort_lines(lines, 1, numeric=True)

    def test_too_few_columns_raises(self):
        lines = ["a 1", "b"]
        with self.assertRaises(ColumnSortError):
            sort_lines(lines, 1)

    def test_negative_index_rejected(self):
        with self.assertRaises(ValueError):
            ColumnSorter(-1)

    def test_bool_index_rejected(self):
        with self.assertRaises(TypeError):
            ColumnSorter(True)  # noqa: FBT003

    def test_string_input_rejected(self):
        with self.assertRaises(TypeError):
            sort_lines("a 1\nb 2", 1)  # type: ignore[arg-type]

    def test_non_string_element_rejected(self):
        with self.assertRaises(TypeError):
            sort_lines(["a 1", 42], 1)  # type: ignore[list-item]

    def test_leading_whitespace_does_not_phantom_column(self):
        lines = ["  a 1", "  b 2"]
        result = sort_lines(lines, 1)
        self.assertEqual([row.split()[0] for row in result], ["a", "b"])

    def test_tab_delimited_columns(self):
        lines = ["alpha\t2", "beta\t1"]
        result = sort_lines(lines, 1)
        self.assertEqual([row.split("\t")[0] for row in result], ["beta", "alpha"])

    def test_zero_column_index(self):
        lines = ["z 1", "a 2", "m 3"]
        result = sort_lines(lines, 0)
        self.assertEqual([row.split()[0] for row in result], ["a", "m", "z"])

    def test_returns_new_list_not_mutating_input(self):
        lines = ["b 2", "a 1"]
        original = list(lines)
        result = sort_lines(lines, 1)
        self.assertIsNot(result, lines)
        self.assertEqual(lines, original)
        self.assertEqual([row.split()[0] for row in result], ["a", "b"])

    def test_single_line(self):
        lines = ["solo 1 only"]
        self.assertEqual(sort_lines(lines, 1), ["solo 1 only"])

    def test_empty_input_returns_empty_list(self):
        self.assertEqual(sort_lines([], 0), [])

    def test_column_index_exactly_at_boundary(self):
        lines = ["a b", "c d"]
        result = sort_lines(lines, 1)
        self.assertEqual([row.split()[0] for row in result], ["a", "c"])

    def test_is_value_error_subclass(self):
        self.assertTrue(issubclass(ColumnSortError, ValueError))


if __name__ == "__main__":
    unittest.main()
