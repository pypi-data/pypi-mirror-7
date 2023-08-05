#!/usr/bin/python
"""Functions for design of experiments (DOE)

These can be passed to the *design* argument of 
:meth:`~modelicares.exps.gen_experiments`.
"""

from itertools import product


def fullfact(*space):
    """Full-factorial DOE

    **Example:**

    .. code-block:: python

       >>> from modelicares import *

       >>> settings = doe.fullfact([0, 1], [0, 1], [0, 1, 2])
       >>> for s in settings:
       ...     print(s)
       (0, 0, 0)
       (0, 0, 1)
       (0, 0, 2)
       (0, 1, 0)
       (0, 1, 1)
       (0, 1, 2)
       (1, 0, 0)
       (1, 0, 1)
       (1, 0, 2)
       (1, 1, 0)
       (1, 1, 1)
       (1, 1, 2)
    """
    return product(*space)

def aslisted(*space):
    """Step through all the entries together (jointly or element-wise).

    The set of experiments will terminate at end of the shortest list.

    **Example:**

    .. code-block:: python

       >>> from modelicares import *

       >>> settings = doe.aslisted([0, 1], [0, 1], [0, 1, 2])
       >>> for s in settings:
       ...     print(s)
       (0, 0, 0)
       (1, 1, 1)
    """
    return zip(*space)

def ofat(*space):
    """One-factor-at-a-time or OFAT method

    The first entry in each sublist is taken as the baseline value for that
    dimension.

    **Example:**

    .. code-block:: python

       >>> from modelicares import *

       >>> settings = doe.ofat([0, 1], [0, 1], [0, 1, 2])
       >>> for s in settings:
       ...     print(s)
       (0, 0, 0)
       (1, 0, 0)
       (0, 1, 0)
       (0, 0, 1)
       (0, 0, 2)
    """
    baseline = [dimension[0] for dimension in space]
    yield tuple(baseline)
    for i, dimension in enumerate(space):
        for level in dimension[1:]:
            if i == 0:
                yield tuple([level] + baseline[i+1:])
            elif i == len(space) - 1:
                yield tuple(baseline[:i] + [level])
            else:
                yield tuple(baseline[:i] + [level] + baseline[i+1:])

if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
    exit()
