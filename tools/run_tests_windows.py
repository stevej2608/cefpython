#!/usr/bin/env python
"""
Windows test runner for CEF Python.

On Windows, pytest-forked doesn't work (no os.fork()), and CEF can only be
initialized once per process. This script runs each CEF test file in a
separate subprocess to ensure proper isolation.

Usage:
    hatch test -- --run-windows-isolated

Or directly (uses hatch internally):
    python tools/run_tests_windows.py
    python tools/run_tests_windows.py -v  # verbose
"""

import subprocess
import sys
import os
import shutil

# Test files that use CEF and need process isolation
CEF_TEST_FILES = [
    "unittests/_ci_headless_test.py",
    "unittests/main_test.py",
    "unittests/osr_test.py",
]

# Test files that don't use CEF (can run together)
NON_CEF_TEST_FILES = [
    "unittests/unittest_test.py",
]

# Test files that require forked mode (skip on Windows)
FORKED_ONLY_TEST_FILES = [
    "unittests/isolated_test.py",
]


def find_hatch():
    """Find hatch executable."""
    return shutil.which("hatch")


def run_tests(verbose=False):
    """Run all tests with proper isolation."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    hatch = find_hatch()
    if not hatch:
        print("ERROR: hatch not found. Please install hatch: pip install hatch")
        return 1

    failed = []
    passed = []
    skipped = []

    print("=" * 70)
    print("CEF Python Windows Test Runner")
    print("=" * 70)
    print()

    # Run non-CEF tests together
    print("Running non-CEF tests...")
    for test_file in NON_CEF_TEST_FILES:
        print(f"  {test_file}")

    cmd = [hatch, "test", "--"] + NON_CEF_TEST_FILES
    if verbose:
        cmd.append("-v")

    result = subprocess.run(cmd, cwd=project_root)
    if result.returncode == 0:
        passed.extend(NON_CEF_TEST_FILES)
    else:
        failed.extend(NON_CEF_TEST_FILES)

    print()

    # Run each CEF test file in a separate process
    print("Running CEF tests (each in separate process)...")
    for test_file in CEF_TEST_FILES:
        print(f"\n  {test_file}...")
        cmd = [hatch, "test", "--", test_file]
        if verbose:
            cmd.append("-v")

        result = subprocess.run(cmd, cwd=project_root)
        if result.returncode == 0:
            passed.append(test_file)
            print(f"    PASSED")
        else:
            failed.append(test_file)
            print(f"    FAILED")

    # Note skipped tests
    print()
    print("Skipped tests (require os.fork(), not available on Windows):")
    for test_file in FORKED_ONLY_TEST_FILES:
        print(f"  {test_file}")
        skipped.append(test_file)

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Passed:  {len(passed)}")
    print(f"Failed:  {len(failed)}")
    print(f"Skipped: {len(skipped)}")

    if failed:
        print()
        print("Failed tests:")
        for f in failed:
            print(f"  - {f}")
        return 1

    print()
    print("All tests passed!")
    return 0


if __name__ == "__main__":
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    sys.exit(run_tests(verbose))
