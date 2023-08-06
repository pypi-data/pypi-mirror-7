# encoding: utf-8
# ---------------------------------------------------------------------------
#  Copyright (C) 2008-2014, IPython Development Team and Enthought, Inc.
#  Distributed under the terms of the BSD License.  See COPYING.rst.
# ---------------------------------------------------------------------------

"""
Estimate pi using a Monte Carlo method with distarray.
Usage:
    $ python pi_distarray.py <number of points>
"""

from __future__ import division

import sys

from util import timer

from distarray.dist import Context, Distribution, hypot
from distarray.dist.random import Random


context = Context()
random = Random(context)


def local_sum(mask):
    return mask.ndarray.sum()


@timer
def calc_pi(n):
    """Estimate pi using distributed NumPy arrays."""
    distribution = Distribution.from_shape(context=context, shape=(n,))
    x = random.rand(distribution)
    y = random.rand(distribution)
    r = hypot(x, y)
    mask = (r < 1)
    lsum = context.apply(local_sum, (mask.key,))
    return 4 * sum(lsum) / n


if __name__ == '__main__':
    N = int(sys.argv[1])
    result, time = calc_pi(N)
    print('time  : %3.4g\nresult: %.7f' % (time, result))
