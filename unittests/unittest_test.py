# Copyright (c) 2016 CEF Python, see the Authors file.
# All rights reserved. Licensed under BSD 3-clause license.
# Project website: https://github.com/cztomczak/cefpython

"""Test the unittest itself.

NOTE: These tests require shared global state across test methods within
a class, so they are incompatible with pytest --forked mode which runs
each test method in a separate process.
"""

import unittest

try:
    import pytest
    requires_shared_state = pytest.mark.requires_shared_state
except ImportError:
    # Fallback for when pytest is not available
    def requires_shared_state(cls):
        return cls

# Globals
g_count = 0
g_setUpClass_count = 0
g_tearDownClass_count = 0
g_setUp_count = 0
g_tearDown_count = 0


@requires_shared_state
class Test(unittest.TestCase):
    count = 0

    @classmethod
    def setUpClass(cls):
        global g_setUpClass_count
        g_setUpClass_count += 1

    @classmethod
    def tearDownClass(cls):
        global g_tearDownClass_count
        g_tearDownClass_count += 1

    def setUp(self):
        global g_setUp_count
        g_setUp_count += 1

    def tearDown(self):
        global g_tearDown_count
        g_tearDown_count += 1

    def test_unittest1(self):
        global g_count
        g_count += 1
        self.count += 1
        self.assertEqual(g_count, 1)
        self.assertEqual(self.count, 1)
        self.assertEqual(g_setUpClass_count, 1)
        self.assertEqual(g_tearDownClass_count, 0)

    def test_unittest2(self):
        global g_count
        g_count += 1
        self.count += 1
        self.assertEqual(g_count, 2)
        self.assertEqual(self.count, 1)
        self.assertEqual(g_setUpClass_count, 1)
        self.assertEqual(g_tearDownClass_count, 0)

    def test_unittest3(self):
        self.assertEqual(g_setUp_count, 3)
        self.assertEqual(g_tearDown_count, 2)
        self.assertEqual(g_setUpClass_count, 1)
        self.assertEqual(g_tearDownClass_count, 0)


if __name__ == "__main__":
    unittest.main()
