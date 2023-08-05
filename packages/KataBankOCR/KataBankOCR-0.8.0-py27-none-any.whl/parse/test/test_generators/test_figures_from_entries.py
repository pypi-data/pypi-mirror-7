"test the figures_from_entries generator"

import pytest

from parse.generators.figures_from_entries import figures_from_entries

import check_generator
from common_tools import adulterate_iterable
from fixture_methods import Entries, Lines, Accounts, Figures

test_iterability = check_generator.raises_on_non_iterable(generator=figures_from_entries)

test_element_type = \
    check_generator.raises_on_bad_element_type(generator=figures_from_entries,
                                               value_or_type=Entries.get_random())

test_element_length = \
    check_generator.raises_on_bad_element_length(generator=figures_from_entries,
                                                 valid_element=Entries.get_random())

def _raises_on_faulty_line(fault, faulty_lines):
    "confirm figures_from_entries raises on invalid Line within Entry"
    for line in faulty_lines:
        adulterated_entry = adulterate_iterable(Entries.get_random(), line)
        iterator = figures_from_entries((adulterated_entry,))
        error = pytest.raises((ValueError, TypeError), tuple, iterator)
        for message in ('Entry Line', fault):
            assert message in error.value.message

test_line_type = lambda: _raises_on_faulty_line(fault='of unexpected type',
                                                faulty_lines=Lines.of_invalid_types())

test_line_legth = lambda: _raises_on_faulty_line(fault='of unexpected length',
                                                 faulty_lines=Lines.of_invalid_lengths())

test_line_compositions = \
    lambda: _raises_on_faulty_line(fault='contains unexpected element',
                                   faulty_lines=Lines.with_invalid_strokes())

def test_identifies_known_entries_as_expected_figures():
    "confirm figures_from_entries finds correct Figures in Entries"
    account = Accounts.get_random()
    expected_figures = Figures.from_account(account)
    entry = Entries.from_account(account)
    iterator = figures_from_entries((entry,))
    found_figures = tuple(iterator)
    assert expected_figures == found_figures
