# Copyright (c) 2016 CEF Python, see the Authors file.
# All rights reserved. Licensed under BSD 3-clause license.
# Project website: https://github.com/cztomczak/cefpython

"""
Test isolated test. Isolated tests are run each using a new instance
of Python interpreter. They also implement some unique features for
our use case. See main_test.py for some real tests.

This module demonstrates cross-platform process isolation:
- IsolatedTest1: Tests that share global state (run in same process)
- IsolatedTest2: Tests that need fresh state (run in isolated subprocess)

The isolation works on all platforms (Windows, Linux, macOS) using the
_process_isolation facade which uses fork() on Unix and subprocess on Windows.
"""

import unittest
# noinspection PyUnresolvedReferences
import _test_runner
from os.path import basename
from _process_isolation import IsolatedTestCase

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
    """Tests that share global state across methods (run in same process)."""

    def test_isolated1(self):
        global g_count
        g_count += 1
        self.assertEqual(g_count, 1)

    def test_isolated2(self):
        global g_count
        g_count += 1
        self.assertEqual(g_count, 2)


class IsolatedTest2(IsolatedTestCase):
    """Tests that need process isolation (run in isolated subprocess).

    Using IsolatedTestCase base class ensures each test runs in a fresh
    process with reset globals, working on all platforms including Windows.
    """

    def test_isolated3(self):
        global g_count
        g_count += 1
        self.assertEqual(g_count, 1)


if __name__ == "__main__":
    _test_runner.main(basename(__file__))
