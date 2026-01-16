# CEF Python Build System Overview

This document provides a comprehensive overview of the CEF Python build system, including the build process, phases, scripts, and platform management.

## Table of Contents

- [General Overview](#general-overview)
- [Build Phases](#build-phases)
- [Key Scripts and Tools](#key-scripts-and-tools)
- [Platform Management](#platform-management)
- [Build Environments](#build-environments)
- [Directory Structure](#directory-structure)
- [Common Build Commands](#common-build-commands)

---

## General Overview

The CEF Python build system is designed to:

1. **Download and setup CEF binaries** for the target platform
2. **Build native C++ libraries** (client_handler, libcefpythonapp, subprocess, cpp_utils)
3. **Compile Cython extensions** that provide Python bindings to CEF
4. **Create installer packages** with the correct directory structure
5. **Build distributable wheel packages** for PyPI

The build system uses **Hatch** as the primary build orchestrator, with custom Python scripts handling platform-specific compilation and packaging.

### Key Technologies

- **Hatch**: Build system and environment management
- **Hatchling**: Build backend (PEP 517 compliant)
- **Cython 3.2.4+**: Python-to-C compilation for bindings
- **CMake + Ninja**: CEF wrapper library compilation
- **Make/Setuptools**: Platform-specific C++ compilation
- **Python build module**: Wheel generation

---

## Build Phases

The build process consists of 5 main phases:

### Phase 1: Setup CEF Binaries

**Script**: `tools/setup_cef.py`

**Purpose**: Downloads and prepares the CEF binaries for the target platform.

**Actions**:
1. Detects the platform (Linux, Windows, Mac)
2. Downloads CEF binary distribution (~5.8GB) from Spotify CDN if not present
3. Extracts the CEF archive
4. Builds the `libcef_dll_wrapper` library using CMake
5. Copies wrapper library and `libcef.lib` to appropriate locations

**Platform-specific behavior**:
- **Linux/Mac**: Uses Ninja generator, outputs `.a` static library
- **Windows**: Tries Ninja first, falls back to Visual Studio generators, outputs `.lib`

**CEF Version**: `123.0.7+g6a21509+chromium-123.0.6312.46`

**Output Directory**: `build/cef123_{CEF_VERSION}_{PLATFORM}/`

### Phase 2: Build C++ Libraries

**Scripts**:
- `tools/build_libs_only.py` (without tests)
- `tools/build.py` (with tests)
- `tools/build_cpp_projects.py` (Windows)

**Purpose**: Compiles the native C++ projects that interface with CEF.

**C++ Projects Built**:
1. **client_handler** - Handles CEF browser callbacks and events
2. **libcefpythonapp** - CEF application framework
3. **subprocess** - CEF subprocess executable
4. **cpp_utils** - C++ utility functions

**Platform-specific compilation**:
- **Linux/Mac**: Uses Makefiles in `src/client_handler/`, `src/subprocess/`, `src/cpp_utils/`
- **Windows**: Uses setuptools/distutils in `tools/build_cpp_projects.py`

**Compiler flags**:
- Linux: `-std=gnu++17 -O3 -DNDEBUG -Wall -Werror -Wno-deprecated-declarations`
- Mac: Adds `-arch x86_64 -stdlib=libc++ -fno-rtti` and visibility flags
- Windows: `/MD` runtime, Visual Studio compiler

**Output Directory**: `build/build_cefpython/`

### Phase 3: Build Cython Extension

**Scripts**:
- `tools/build_libs_only.py`
- Hatch-Cython plugin (configured in `pyproject.toml`)

**Purpose**: Compiles the Cython `.pyx` files into Python extension modules.

**Actions**:
1. Generates `compile_time_constants.pxi` with platform info
2. Copies and fixes `.pyx` files
3. Runs Cython compilation to generate C code
4. Compiles C code into `.pyd` (Windows) or `.so` (Linux/Mac) extension
5. Generates `cefpython_py{version}.h` header file
6. Creates a "fixed" version of the header file

**First-run behavior**: The build may fail on the first run because the Cython-generated header doesn't exist yet. The script detects this, creates the header, and re-runs automatically.

**Output**: `cefpython_py{pyversion}.{pyd|so}` in `build/build_cefpython/`

### Phase 4: Create Installer Package

**Script**: `tools/make_installer.py`

**Purpose**: Assembles all built components into a distributable package structure.

**Actions**:
1. Creates `build/cefpython3_{VERSION}_{PLATFORM}/` directory
2. Copies Python package files to `cefpython3/` subdirectory:
   - `__init__.py` (with version substitution)
   - Cython extension module
   - CEF binaries (libcef.so, DLLs, resources, locales)
   - Subprocess executable
3. Copies examples to `examples/` subdirectory
4. Generates package metadata files

**Output Directory**: `build/cefpython3_{VERSION}_{PLATFORM}/`

Example: `build/cefpython3_123.0_linux64/`

### Phase 5: Build Wheel Package

**Scripts**:
- `tools/build_all.py` (calls `python -m build`)
- `hatch_build.py` (Hatch build hook)

**Purpose**: Creates a distributable wheel package for PyPI.

**Actions**:
1. Hatch build hook (`hatch_build.py`) configures wheel paths
2. Sets `force_include` to include the installer package in the wheel
3. Python build module creates the wheel file
4. Generates checksums (MD5 and SHA256)

**Output**: `dist/cefpython3-{VERSION}-{PYTHON_VERSION}-{PLATFORM}.whl`

Example: `dist/cefpython3-123.0-cp311-cp311-linux_x86_64.whl`

---

## Key Scripts and Tools

### Orchestration Scripts

#### `tools/build_all.py`
**Purpose**: Top-level orchestrator for the complete build process.

**Usage**: `hatch run build:all`

**Phases**:
1. Setup CEF binaries
2. Build C++ libraries
3. Build wheel
4. Generate checksums

**Error Handling**: Each phase is run with error detection; build stops if any phase fails.

#### `hatch_build.py`
**Purpose**: Custom Hatch build hook (PEP 517 compliant).

**Class**: `CefPythonBuildHook(BuildHookInterface)`

**Methods**:
- `initialize()` - Main entry point, runs all build phases
- `_detect_cef_directory()` - Locates CEF binaries
- `_build_native_libraries()` - Builds C++ projects
- `_build_cython_extension()` - Compiles Cython
- `_create_installer_package()` - Assembles package
- `_configure_wheel_paths()` - Sets up wheel structure
- `clean()` - Removes build artifacts

**Configuration**: `pyproject.toml` section `[tool.hatch.build.hooks.custom]`

### Build Scripts

#### `tools/setup_cef.py`
**Purpose**: Downloads and prepares CEF binaries.

**Key Functions**:
- `get_platform_info()` - Returns OS_POSTFIX2 and CEF_POSTFIX2
- `main()` - Downloads, extracts, builds wrapper library

**CEF URL**: `https://cef-builds.spotifycdn.com/cef_binary_{VERSION}_{PLATFORM}.tar.bz2`

#### `tools/build_libs_only.py`
**Purpose**: Builds C++ and Cython without tests or installation.

**Usage**: `python tools/build_libs_only.py 123.0 --fast`

**Key Features**:
- Handles first-run scenario (missing header file)
- Calls platform-specific compilation functions
- Re-runs itself if header needs to be generated

#### `tools/build.py`
**Purpose**: Full build including tests (legacy, used by build_libs_only.py).

**Key Functions**:
- `check_cython_version()` - Validates Cython version
- `setup_environ()` - Sets environment variables
- `copy_and_fix_pyx_files()` - Prepares Cython source files
- `build_cefpython_module()` - Compiles Cython extension
- `fix_cefpython_api_header_file()` - Fixes generated header
- `compile_cpp_projects_unix()` - Unix compilation
- `compile_cpp_projects_with_setuptools()` - Windows compilation

#### `tools/make_installer.py`
**Purpose**: Creates the installer package structure.

**Usage**: `python tools/make_installer.py 123.0`

**Actions**:
1. Creates package directory structure
2. Copies binaries and resources
3. Substitutes version numbers in templates
4. Removes CEF sample apps

#### `tools/generate_checksums.py`
**Purpose**: Generates MD5 and SHA256 checksums for wheel files.

**Output Files**:
- `dist/MD5SUMS`
- `dist/SHA256SUMS`

### Utility Scripts

#### `tools/common.py`
**Purpose**: Platform detection and common utilities.

**Key Variables**:
- `OS_POSTFIX` - "win", "linux", "mac"
- `OS_POSTFIX2` - "win64", "linux64", "mac64" (includes architecture)
- `CEF_POSTFIX2` - "windows64", "linux64", "macosx64" (CEF naming)
- `PYVERSION` - Python version as string ("311", "312", "313")
- `WINDOWS`, `LINUX`, `MAC` - Platform booleans

**Key Functions**:
- `get_cefpython_version()` - Reads version from `src/version/cef_version_{OS}.h`
- `get_version_from_command_line_args()` - Extracts version from argv
- `get_python_include_path()` - Locates Python headers
- `_detect_cef_binaries_libraries_dir()` - Finds CEF directory

#### `tools/build_cpp_projects.py`
**Purpose**: Windows-specific C++ compilation using setuptools.

**Projects**: Compiles all 4 C++ projects using Extension modules.

---

## Platform Management

### Platform Detection

Platform detection is centralized in `tools/common.py`:

```python
OS_POSTFIX = "win" | "linux" | "mac"
OS_POSTFIX2 = "win64" | "linux64" | "mac64"
CEF_POSTFIX2 = "windows64" | "linux64" | "macosx64"
```

Detection uses `platform.system()` and `struct.calcsize('P')` for architecture.

### Platform-Specific Version Headers

Each platform has its own CEF version header:

- `src/version/cef_version_win.h`
- `src/version/cef_version_linux.h`
- `src/version/cef_version_mac.h`

These headers contain:
- `CEF_VERSION` - Full CEF version string
- `CHROME_VERSION_MAJOR` - Major Chrome version (123)
- `CEF_COMMIT_NUMBER` - CEF commit number
- `CEF_API_HASH_PLATFORM` - Platform-specific API hash

The build system reads these headers using `get_cefpython_version()` to determine which CEF binaries to download and build against.

### Platform-Specific Compilation

#### Linux/Mac (Unix)
- **Build method**: Makefiles
- **Compiler**: g++/clang
- **Flags**: `-std=gnu++17 -O3 -DNDEBUG`
- **Makefiles**:
  - `src/client_handler/Makefile`
  - `src/subprocess/Makefile`
  - `src/subprocess/Makefile-libcefpythonapp`
  - `src/cpp_utils/Makefile`
- **Extension**: `.so` (shared object)
- **Static lib**: `.a`

#### Windows
- **Build method**: setuptools/distutils
- **Compiler**: MSVC (Visual Studio)
- **Runtime**: `/MD` (Multi-threaded DLL)
- **Script**: `tools/build_cpp_projects.py`
- **Extension**: `.pyd` (Python DLL)
- **Static lib**: `.lib`

#### Mac-Specific
- **Architecture**: x86_64 (arm64 support TBD)
- **Flags**: `-arch x86_64 -stdlib=libc++ -fno-rtti`
- **Framework linking**: CEF framework dependency

### Platform-Specific CEF Setup

#### Linux
- **CEF binary name**: `cef_binary_{VERSION}_linux64.tar.bz2`
- **Wrapper library**: `libcef_dll_wrapper.a`
- **CEF library**: `libcef.so` (loaded via ctypes)
- **Subprocess**: `subprocess` (no extension)

#### Windows
- **CEF binary name**: `cef_binary_{VERSION}_windows64.tar.bz2`
- **Wrapper library**: `libcef_dll_wrapper_MD.lib`
- **CEF library**: `libcef.lib` + `libcef.dll`
- **Subprocess**: `subprocess.exe`
- **CMake generators**: Ninja (preferred) or Visual Studio 2019/2022

#### Mac
- **CEF binary name**: `cef_binary_{VERSION}_macosx64.tar.bz2`
- **Wrapper library**: `libcef_dll_wrapper.a`
- **CEF framework**: `Chromium Embedded Framework.framework`
- **Subprocess**: `subprocess` (inside .app bundle)

### Platform-Specific Wheel Names

Wheel filenames follow PEP conventions:

- **Linux**: `cefpython3-123.0-cp311-cp311-linux_x86_64.whl`
- **Windows**: `cefpython3-123.0-cp311-cp311-win_amd64.whl`
- **Mac**: `cefpython3-123.0-cp311-cp311-macosx_10_9_x86_64.whl`

---

## Build Environments

The build system uses Hatch environments defined in `pyproject.toml`.

### `build` Environment

**Purpose**: Main build environment for complete package builds.

**Configuration**: `[tool.hatch.envs.build]`

**Dependencies**:
- `hatchling` - Build backend
- `hatch-cython>=0.5.0` - Cython build hook
- `cython>=3.2.4,<4.0` - Cython compiler
- `pillow>=9.0` - Image library (for examples)
- `setuptools>=65.0` - Python package tools
- `build>=1.0` - Python build module

**Detached**: Yes (isolated from default environment)

**Scripts**:
- `all` - Complete build: `python tools/build_all.py`
- `setup-cef` - Setup CEF binaries only
- `build-libs` - Build libraries only (fast, no tests)
- `build-libs-with-tests` - Build libraries with tests
- `build-wheel` - Build wheel only (deprecated in favor of `all`)
- `checksums` - Generate checksums
- `prepare-envs` - Prepare multi-version environments

**Usage**: `hatch run build:all`

### `build-matrix` Environment

**Purpose**: Build wheels for multiple Python versions.

**Configuration**: `[tool.hatch.envs.build-matrix]`

**Python matrix**: `["3.11", "3.12", "3.13"]`

**Scripts**:
- `wheel` - Build wheel for specific Python version
- `complete` - Complete build for specific Python version
- `complete-with-tests` - Complete build with tests

**Usage**: `hatch run build-matrix.py3.11:complete`

This allows building for multiple Python versions in parallel or sequentially.

### `test` Environment

**Purpose**: Run unit tests.

**Configuration**: `[tool.hatch.envs.test]`

**Dependencies**:
- `pytest>=7.0`
- `pytest-cov>=4.0`

**Scripts**:
- `run` - Run tests: `pytest unittests/ -v`
- `cov` - Run tests with coverage

**Usage**: `hatch run test:run`

### `default` Environment

**Purpose**: Development environment for examples and quick tests.

**Scripts**:
- `build-cpp` - Build C++ libraries: `python tools/build.py 123.0 --fast`
- `test` - Run unit tests
- `example-hello` - Run hello world example
- `clean` - Clean build artifacts

---

## Directory Structure

```
cefpython/
├── build/                                    # Build output directory
│   ├── cef123_{VERSION}_{PLATFORM}/         # CEF binaries (downloaded)
│   │   ├── bin/                             # CEF runtime files
│   │   ├── lib/                             # CEF libraries
│   │   ├── Release/                         # CEF release binaries
│   │   └── Resources/                       # CEF resources
│   ├── build_cefpython/                     # C++ build output
│   │   ├── cefpython_py{ver}_{os}/         # Cython extension
│   │   ├── cefpython_app_py{ver}_{os}/     # libcefpythonapp build
│   │   ├── client_handler_py{ver}_{os}/    # client_handler build
│   │   ├── cpp_utils_py{ver}_{os}/         # cpp_utils build
│   │   └── subprocess_py{ver}_{os}/        # subprocess build
│   ├── cefpython3_{VERSION}_{PLATFORM}/     # Installer package
│   │   ├── cefpython3/                      # Python package
│   │   │   ├── __init__.py
│   │   │   ├── cefpython_py{ver}.{so|pyd}
│   │   │   ├── libcef.so (or .dll)
│   │   │   ├── subprocess
│   │   │   ├── locales/
│   │   │   └── ...
│   │   └── examples/                        # Example scripts
│   └── cefpython_binary_{VERSION}_{PLATFORM}/ # Binary output directory
├── dist/                                     # Distribution packages
│   ├── cefpython3-{VERSION}-{PYVER}-{PLATFORM}.whl
│   ├── MD5SUMS
│   └── SHA256SUMS
├── src/                                      # Source code
│   ├── client_handler/                      # CEF client handler C++
│   ├── subprocess/                          # CEF subprocess C++
│   ├── cpp_utils/                           # C++ utilities
│   ├── linux/                               # Linux-specific code
│   ├── windows/                             # Windows-specific code
│   ├── mac/                                 # Mac-specific code
│   ├── version/                             # Platform version headers
│   │   ├── cef_version_linux.h
│   │   ├── cef_version_win.h
│   │   └── cef_version_mac.h
│   ├── compile_time_constants.pxi           # Generated Cython constants
│   └── *.pyx                                # Cython source files
├── tools/                                    # Build scripts
│   ├── build_all.py                         # Main build orchestrator
│   ├── setup_cef.py                         # CEF setup
│   ├── build_libs_only.py                   # Library build (no tests)
│   ├── build.py                             # Full build with tests
│   ├── make_installer.py                    # Installer creation
│   ├── generate_checksums.py                # Checksum generation
│   ├── build_cpp_projects.py                # Windows C++ build
│   ├── common.py                            # Platform detection
│   └── ...
├── examples/                                 # Example applications
├── unittests/                                # Unit tests
├── hatch_build.py                           # Hatch build hook
├── pyproject.toml                           # Project configuration
└── README.md
```

---

## Common Build Commands

### Complete Build

Build everything from scratch:
```bash
hatch clean
hatch run build:all
```

This will:
1. Setup CEF binaries
2. Build C++ libraries
3. Build Cython extension
4. Create installer package
5. Build wheel
6. Generate checksums

### Build for Multiple Python Versions

```bash
# Build for Python 3.11
hatch run build-matrix.py3.11:complete

# Build for Python 3.12
hatch run build-matrix.py3.12:complete

# Build for all versions (requires all Python versions installed)
hatch run build-matrix:complete
```

### Incremental Builds

If you've already run the complete build and only need to rebuild parts:

```bash
# Rebuild C++ libraries only
hatch run build:build-libs

# Rebuild wheel only (after manual changes to package)
hatch run build:build-wheel

# Generate checksums only
hatch run build:checksums
```

### Setup CEF Only

Download and setup CEF binaries without building:
```bash
hatch run build:setup-cef
```

### Clean Build Artifacts

```bash
# Clean using Hatch
hatch clean

# Or use the environment script
hatch run default:clean
```

### Testing

```bash
# Run unit tests
hatch run test:run

# Run with coverage
hatch run test:cov
```

### Development Workflow

For quick development iteration:

```bash
# Build C++ and Cython (fast, no packaging)
hatch run default:build-cpp

# Run examples
hatch run default:example-hello
```

---

## Build Troubleshooting

### Common Issues

#### Issue: "CEF binaries not found"
**Solution**: Run `hatch run build:setup-cef` first

#### Issue: "Environment 'build' is not a builder environment"
**Solution**: Don't call `hatch build` from within a hatch environment script. Use `python -m build` instead.

#### Issue: "Cannot import 'hatchling.build'"
**Solution**: Ensure `hatchling` is in the build environment dependencies

#### Issue: First build fails with "header file not found"
**Solution**: This is expected. The script will auto-detect and re-run. If it doesn't, the header generation logic in `build_libs_only.py` handles this.

#### Issue: CMake configuration fails on Windows
**Solution**:
- Run from Visual Studio Developer Command Prompt, or
- Install Ninja build system, or
- Install full Visual Studio 2019/2022

#### Issue: Wrong Cython version
**Solution**: Update `pyproject.toml` `[build-system]` requires section to match the version in the `build` environment

### Platform-Specific Issues

#### Linux
- Ensure g++ and make are installed
- Install Ninja: `sudo apt install ninja-build` (Ubuntu/Debian)
- Check that CEF libraries are extracted correctly

#### Windows
- Requires Visual Studio Build Tools or full Visual Studio
- Set up environment with `vcvarsall.bat`
- Ensure `/MD` runtime is used

#### Mac
- Requires Xcode command line tools
- May need to specify architecture explicitly: `-arch x86_64`

---

## Version Management

### Updating CEF Version

To update to a new CEF version:

1. Update `CEF_VERSION` in `tools/setup_cef.py`
2. Update platform version headers in `src/version/cef_version_{platform}.h`
3. Update `version` in `pyproject.toml` `[project]` section
4. Update `version` in `hatch_build.py` `__init__` method
5. Clean and rebuild: `hatch clean && hatch run build:all`

### Version Sources

The version number appears in multiple places:

- **Python package version**: `pyproject.toml` `[project]` section
- **CEF version**: `tools/setup_cef.py` constant
- **Chrome version**: `src/version/cef_version_{platform}.h` headers
- **Build scripts**: Passed as command-line arg (e.g., `123.0`)

All version numbers should be kept in sync.

---

## Future Improvements

Potential areas for improvement:

1. **Unified version management**: Single source of truth for version numbers
2. **Parallel C++ compilation**: Speed up builds by compiling projects in parallel
3. **Cross-compilation**: Support building for different platforms from a single host
4. **CI/CD integration**: GitHub Actions workflows for automated builds
5. **Binary caching**: Cache compiled CEF binaries to speed up rebuilds
6. **ARM64 support**: Add support for Apple Silicon and ARM Linux
7. **Python 3.14+ support**: Update for future Python versions

---

## References

- [Hatch Documentation](https://hatch.pypa.io/)
- [Cython Documentation](https://cython.readthedocs.io/)
- [CEF Project](https://bitbucket.org/chromiumembedded/cef)
- [PEP 517 - Build Backend Interface](https://www.python.org/dev/peps/pep-0517/)
- [PEP 660 - Editable Installs](https://www.python.org/dev/peps/pep-0660/)
