# Copyright (c) 2024 CEF Python, see the Authors file.
# All rights reserved. Licensed under BSD 3-clause license.
# Project website: https://github.com/cztomczak/cefpython

"""
Pytest configuration and fixtures for CEF Python tests.

This module provides fixtures for tests that require a fully built
cefpython3 package with compiled Cython extensions.

Note: This module is designed for pytest but can also be imported by
unittest-based tests. When pytest is not available, pytest-specific
features will be disabled.
"""

import glob
import os
import sys
import platform

# pytest is optional - this module may be imported by unittest tests
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    pytest = None
    PYTEST_AVAILABLE = False


# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")


def get_python_tag():
    """Get the Python version tag for wheel naming (e.g., 'cp311')."""
    return f"cp{sys.version_info.major}{sys.version_info.minor}"


def get_platform_tag():
    """Get the platform tag for wheel naming."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "linux":
        if machine == "x86_64":
            return "linux_x86_64"
        return f"linux_{machine}"
    elif system == "windows":
        if machine in ("amd64", "x86_64"):
            return "win_amd64"
        return "win32"
    elif system == "darwin":
        return "macosx_*"
    return "*"


def find_wheel_for_current_python():
    """
    Find a wheel in dist/ that matches the current Python version.

    Returns:
        str: Path to the wheel file, or None if not found.
    """
    if not os.path.isdir(DIST_DIR):
        return None

    python_tag = get_python_tag()
    platform_tag = get_platform_tag()

    # Pattern: cefpython3-{version}-{python_tag}-{python_tag}-{platform}.whl
    pattern = os.path.join(DIST_DIR, f"cefpython3-*-{python_tag}-{python_tag}-*.whl")
    wheels = glob.glob(pattern)

    if wheels:
        # Return the most recent wheel
        return max(wheels, key=os.path.getmtime)

    # Try a more lenient pattern
    pattern = os.path.join(DIST_DIR, f"cefpython3-*-{python_tag}-*.whl")
    wheels = glob.glob(pattern)

    if wheels:
        return max(wheels, key=os.path.getmtime)

    return None


def is_cefpython_fully_installed():
    """
    Check if cefpython3 is fully installed with compiled extensions.

    Returns:
        tuple: (bool, str) - (is_installed, error_message)
    """
    try:
        from cefpython3 import cefpython as cef

        # Check for a function that only exists in the compiled module
        if not hasattr(cef, 'ExceptHook'):
            return False, (
                "cefpython3 is installed but missing compiled extensions. "
                "The 'ExceptHook' attribute is not available."
            )

        if not hasattr(cef, 'Initialize'):
            return False, (
                "cefpython3 is installed but missing compiled extensions. "
                "The 'Initialize' function is not available."
            )

        return True, None

    except ImportError as e:
        return False, f"cefpython3 is not installed: {e}"
    except Exception as e:
        return False, f"Error checking cefpython3 installation: {e}"


class CefPythonNotBuiltError(Exception):
    """Raised when cefpython3 wheel is not built."""
    pass


class CefPythonNotInstalledError(Exception):
    """Raised when cefpython3 is not properly installed."""
    pass


# Helper to check display availability
def has_display():
    """Check if a display is available for GUI tests."""
    system = platform.system().lower()

    if system == "linux":
        return os.environ.get("DISPLAY") is not None
    elif system == "darwin":
        # macOS always has a display in normal circumstances
        return True
    elif system == "windows":
        # Windows always has a display in normal circumstances
        return True

    return False


# Track if we're running in forked mode
FORKED_MODE = False


# Only define pytest fixtures if pytest is available
if PYTEST_AVAILABLE:
    @pytest.fixture(scope="session")
    def cefpython_wheel():
        """
        Fixture that provides the path to the built cefpython3 wheel.

        Raises:
            CefPythonNotBuiltError: If no wheel is found in dist/ for the current Python version.

        Returns:
            str: Path to the wheel file.
        """
        wheel_path = find_wheel_for_current_python()

        if wheel_path is None:
            python_tag = get_python_tag()
            raise CefPythonNotBuiltError(
                f"\n\nNo cefpython3 wheel found in {DIST_DIR}/ for Python {python_tag}.\n"
                f"Please build the package first:\n\n"
                f"    hatch run build:all\n\n"
                f"Or for the current Python version only:\n\n"
                f"    hatch run build-matrix.py{sys.version_info.major}.{sys.version_info.minor}:complete\n"
            )

        return wheel_path


    @pytest.fixture(scope="session")
    def require_cefpython():
        """
        Fixture that ensures cefpython3 is fully installed with compiled extensions.

        This fixture checks that:
        1. A wheel exists in dist/ for the current Python version
        2. cefpython3 is importable with all compiled components

        Raises:
            CefPythonNotBuiltError: If no wheel is found in dist/.
            CefPythonNotInstalledError: If cefpython3 is not properly installed.

        Returns:
            module: The cefpython module.
        """
        # First check if wheel exists
        wheel_path = find_wheel_for_current_python()

        if wheel_path is None:
            python_tag = get_python_tag()
            raise CefPythonNotBuiltError(
                f"\n\nNo cefpython3 wheel found in {DIST_DIR}/ for Python {python_tag}.\n"
                f"Please build the package first:\n\n"
                f"    hatch run build:all\n\n"
                f"Or for the current Python version only:\n\n"
                f"    hatch run build-matrix.py{sys.version_info.major}.{sys.version_info.minor}:complete\n"
            )

        # Check if properly installed
        is_installed, error_msg = is_cefpython_fully_installed()

        if not is_installed:
            raise CefPythonNotInstalledError(
                f"\n\n{error_msg}\n\n"
                f"A wheel was found at: {wheel_path}\n"
                f"Please install it:\n\n"
                f"    pip install {wheel_path}\n\n"
                f"Or reinstall the package:\n\n"
                f"    pip install --force-reinstall {wheel_path}\n"
            )

        from cefpython3 import cefpython as cef
        return cef


    @pytest.fixture(scope="session")
    def cef(require_cefpython):
        """
        Convenience fixture that provides the cefpython module.

        This is an alias for require_cefpython for cleaner test code.
        """
        return require_cefpython


    # Pytest markers and configuration
    def pytest_configure(config):
        """Register custom markers and detect forked mode."""
        global FORKED_MODE

        # Detect if --forked is being used
        if hasattr(config.option, 'forked') and config.option.forked:
            FORKED_MODE = True

        config.addinivalue_line(
            "markers",
            "requires_cefpython: mark test as requiring a fully built cefpython3 package"
        )
        config.addinivalue_line(
            "markers",
            "requires_display: mark test as requiring a display/GUI environment"
        )
        config.addinivalue_line(
            "markers",
            "requires_shared_state: mark test as requiring shared state across test methods (incompatible with --forked)"
        )


    @pytest.fixture
    def skip_if_no_cefpython():
        """
        Fixture that skips the test if cefpython3 is not fully installed.

        Use this for tests that should be skipped rather than fail when
        cefpython3 is not available.
        """
        is_installed, error_msg = is_cefpython_fully_installed()

        if not is_installed:
            pytest.skip(f"cefpython3 not fully installed: {error_msg}")


    @pytest.fixture
    def skip_if_no_wheel():
        """
        Fixture that skips the test if no wheel is found in dist/.
        """
        wheel_path = find_wheel_for_current_python()

        if wheel_path is None:
            python_tag = get_python_tag()
            pytest.skip(f"No cefpython3 wheel found in dist/ for {python_tag}")

        return wheel_path


    @pytest.fixture
    def skip_if_no_display():
        """Fixture that skips the test if no display is available."""
        if not has_display():
            pytest.skip("No display available for GUI tests")


    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(config, items):
        """Group tests that require shared state to run together without forking.

        Uses trylast=True to run after pytest-randomly has shuffled the tests,
        so we can restore the correct order for shared-state tests.
        """
        # Separate shared state tests from other tests
        shared_state_items = []
        other_items = []
        for item in items:
            if "requires_shared_state" in item.keywords:
                shared_state_items.append(item)
            else:
                other_items.append(item)

        if not shared_state_items:
            return

        # Sort shared_state tests by class and then by test name to ensure
        # deterministic execution order (tests within a class must run in order)
        def sort_key(item):
            # Sort by: module path, class name, test name
            cls_name = item.cls.__name__ if item.cls else ""
            return (item.fspath, cls_name, item.name)

        shared_state_items.sort(key=sort_key)

        # Put shared state tests at the end, grouped and sorted
        items[:] = other_items + shared_state_items


    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_protocol(item, nextitem):
        """
        Run tests marked with requires_shared_state without forking.

        When --forked is enabled, pytest-forked wraps each test in a subprocess.
        For tests that need shared state across methods, we bypass forking by
        running them directly using the standard protocol.

        Uses tryfirst=True to ensure this runs before pytest-forked's hook.
        """
        if not FORKED_MODE:
            return None  # Let pytest handle normally

        if "requires_shared_state" not in item.keywords:
            return None  # Let pytest-forked handle this test

        # Run this test without forking by using the standard protocol
        from _pytest.runner import runtestprotocol
        runtestprotocol(item, nextitem=nextitem)
        return True  # We handled it, don't let other hooks run


def require_built_cefpython():
    """
    Helper function for module-level skip/error when cefpython is not available.

    Use at the top of test modules that require the built cefpython3 package:

        from conftest import require_built_cefpython
        cef = require_built_cefpython()

    This will:
    - Skip the entire module if no wheel is found in dist/ (pytest)
    - Raise an error if cefpython3 is not properly installed (unittest)
    - Return the cefpython module if available

    Raises:
        pytest.skip: If cefpython3 is not available and pytest is available
        CefPythonNotBuiltError: If wheel not found and pytest unavailable
        CefPythonNotInstalledError: If cefpython3 not installed and pytest unavailable

    Returns:
        module: The cefpython module
    """
    # Check for wheel in dist/
    wheel_path = find_wheel_for_current_python()

    if wheel_path is None:
        python_tag = get_python_tag()
        msg = (
            f"No cefpython3 wheel found for Python {python_tag}. "
            f"Run: hatch run build:all"
        )
        if PYTEST_AVAILABLE:
            pytest.skip(msg, allow_module_level=True)
        else:
            raise CefPythonNotBuiltError(msg)

    # Check if properly installed
    is_installed, error_msg = is_cefpython_fully_installed()

    if not is_installed:
        msg = (
            f"{error_msg}\n"
            f"Wheel found at: {wheel_path}\n"
            f"Install with: pip install {wheel_path}"
        )
        if PYTEST_AVAILABLE:
            pytest.skip(msg, allow_module_level=True)
        else:
            raise CefPythonNotInstalledError(msg)

    from cefpython3 import cefpython as cef
    return cef
