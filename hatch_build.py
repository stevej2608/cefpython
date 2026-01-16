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
import platform
import sysconfig
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

    def _print_tooling_report(self) -> None:
        """Print comprehensive tooling version report for build environment comparison."""
        self.app.display_info("=" * 70)
        self.app.display_info("BUILD ENVIRONMENT TOOLING REPORT")
        self.app.display_info("=" * 70)

        # System information
        self.app.display_info("")
        self.app.display_info("--- System Information ---")
        self.app.display_info(f"Platform: {platform.system()} {platform.release()}")
        self.app.display_info(f"Platform version: {platform.version()}")
        self.app.display_info(f"Machine: {platform.machine()}")
        self.app.display_info(f"Processor: {platform.processor()}")

        # Python information
        self.app.display_info("")
        self.app.display_info("--- Python Information ---")
        self.app.display_info(f"Python version: {sys.version}")
        self.app.display_info(f"Python executable: {sys.executable}")
        self.app.display_info(f"Python architecture: {platform.architecture()[0]}")
        self.app.display_info(f"Python include path: {sysconfig.get_path('include')}")
        self.app.display_info(f"Python library path: {sysconfig.get_config_var('LIBDIR')}")

        # Cython version
        self.app.display_info("")
        self.app.display_info("--- Cython ---")
        try:
            import Cython
            self.app.display_info(f"Cython version: {Cython.__version__}")
        except ImportError:
            self.app.display_info("Cython: NOT INSTALLED")

        # Platform-specific compiler information
        self.app.display_info("")
        if WINDOWS:
            self._print_windows_tooling()
        elif LINUX:
            self._print_linux_tooling()
        elif MAC:
            self._print_macos_tooling()

        # Common tools (CMake, Ninja)
        self.app.display_info("")
        self.app.display_info("--- Build Tools ---")
        self._print_tool_version("cmake", "--version")
        self._print_tool_version("ninja", "--version")
        self._print_tool_version("make", "--version")
        self._print_tool_version("git", "--version")

        # Key environment variables
        self.app.display_info("")
        self.app.display_info("--- Key Environment Variables ---")
        env_vars = [
            "PATH", "CEF_BINARIES_LIBRARIES",
            # Windows-specific
            "VCINSTALLDIR", "VSINSTALLDIR", "VS170COMNTOOLS", "VS160COMNTOOLS",
            "WindowsSdkDir", "WindowsSDKVersion", "VSCMD_VER",
            "INCLUDE", "LIB", "LIBPATH",
            # Unix-specific
            "CC", "CXX", "CFLAGS", "CXXFLAGS", "LDFLAGS",
            "LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH",
        ]
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                # Display PATH-like variables as indented lists for readability
                if var in ("PATH", "INCLUDE", "LIB", "LIBPATH", "LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH"):
                    separator = ";" if WINDOWS else ":"
                    paths = value.split(separator)
                    self.app.display_info(f"{var}:")
                    for path in paths:
                        if path:  # Skip empty entries
                            self.app.display_info(f"    {path}")
                else:
                    self.app.display_info(f"{var}={value}")

        self.app.display_info("")
        self.app.display_info("=" * 70)
        self.app.display_info("END TOOLING REPORT")
        self.app.display_info("=" * 70)
        self.app.display_info("")

    def _print_windows_tooling(self) -> None:
        """Print Windows-specific tooling information."""
        self.app.display_info("--- Windows Compiler Toolchain ---")

        # MSVC compiler version (cl.exe)
        try:
            result = subprocess.run(
                ["cl"],
                capture_output=True,
                text=True,
                shell=True,
            )
            # cl.exe outputs version info to stderr
            output = result.stderr or result.stdout
            if output:
                # Extract first line which contains version info
                first_line = output.strip().split('\n')[0]
                self.app.display_info(f"MSVC (cl.exe): {first_line}")
            else:
                self.app.display_info("MSVC (cl.exe): Available but no version output")
        except Exception as e:
            self.app.display_info(f"MSVC (cl.exe): NOT FOUND or error - {e}")

        # Try to get Visual Studio version from environment
        vscmd_ver = os.environ.get("VSCMD_VER")
        if vscmd_ver:
            self.app.display_info(f"Visual Studio Version (VSCMD_VER): {vscmd_ver}")

        vs_installdir = os.environ.get("VSINSTALLDIR")
        if vs_installdir:
            self.app.display_info(f"VS Install Dir: {vs_installdir}")

        # Windows SDK version
        sdk_version = os.environ.get("WindowsSDKVersion", "").rstrip("\\")
        if sdk_version:
            self.app.display_info(f"Windows SDK Version: {sdk_version}")

        sdk_dir = os.environ.get("WindowsSdkDir")
        if sdk_dir:
            self.app.display_info(f"Windows SDK Dir: {sdk_dir}")

        # MSVC tools version from VC install dir
        vc_tools = os.environ.get("VCToolsVersion")
        if vc_tools:
            self.app.display_info(f"VC Tools Version: {vc_tools}")

        # Link.exe version
        try:
            result = subprocess.run(
                ["link", "/version"],
                capture_output=True,
                text=True,
                shell=True,
            )
            output = (result.stdout or result.stderr).strip()
            if output:
                self.app.display_info(f"Linker (link.exe): {output.split(chr(10))[0]}")
        except Exception:
            pass

    def _print_linux_tooling(self) -> None:
        """Print Linux-specific tooling information."""
        self.app.display_info("--- Linux Compiler Toolchain ---")

        # GCC version
        self._print_tool_version("gcc", "--version")
        self._print_tool_version("g++", "--version")

        # ld version
        self._print_tool_version("ld", "--version")

        # libc version
        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            gnu_get_libc_version = libc.gnu_get_libc_version
            gnu_get_libc_version.restype = ctypes.c_char_p
            self.app.display_info(f"glibc version: {gnu_get_libc_version().decode()}")
        except Exception:
            pass

    def _print_macos_tooling(self) -> None:
        """Print macOS-specific tooling information."""
        self.app.display_info("--- macOS Compiler Toolchain ---")

        # Clang version
        self._print_tool_version("clang", "--version")
        self._print_tool_version("clang++", "--version")

        # Xcode version
        try:
            result = subprocess.run(
                ["xcodebuild", "-version"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                self.app.display_info(f"Xcode: {result.stdout.strip().replace(chr(10), ' ')}")
        except Exception:
            pass

        # macOS SDK
        try:
            result = subprocess.run(
                ["xcrun", "--show-sdk-version"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                self.app.display_info(f"macOS SDK Version: {result.stdout.strip()}")
        except Exception:
            pass

    def _print_tool_version(self, tool: str, version_arg: str) -> None:
        """Print version of a tool if available."""
        try:
            result = subprocess.run(
                [tool, version_arg],
                capture_output=True,
                text=True,
            )
            output = (result.stdout or result.stderr).strip()
            if output and result.returncode == 0:
                # Get first line only for cleaner output
                first_line = output.split('\n')[0]
                self.app.display_info(f"{tool}: {first_line}")
            else:
                self.app.display_info(f"{tool}: NOT FOUND")
        except FileNotFoundError:
            self.app.display_info(f"{tool}: NOT FOUND")
        except Exception as e:
            self.app.display_info(f"{tool}: ERROR - {e}")

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

        # Print tooling report at the start of the build
        self._print_tooling_report()

        # Check if installer package already exists
        installer_dir = Path(f"build/cefpython3_{self.version}_{OS_POSTFIX2}")
        if installer_dir.exists():
            self.app.display_info(f"Installer package already exists at {installer_dir}")
            self.app.display_info("Skipping build steps, using existing package")
        else:
            self.app.display_info("Starting CEF Python build process...")
            # Note: build_libs_only.py handles both C++ and Cython builds in the correct order
            # It first builds Cython to generate headers, then builds C++ projects
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
