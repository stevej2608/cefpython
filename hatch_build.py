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

# Import platform detection from tools/common.py
sys.path.insert(0, str(Path(__file__).parent / "tools"))
from common import (
    WINDOWS, MAC, LINUX,
    OS_POSTFIX2, CEF_POSTFIX2,
    get_cefpython_version,
    MODULE_EXT
)


class CefPythonBuildHook(BuildHookInterface):
    """Custom build hook for CEF Python."""

    PLUGIN_NAME = "custom"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.build_dir = Path(self.root) / "build"
        self.src_dir = Path(self.root) / "src"
        self.version = self.metadata.version

    def _detect_cef_directory(self) -> Path:
        """Detect CEF binaries directory dynamically based on platform."""
        version_info = get_cefpython_version()
        cef_version = version_info["CEF_VERSION"]
        chrome_major = version_info["CHROME_VERSION_MAJOR"]

        # Pattern: cef123_123.0.7+g6a21509+chromium-123.0.6312.46_{platform}
        # Note: Uses OS_POSTFIX2 (win64) not CEF_POSTFIX2 (windows64)
        basename = f"cef{chrome_major}_{cef_version}_{OS_POSTFIX2}"
        cef_dir = self.build_dir / basename

        if not cef_dir.exists():
            # Try glob pattern for any CEF directory matching major version
            pattern = f"cef{chrome_major}_*_{OS_POSTFIX2}"
            matches = list(self.build_dir.glob(pattern))
            if matches:
                cef_dir = matches[0]
            else:
                raise RuntimeError(
                    f"CEF binaries not found. Expected: {cef_dir}\n"
                    f"Run: hatch run build:setup-cef"
                )

        return cef_dir

    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        """Initialize the build process."""
        # Only run full build for wheel targets, not for editable installs
        if self.target_name != "wheel":
            return

        # Check if installer package already exists
        installer_dir = Path(f"build/cefpython3_{self.version}_{OS_POSTFIX2}")
        if installer_dir.exists():
            self.app.display_info(f"Installer package already exists at {installer_dir}")
            self.app.display_info("Skipping build steps, using existing package")
        else:
            self.app.display_info("Starting CEF Python build process...")
            self._build_native_libraries()
            self._build_cython_extension()
            self._create_installer_package()

        # Configure platform-specific wheel paths
        self._configure_wheel_paths(build_data)

    def _build_native_libraries(self) -> None:
        """Build all C++ libraries using platform-specific methods."""
        self.app.display_info("Building C++ libraries...")

        cef_dir = self._detect_cef_directory()

        if WINDOWS:
            self._build_cpp_windows(cef_dir)
        elif MAC or LINUX:
            self._build_cpp_unix(cef_dir)
        else:
            raise RuntimeError(f"Unsupported platform: {OS_POSTFIX2}")

        self.app.display_success("C++ libraries built successfully")

    def _build_cpp_unix(self, cef_dir: Path) -> None:
        """Build C++ projects using makefiles (Linux/Mac)."""
        env = os.environ.copy()
        env.update({
            "CEF_CCFLAGS": self._get_cef_ccflags(),
            "PYTHON_INCLUDE": self._get_python_include(),
            "CEF_BIN": str(cef_dir / "bin"),
            "CEF_LIB": str(cef_dir / "lib"),
        })

        # Add Mac-specific environment variables
        if MAC:
            env["CC"] = "c++"
            env["CXX"] = "c++"
            env["ARCHFLAGS"] = "-arch x86_64"
            env["PATH"] = "/usr/local/bin:" + env.get("PATH", "")

        projects = [
            ("client_handler", "src/client_handler", "Makefile"),
            ("libcefpythonapp", "src/subprocess", "Makefile-libcefpythonapp"),
            ("subprocess", "src/subprocess", "Makefile"),
            ("cpp_utils", "src/cpp_utils", "Makefile"),
        ]

        for name, directory, makefile in projects:
            self._run_make(name, directory, makefile, env)

    def _build_cpp_windows(self, cef_dir: Path) -> None:
        """Build C++ projects using setuptools (Windows)."""
        self.app.display_info("Building C++ projects with setuptools...")

        env = os.environ.copy()
        env["CEF_BINARIES_LIBRARIES"] = str(cef_dir)

        result = subprocess.run(
            [sys.executable, "tools/build_cpp_projects.py"],
            cwd=str(self.root),
            env=env,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            self.app.display_error("Failed to build C++ projects")
            self.app.display_error(result.stderr)
            raise RuntimeError("C++ build failed on Windows")

    def _get_cef_ccflags(self) -> str:
        """Get CEF compiler flags for current platform."""
        flags = "-std=gnu++17 -DNDEBUG -Wall -Werror"

        if LINUX:
            flags += " -Wno-deprecated-declarations -O3"
        elif MAC:
            flags += (" -O3 -arch x86_64 -Wno-return-type-c-linkage"
                     " -stdlib=libc++ -fno-strict-aliasing -fno-rtti"
                     " -fno-threadsafe-statics -fobjc-call-cxx-cdtors"
                     " -fvisibility=hidden -fvisibility-inlines-hidden")

        return flags

    def _run_make(self, name: str, directory: str, makefile: str, env: dict) -> None:
        """Run make command for a C++ project."""
        self.app.display_info(f"Building {name}...")
        project_dir = Path(self.root) / directory

        cmd = ["make", "-C", str(project_dir)]
        if makefile != "Makefile":
            cmd.extend(["-f", makefile])

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            self.app.display_error(f"Failed to build {name}")
            self.app.display_error(result.stderr)
            raise RuntimeError(f"C++ build failed for {name}")

    def _build_cython_extension(self) -> None:
        """Build the Cython extension module."""
        self.app.display_info("Building Cython extension...")

        # Run the build script (without tests)
        result = subprocess.run(
            [sys.executable, "tools/build_libs_only.py", self.version, "--fast"],
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

    def _configure_wheel_paths(self, build_data: Dict[str, Any]) -> None:
        """Configure platform-specific paths for wheel building."""
        # Determine the installer package directory based on platform
        installer_dir = f"build/cefpython3_{self.version}_{OS_POSTFIX2}"

        self.app.display_info(f"Configuring wheel paths for {OS_POSTFIX2}...")
        self.app.display_info(f"Package directory: {installer_dir}")

        # Set the force_include paths for the wheel
        if "force_include" not in build_data:
            build_data["force_include"] = {}

        build_data["force_include"][f"{installer_dir}/cefpython3"] = "cefpython3"
        build_data["force_include"][f"{installer_dir}/examples"] = "cefpython3/examples"

        self.app.display_success("Wheel paths configured successfully")

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
        ]

        # Platform-specific binary extensions
        if WINDOWS:
            patterns.extend([
                "src/**/*.pyd",
                "src/**/*.dll",
                "src/**/*.obj",
                "src/**/*.lib",
                "src/**/*.exp",
            ])
        else:
            patterns.extend([
                "src/**/*.so",
                "src/**/*.o",
                "src/**/*.a",
            ])

        if MAC:
            patterns.append("src/**/*.dylib")

        for pattern in patterns:
            for path in Path(self.root).glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)

        self.app.display_success("Build artifacts cleaned")
