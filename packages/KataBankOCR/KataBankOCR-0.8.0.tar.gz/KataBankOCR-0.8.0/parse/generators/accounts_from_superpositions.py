"generator that yields Accounts and the functions that support it"

from itertools import product

from toolz import pipe, curry
from toolz.curried import map as cmap

from parse import settings
from parse.validators import Validate

_superpositions_per_account = settings.figures_per_entry
_maximum_possible_errors_in_an_entry = settings.strokes_per_figure * settings.figures_per_entry

def accounts_from_superpositions(superpositions):
    "generator that consumes Superpositions and yields Accounts"
    collected = []
    for superposition in superpositions:
        Validate.type(dict, superposition, 'Superposition')
        collected.append(superposition)
        if len(collected) == _superpositions_per_account:
            yield _account(collected)
            collected = []

def _account(superpositions):
    "return a single [in]valid Account"
    valid_accounts = _valid_accounts(superpositions)
    if len(valid_accounts) == 1:
        return valid_accounts.pop()
    return _invalid_or_illegible_account(superpositions)

def _invalid_or_illegible_account(superpositions):
    "return the invalid or illegible Account represented by Superpositions"
    return pipe(superpositions, cmap(_numeral), ''.join)

def _numeral(superposition):
    "return Numeral represented by Superposition"
    try:
        return superposition[0].pop()
    except KeyError:
        return settings.illegible_numeral

def _valid_accounts(superpositions):
    "return valid Accounts with fewest errors (omitted/added strokes)"
    for error_count in range(_maximum_possible_errors_in_an_entry):
        accounts = _valid_accounts_by_error_count(superpositions, error_count)
        if accounts:
            return accounts

def _valid_accounts_by_error_count(superpositions, error_count):
    "return valid Accounts containing exactly error_count errors"
    accounts = set()
    for distribution in _error_distributions(superpositions, error_count):
        numeral_sets = _numeral_sets_by_error_distribution(superpositions, distribution)
        accounts |= _valid_accounts_from_numeral_sets(numeral_sets)
    return accounts

def _error_distributions(superpositions, total_errors):
    "return lists of error_counts each list with exactly total_errors"
    ECs_by_sup = curry(_error_counts_by_superposition, total_errors)
    error_distributions = product(*map(ECs_by_sup, superpositions))
    return [dist for dist in error_distributions if sum(dist) == total_errors]

def _error_counts_by_superposition(max_error_count, superposition):
    "return list of error counts <= max_error_count"
    return [error_count for error_count in superposition.keys() if error_count <= max_error_count]

def _numeral_sets_by_error_distribution(superpositions, distribution):
    "return sets of numerals with error counts matching distribution"
    return [sup[err_count] for sup, err_count in zip(superpositions, distribution)]

def _valid_accounts_from_numeral_sets(numeral_sets):
    "return valid accounts assemblable from numeral sets"
    accounts = _accounts_from_numeral_sets(numeral_sets)
    return set(filter(settings.checksum, accounts))

def _accounts_from_numeral_sets(numeral_sets):
    "return all possible accounts assemblable from numeral sets"
    return map(''.join, product(*numeral_sets))
