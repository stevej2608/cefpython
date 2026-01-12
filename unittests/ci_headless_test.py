"""
CI-friendly headless test for CEFPython.

This test is designed to run in CI environments without a display server,
using off-screen rendering (OSR) mode.
"""

import sys
import os
import unittest

try:
    import cefpython3 as cef
except ImportError:
    print("ERROR: cefpython3 module not found. Install it first.")
    sys.exit(1)


class CIHeadlessTest(unittest.TestCase):
    """Test CEFPython initialization in headless/OSR mode for CI."""

    @classmethod
    def setUpClass(cls):
        """Set up exception hook for CEF."""
        sys.excepthook = cef.ExceptHook

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
        """Test that CEF can initialize in off-screen rendering mode."""
        # Configure CEF for headless operation
        settings = {
            "debug": False,
            "log_severity": cef.LOGSEVERITY_INFO,
            "log_file": "debug.log",
            "windowless_rendering_enabled": True,
        }

        # Initialize CEF
        try:
            cef.Initialize(settings)
            print("✓ CEF initialization successful")
        except Exception as e:
            self.fail(f"CEF initialization failed: {e}")

    def test_04_create_browser_osr(self):
        """Test creating a browser with off-screen rendering."""
        try:
            # Create browser with OSR
            parent_handle = 0
            window_info = cef.WindowInfo()
            window_info.SetAsOffscreen(parent_handle)

            # Create browser with a simple data URL
            browser = cef.CreateBrowserSync(
                window_info=window_info,
                url="data:text/html,<h1>CEFPython CI Test</h1><p>Headless mode</p>"
            )

            self.assertIsNotNone(browser, "Browser should be created")
            print("✓ Browser creation successful")

            # Verify browser URL
            url = browser.GetUrl()
            self.assertTrue(url.startswith("data:"), f"URL should be a data URL, got: {url}")
            print(f"✓ Browser URL: {url[:50]}...")

            # Get browser identifier
            browser_id = browser.GetIdentifier()
            self.assertIsInstance(browser_id, int, "Browser ID should be an integer")
            print(f"✓ Browser ID: {browser_id}")

        except Exception as e:
            self.fail(f"Browser creation failed: {e}")

    def test_05_cef_api_elements(self):
        """Test that key CEF API elements are accessible."""
        # Check for key classes
        required_classes = [
            'CefBrowser',
            'CefFrame',
            'WindowInfo',
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
