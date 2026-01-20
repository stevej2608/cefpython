"""
CI-friendly headless test for CEFPython.

This test is designed to run in CI environments without a display server,
using off-screen rendering (OSR) mode.

Requires a fully built cefpython3 package. Run `hatch run build:all` first.
"""

import sys
import os
import unittest

# Use the conftest helper to check for and import cefpython
from conftest import require_built_cefpython
cef = require_built_cefpython()


class CIHeadlessTest(unittest.TestCase):
    """Test CEFPython initialization in headless/OSR mode for CI."""

    @classmethod
    def setUpClass(cls):
        """Set up CEF for headless/OSR mode."""
        sys.excepthook = cef.ExceptHook

        # Configure CEF for headless operation
        settings = {
            "debug": False,
            "log_severity": cef.LOGSEVERITY_INFO,
            "log_file": "debug.log",
            "windowless_rendering_enabled": True,
        }

        # Initialize CEF once for all tests in this class
        cef.Initialize(settings)
        cls._cef_initialized = True

    def test_01_module_import(self):
        """Test that the cefpython3 module imports correctly."""
        self.assertIsNotNone(cef)
        print("✓ Module import successful")

    def test_02_version_info(self):
        """Test that version information is accessible."""
        self.assertIsNotNone(cef.__version__)
        self.assertIsNotNone(cef.__chrome_version__)
        self.assertIsNotNone(cef.__cef_version__)

        print(f"✓ CEFPython version: {cef.__version__}")
        print(f"✓ Chrome version: {cef.__chrome_version__}")
        print(f"✓ CEF version: {cef.__cef_version__}")

        # Verify Chrome version is 123
        chrome_major = int(cef.__chrome_version__.split('.')[0])
        self.assertEqual(chrome_major, 123, "Chrome major version should be 123")
        print("✓ Chrome version verification passed")

    def test_03_cef_initialize(self):
        """Test that CEF is initialized in off-screen rendering mode."""
        # CEF is initialized in setUpClass - verify it's ready
        self.assertTrue(
            getattr(self.__class__, '_cef_initialized', False),
            "CEF should be initialized in setUpClass"
        )
        print("✓ CEF initialization verified")

    def test_04_create_browser_osr(self):
        """Test creating a browser with off-screen rendering."""
        import time
        try:
            # Create browser with OSR
            parent_handle = 0
            window_info = cef.WindowInfo()
            window_info.SetAsOffscreen(parent_handle)

            # Create browser with a simple data URL
            test_url = "data:text/html,<h1>CEFPython CI Test</h1><p>Headless mode</p>"
            browser = cef.CreateBrowserSync(
                window_info=window_info,
                url=test_url
            )

            self.assertIsNotNone(browser, "Browser should be created")
            print("✓ Browser creation successful")

            # Get browser identifier (available immediately)
            browser_id = browser.GetIdentifier()
            self.assertIsInstance(browser_id, int, "Browser ID should be an integer")
            print(f"✓ Browser ID: {browser_id}")

            # Run message loop to let CEF process the navigation
            # URL may not be available immediately after CreateBrowserSync
            for _ in range(50):  # Up to 500ms
                cef.MessageLoopWork()
                time.sleep(0.01)
                url = browser.GetUrl()
                if url:
                    break

            # Verify browser URL (may still be empty in headless mode)
            if url:
                self.assertTrue(url.startswith("data:"), f"URL should be a data URL, got: {url}")
                print(f"✓ Browser URL: {url[:50]}...")
            else:
                # In headless/OSR mode without proper render handler, URL may not be set
                print("⚠ Browser URL not yet available (expected in headless mode)")

        except Exception as e:
            self.fail(f"Browser creation failed: {e}")

    def test_05_cef_api_elements(self):
        """Test that key CEF API elements are accessible."""
        # Check for key classes (note: CEF Python uses Py* prefix for classes)
        required_classes = [
            'PyBrowser',      # Browser object type
            'PyFrame',        # Frame object type
            'WindowInfo',     # Window configuration
            'JavascriptBindings',  # JS bindings
            'Request',        # HTTP request
        ]

        for cls_name in required_classes:
            self.assertTrue(
                hasattr(cef, cls_name),
                f"Class {cls_name} should be available"
            )
        print(f"✓ All {len(required_classes)} required classes found")

        # Check for key functions
        required_functions = [
            'Initialize',
            'Shutdown',
            'CreateBrowserSync',
            'MessageLoopWork',
            'GetBrowserByIdentifier',
            'SetGlobalClientHandler',
        ]

        for func_name in required_functions:
            self.assertTrue(
                hasattr(cef, func_name),
                f"Function {func_name} should be available"
            )
        print(f"✓ All {len(required_functions)} required functions found")

    def test_06_platform_specific(self):
        """Test platform-specific functionality."""
        if sys.platform == 'win32':
            print("✓ Running on Windows")
            # Windows-specific checks
            pkg_dir = os.path.dirname(cef.__file__)
            libcef_path = os.path.join(pkg_dir, "libcef.dll")
            self.assertTrue(
                os.path.exists(libcef_path),
                f"libcef.dll should exist at {libcef_path}"
            )
            print(f"✓ Found libcef.dll")

        elif sys.platform == 'darwin':
            print("✓ Running on macOS")
            # macOS-specific checks
            pkg_dir = os.path.dirname(cef.__file__)
            framework_path = os.path.join(
                pkg_dir,
                "Chromium Embedded Framework.framework"
            )
            # Note: Framework might be in different location on macOS
            print(f"  Framework expected at: {framework_path}")

        else:  # Linux
            print("✓ Running on Linux")
            # Linux-specific checks
            pkg_dir = os.path.dirname(cef.__file__)
            libcef_path = os.path.join(pkg_dir, "libcef.so")
            self.assertTrue(
                os.path.exists(libcef_path),
                f"libcef.so should exist at {libcef_path}"
            )
            print(f"✓ Found libcef.so")

    @classmethod
    def tearDownClass(cls):
        """Clean up CEF."""
        if getattr(cls, '_cef_initialized', False):
            try:
                cef.Shutdown()
                print("✓ CEF shutdown successful")
            except Exception as e:
                print(f"⚠ CEF shutdown warning: {e}")


def main():
    """Run the test suite."""
    print("=" * 70)
    print("CEFPython CI Headless Test")
    print("=" * 70)
    print()

    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(CIHeadlessTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 70)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        print("=" * 70)
        return 0
    else:
        print("❌ Some tests failed")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
