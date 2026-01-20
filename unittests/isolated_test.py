# Copyright (c) 2016 CEF Python, see the Authors file.
# All rights reserved. Licensed under BSD 3-clause license.
# Project website: https://github.com/cztomczak/cefpython

"""
Test isolated test. Isolated tests are run each using a new instance
of Python interpreter. They also implement some unique features for
our use case. See main_test.py for some real tests.

NOTE: These tests require shared global state across test methods within
a class, so they are incompatible with pytest --forked mode which runs
each test method in a separate process.
"""

import unittest
# noinspection PyUnresolvedReferences
import _test_runner
from os.path import basename

try:
    import pytest
    requires_shared_state = pytest.mark.requires_shared_state
except ImportError:
    # Fallback for when pytest is not available
    def requires_shared_state(cls):
        return cls

# Globals
g_count = 0


@requires_shared_state
class IsolatedTest1(unittest.TestCase):

    def test_isolated1(self):
        global g_count
        g_count += 1
        self.assertEqual(g_count, 1)

    def test_isolated2(self):
        global g_count
        g_count += 1
        self.assertEqual(g_count, 2)


class IsolatedTest2(unittest.TestCase):
    """This class runs in isolation (forked) to verify globals reset between classes."""

    def test_isolated3(self):
        global g_count
        g_count += 1
        self.assertEqual(g_count, 1)


if __name__ == "__main__":
    _test_runner.main(basename(__file__))
