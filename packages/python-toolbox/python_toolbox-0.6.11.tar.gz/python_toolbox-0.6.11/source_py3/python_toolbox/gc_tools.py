# Copyright 2009-2014 Ram Rachum.
# This program is distributed under the MIT license.

'''Defines various tools for working with garbage-collection.'''

import gc

from python_toolbox import sys_tools

def collect():
    if sys_tools.is_pypy:
        for _ in range(3):
            gc.collect()
    else:
        gc.collect()