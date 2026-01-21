# Copyright (c) 2024 CEF Python, see the Authors file.
# All rights reserved. Licensed under BSD 3-clause license.
# Project website: https://github.com/cztomczak/cefpython

"""
Cross-platform process isolation facade.

This module provides a platform-independent way to run code in an isolated
process. On Unix, it uses fork() when available for efficiency. On Windows
(and as a fallback), it uses subprocess with a fresh Python interpreter.

This is useful for:
- CEF tests (CEF can only be initialized once per process)
- Tests that need fresh global state
- Porting fork()-based code to Windows

Usage:
    from _process_isolation import run_isolated, IsolatedTestCase

    # Run a function in an isolated process
    result = run_isolated(my_function, arg1, arg2)

    # Or use the test case base class
    class MyTest(IsolatedTestCase):
        def test_something(self):
            # This runs in an isolated process
            pass
"""

import os
import sys
import platform
import subprocess
import unittest
import pickle
import tempfile
from typing import Any, Callable, Optional, Tuple


def _can_use_fork():
    """Check if os.fork() is available."""
    return hasattr(os, 'fork') and platform.system() != 'Windows'


def run_isolated(func: Callable, *args, **kwargs) -> Tuple[bool, Any]:
    """
    Run a function in an isolated process.

    Args:
        func: The function to run
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Tuple of (success: bool, result: Any)
        On success, result is the function's return value.
        On failure, result is the exception message.
    """
    if _can_use_fork():
        return _run_isolated_fork(func, *args, **kwargs)
    else:
        return _run_isolated_subprocess(func, *args, **kwargs)


def _run_isolated_fork(func: Callable, *args, **kwargs) -> Tuple[bool, Any]:
    """Run function in a forked process (Unix only)."""
    # Create a pipe for communication
    read_fd, write_fd = os.pipe()

    pid = os.fork()
    if pid == 0:
        # Child process
        os.close(read_fd)
        try:
            result = func(*args, **kwargs)
            # Send success result
            with os.fdopen(write_fd, 'wb') as f:
                pickle.dump((True, result), f)
            os._exit(0)
        except Exception as e:
            # Send error
            with os.fdopen(write_fd, 'wb') as f:
                pickle.dump((False, str(e)), f)
            os._exit(1)
    else:
        # Parent process
        os.close(write_fd)
        with os.fdopen(read_fd, 'rb') as f:
            try:
                result = pickle.load(f)
            except Exception:
                result = (False, "Failed to read result from child process")
        os.waitpid(pid, 0)
        return result


def _run_isolated_subprocess(func: Callable, *args, **kwargs) -> Tuple[bool, Any]:
    """Run function in a subprocess (cross-platform)."""
    # Serialize the function call to a temp file
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pkl', delete=False) as f:
        temp_path = f.name
        pickle.dump((func, args, kwargs), f)

    result_path = temp_path + '.result'

    try:
        # Run the helper script
        code = f'''
import pickle
import sys
with open({repr(temp_path)}, 'rb') as f:
    func, args, kwargs = pickle.load(f)
try:
    result = func(*args, **kwargs)
    with open({repr(result_path)}, 'wb') as f:
        pickle.dump((True, result), f)
except Exception as e:
    with open({repr(result_path)}, 'wb') as f:
        pickle.dump((False, str(e)), f)
    sys.exit(1)
'''
        proc = subprocess.run(
            [sys.executable, '-c', code],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True
        )

        # Read result
        if os.path.exists(result_path):
            with open(result_path, 'rb') as f:
                return pickle.load(f)
        else:
            stderr = proc.stderr.decode('utf-8', errors='replace')
            return (False, f"Subprocess failed: {stderr}")
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if os.path.exists(result_path):
            os.unlink(result_path)


def run_test_isolated(test_class: type, test_method: str) -> Tuple[bool, str]:
    """
    Run a specific test method from a test class in an isolated process.

    Args:
        test_class: The unittest.TestCase subclass
        test_method: Name of the test method to run

    Returns:
        Tuple of (success: bool, output: str)
    """
    # Get the module and class names for the subprocess
    module_name = test_class.__module__
    class_name = test_class.__name__

    # Build the test ID
    test_id = f"{module_name}.{class_name}.{test_method}"

    # Run pytest on just this test
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', '-xvs', test_id],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        env={**os.environ, '_CEF_SUBPROCESS_TEST': '1'}
    )

    output = result.stdout.decode('utf-8', errors='replace')
    if result.stderr:
        output += '\n' + result.stderr.decode('utf-8', errors='replace')

    return (result.returncode == 0, output)


class IsolatedTestCase(unittest.TestCase):
    """
    A TestCase that runs each test method in an isolated process.

    This provides the same isolation as pytest-forked but works on Windows.

    Usage:
        class MyTest(IsolatedTestCase):
            def test_something(self):
                # This runs in a fresh process
                pass
    """

    _isolation_enabled = True

    @classmethod
    def setUpClass(cls):
        """Check if we're in the isolated subprocess."""
        # If we're in the subprocess, disable further isolation
        if os.environ.get('_ISOLATED_TEST_SUBPROCESS') == '1':
            cls._isolation_enabled = False

    def run(self, result=None):
        """Override run to execute in isolated process if needed."""
        if not self._isolation_enabled:
            # We're in the subprocess, run normally
            return super().run(result)

        # Run this test in an isolated subprocess
        test_method = self._testMethodName
        success, output = self._run_in_subprocess(test_method)

        # Report result
        if result is not None:
            if success:
                result.addSuccess(self)
            else:
                result.addFailure(self, (AssertionError, AssertionError(output), None))

        return result

    def _run_in_subprocess(self, test_method: str) -> Tuple[bool, str]:
        """Run a test method in an isolated subprocess."""
        # Get the file path for this test class
        import inspect
        module = inspect.getmodule(self.__class__)
        if module and hasattr(module, '__file__'):
            file_path = module.__file__
        else:
            file_path = f"{self.__class__.__module__.replace('.', '/')}.py"

        class_name = self.__class__.__name__
        # pytest test ID format: file_path::ClassName::method_name
        test_id = f"{file_path}::{class_name}::{test_method}"

        env = os.environ.copy()
        env['_ISOLATED_TEST_SUBPROCESS'] = '1'
        env['_CEF_SUBPROCESS_TEST'] = '1'

        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '-xvs', test_id],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            env=env
        )

        output = result.stdout.decode('utf-8', errors='replace')
        return (result.returncode == 0, output)
