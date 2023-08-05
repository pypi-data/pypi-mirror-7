"""
Alternate namespece for toolz such that all functions are curried

Currying provides implicit partial evaluation of all functions

Example:

    Get usually requires two arguments, an index and a collection
    >>> from toolz.curried import get
    >>> get(0, ('a', 'b'))
    'a'

    When we use it in higher order functions we often want to pass a partially
    evaluated form
    >>> data = [(1, 2), (11, 22), (111, 222)]
    >>> list(map(lambda seq: get(0, seq), data))
    [1, 11, 111]

    The curried version allows simple expression of partial evaluation
    >>> list(map(get(0), data))
    [1, 11, 111]

See Also:
    toolz.functoolz.curry
"""

import toolz
import toolz.curried_exceptions
from .functoolz import curry
import inspect


def _nargs(f):
    try:
        return len(inspect.getargspec(f).args)
    except TypeError:
        return None


def _should_curry(f):
    do_curry = set((toolz.map, toolz.filter, toolz.sorted, toolz.reduce))
    return (callable(f) and _nargs(f) and _nargs(f) > 1
            or f in do_curry)


_d = dict((name, curry(f) if _should_curry(f) else f)
          for name, f in toolz.__dict__.items()
          if '__' not in name)

_exceptions = dict((name, curry(f) if callable(f) else f)
                   for name, f in toolz.curried_exceptions.__dict__.items()
                   if '__' not in name)

locals().update(toolz.merge(_d, _exceptions))
