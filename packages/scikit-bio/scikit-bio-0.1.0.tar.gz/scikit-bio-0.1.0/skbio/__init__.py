#!/usr/bin/env python
from __future__ import print_function

# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

__credits__ = "https://github.com/biocore/scikit-bio/graphs/contributors"
__version__ = "0.1.0"

mottos = [
    # 03/15/2014
    "It's gonna get weird, bro.",
    # 05/14/2014
    "no cog yay"
]
motto = mottos[-1]

title = r"""
               _ _    _ _          _     _
              (_) |  (_) |        | |   (_)
      ___  ___ _| | ___| |_ ______| |__  _  ___
     / __|/ __| | |/ / | __|______| '_ \| |/ _ \
     \__ \ (__| |   <| | |_       | |_) | | (_) |
     |___/\___|_|_|\_\_|\__|      |_.__/|_|\___/

"""

art = r"""

           Opisthokonta
                   \  Amoebozoa
                    \ /
                     *    Euryarchaeota
                      \     |_ Crenarchaeota
                       \   *
                        \ /
                         *
                        /
                       /
                      /
                     *
                    / \
                   /   \
        Proteobacteria  \
                       Cyanobacteria
"""

if __doc__ is None:
    __doc__ = title + art
else:
    __doc__ = title + art + __doc__

from numpy.testing import Tester
test = Tester().test

if __name__ == '__main__':
    print(title)
    print(art)
