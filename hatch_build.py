"""
Custom Hatch build hook for CEF Python.

This build hook manages the complete build process including:
1. Building C++ libraries (client_handler, libcefpythonapp, subprocess, cpp_utils)
2. Compiling Cython extensions
3. Creating the installer package structure
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Any, Dict

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CefPythonBuildHook(BuildHookInterface):
    """Custom build hook for CEF Python."""

    PLUGIN_NAME = "custom"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.build_dir = Path(self.root) / "build"
        self.src_dir = Path(self.root) / "src"
        self.version = "123.0"

    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        """Initialize the build process."""
        # Only run full build for wheel targets, not for editable installs
        if self.target_name != "wheel":
            return

        self.app.display_info("Starting CEF Python build process...")
        self._build_native_libraries()
        self._build_cython_extension()
        self._create_installer_package()

    def _build_native_libraries(self) -> None:
        """Build all C++ libraries."""
        self.app.display_info("Building C++ libraries...")

        # Set up environment variables
        env = os.environ.copy()
        env.update({
            "CEF_CCFLAGS": "-std=gnu++17 -DNDEBUG -Wall -Werror -Wno-deprecated-declarations -O3",
            "PYTHON_INCLUDE": self._get_python_include(),
            "CEF_BIN": str(self.build_dir / "cef123_123.0.7+g6a21509+chromium-123.0.6312.46_linux64/bin"),
            "CEF_LIB": str(self.build_dir / "cef123_123.0.7+g6a21509+chromium-123.0.6312.46_linux64/lib"),
        })

        # Build each C++ project
        projects = [
            ("client_handler", "src/client_handler", "Makefile"),
            ("libcefpythonapp", "src/subprocess", "Makefile-libcefpythonapp"),
            ("subprocess", "src/subprocess", "Makefile"),
            ("cpp_utils", "src/cpp_utils", "Makefile"),
        ]

        for name, directory, makefile in projects:
            self.app.display_info(f"Building {name}...")
            project_dir = Path(self.root) / directory

            cmd = ["make", "-C", str(project_dir)]
            if makefile != "Makefile":
                cmd.extend(["-f", makefile])

            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                self.app.display_error(f"Failed to build {name}")
                self.app.display_error(result.stderr)
                raise RuntimeError(f"C++ build failed for {name}")

        self.app.display_success("C++ libraries built successfully")

    def _build_cython_extension(self) -> None:
        """Build the Cython extension module."""
        self.app.display_info("Building Cython extension...")

        # Run the build script
        result = subprocess.run(
            [sys.executable, "tools/build.py", self.version, "--fast"],
            cwd=str(self.root),
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            self.app.display_error("Failed to build Cython extension")
            self.app.display_error(result.stderr)
            raise RuntimeError("Cython build failed")

        self.app.display_success("Cython extension built successfully")

    def _create_installer_package(self) -> None:
        """Create the installer package structure."""
        self.app.display_info("Creating installer package...")

        result = subprocess.run(
            [sys.executable, "tools/make_installer.py", self.version],
            cwd=str(self.root),
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            self.app.display_error("Failed to create installer package")
            self.app.display_error(result.stderr)
            raise RuntimeError("Installer creation failed")

        self.app.display_success("Installer package created successfully")

    def _get_python_include(self) -> str:
        """Get the Python include directory."""
        import sysconfig
        return sysconfig.get_path("include")

    def clean(self, versions: list[str]) -> None:
        """Clean build artifacts."""
        self.app.display_info("Cleaning build artifacts...")

        patterns = [
            "build/build_cefpython",
            "build/temp.*",
            "build/lib.*",
            "dist",
            "*.egg-info",
            "src/**/__pycache__",
            "src/**/*.pyc",
            "src/**/*.pyo",
            "src/**/*.so",
            "src/**/*.o",
            "src/**/*.a",
        ]

        for pattern in patterns:
            for path in Path(self.root).glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)

        self.app.display_success("Build artifacts cleaned")
