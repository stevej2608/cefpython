# Build instructions

Table of contents:
* [Preface](#preface)
* [Quick build instructions for Windows](#quick-build-instructions-for-windows)
* [Quick build instructions for Linux](#quick-build-instructions-for-linux)
* [Build Commands Reference](#build-commands-reference)
* [Understanding Multi-Version Builds](#understanding-multi-version-builds)
* [Testing Built Wheels](#testing-built-wheels)
* [Requirements](#requirements)
  * [Windows](#windows)
  * [Linux](#linux)
  * [Mac](#mac)
  * [All platforms](#all-platforms)
* [CEF Automated Builds (Spotify)](#cef-automated-builds-spotify)
* [Notes](#notes)
* [How to patch mini tutorial](#how-to-patch-mini-tutorial)


## Preface

These instructions cover building CEF Python v123+ using the modern Hatch-based
build system.

**For CEF 123+ (Chromium 123+) - Modern Build System:**
- Uses Hatch for project management
- Automatically downloads CEF binaries from Spotify CDN
- Supports multi-platform builds (Windows, Linux, macOS)
- Supports Python 3.11, 3.12, and 3.13

See the [Quick build instructions for Windows](#quick-build-instructions-for-windows)
and [Quick build instructions for Linux](#quick-build-instructions-for-linux)
sections. These instructions are complete and you should be able to build
cefpython in less than 30 minutes (including CEF binary download time).

Before you can build CEF Python you must satisfy [requirements](#requirements)
listed on this page.


## Quick build instructions for Windows

Complete steps for building CEF Python with Python 3.11+ using the
modern Hatch-based build system.

When cloning repository you should checkout a stable branch which
are named "cefpythonXX" where XX is Chromium version number.

1) Tested and works fine on Windows 10/11 64-bit

2) Install **Visual Studio Build Tools 2022** or full Visual Studio 2022/2019
   - Download from: https://visualstudio.microsoft.com/downloads/
   - For Build Tools, select "Desktop development with C++" workload
   - Includes CMake and build tools

3) Download [ninja](https://github.com/ninja-build/ninja/releases) 1.7.2 or later
   - Extract and add to PATH, OR
   - Install via chocolatey: `choco install ninja`, OR
   - Use from within VS Developer Command Prompt (recommended with Build Tools)

4) Install Python 3.11 or later (tested with 3.11, 3.12, 3.13)
   - For multi-version builds, install all target Python versions
   - Download from: https://www.python.org/downloads/

5) Clone cefpython and checkout the appropriate branch:
```
git clone https://github.com/cztomczak/cefpython.git
cd cefpython/
git checkout cefpython123
```

6) **IMPORTANT**: If using Build Tools (not full Visual Studio), open
   "Developer Command Prompt for VS 2022" or "Developer PowerShell for VS 2022"
   from the Start Menu and navigate to your project directory.

   **VSCode Users**: You can configure VSCode to have a Developer Command Prompt terminal.
   Add this to your `.vscode/settings.json`:

   ```json
   {
       "terminal.integrated.profiles.windows": {
           "Dev CMD": {
               "path": "cmd.exe",
               "args": [
                   "/k",
                   "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Auxiliary\\Build\\vcvars64.bat"
               ]
           }
       }
   }
   ```

   Then select "Dev CMD" from the terminal dropdown. This ensures all build commands
   run with the correct Visual Studio environment variables.

   **Note**: Adjust the path if you have Visual Studio 2019 or full Visual Studio 2022:
   - VS Build Tools 2022: `...\Microsoft Visual Studio\2022\BuildTools\...\vcvars64.bat`
   - VS Community 2022: `...\Microsoft Visual Studio\2022\Community\...\vcvars64.bat`
   - VS Build Tools 2019: `...\Microsoft Visual Studio\2019\BuildTools\...\vcvars64.bat`

7) Install Hatch (modern Python project manager):
```
pip install hatch
```

8) Build cefpython for current Python version:
```
hatch run build:all
```

This will:
- Download CEF binaries from Spotify CDN (~5.8GB, one-time download)
- Build the libcef_dll_wrapper library
- Build the cefpython module for your Python version
- Create wheel package in `dist/`

**Output**: `dist/cefpython3-123.0-cp3XX-cp3XX-win_amd64.whl`

## Building for Multiple Python Versions

To build wheels for Python 3.11, 3.12, and 3.13:

1) Install all target Python versions on your system

2) Validate environments (optional but recommended):
```
hatch run build:prepare-envs
```

3) Build for all Python versions:
```
# Setup CEF binaries (one-time, shared across all versions)
hatch run build:setup-cef

# Build wheels for all versions (3.11, 3.12, 3.13)
hatch run build-matrix:complete
```

4) Or build for specific Python version only:
```
hatch run build-matrix.py3.11:complete
hatch run build-matrix.py3.12:complete
hatch run build-matrix.py3.13:complete
```

**Output**: Multiple wheels in `dist/`:
- `cefpython3-123.0-cp311-cp311-win_amd64.whl`
- `cefpython3-123.0-cp312-cp312-win_amd64.whl`
- `cefpython3-123.0-cp313-cp313-win_amd64.whl`

**Note**: Each wheel is Python version-specific due to compiled Cython extensions


## Quick build instructions for Linux

Complete steps for building CEF Python with Python 3.11+ using the
modern Hatch-based build system.

When cloning repository you should checkout a stable branch which
are named "cefpythonXX" where XX is Chromium version number.

1) Tested and works fine on Ubuntu 20.04+ 64-bit

2) Install required packages:
```
sudo apt-get install python3 python3-pip cmake g++ ninja-build libgtk2.0-dev libgtkglext1-dev
```

3) Install Python 3.11 or later (tested with 3.11, 3.12, 3.13)
   - For multi-version builds, install all target Python versions
   - Ubuntu: `sudo apt-get install python3.11 python3.12 python3.13`
   - Or use [pyenv](https://github.com/pyenv/pyenv) to manage multiple versions

4) Install Hatch (modern Python project manager):
```
pip3 install hatch
```

5) Clone cefpython and checkout the appropriate branch:
```
git clone https://github.com/cztomczak/cefpython.git
cd cefpython/
git checkout cefpython123
```

6) Build cefpython for current Python version:
```
hatch run build:all
```

This will:
- Download CEF binaries from Spotify CDN (~5.8GB, one-time download)
- Build the libcef_dll_wrapper library
- Build the cefpython module for your Python version
- Create wheel package in `dist/`

**Output**: `dist/cefpython3-123.0-cp3XX-cp3XX-manylinux1_x86_64.whl`

## Building for Multiple Python Versions

To build wheels for Python 3.11, 3.12, and 3.13:

1) Install all target Python versions on your system

2) Validate environments (optional but recommended):
```
hatch run build:prepare-envs
```

3) Build for all Python versions:
```
# Setup CEF binaries (one-time, shared across all versions)
hatch run build:setup-cef

# Build wheels for all versions (3.11, 3.12, 3.13)
hatch run build-matrix:complete
```

4) Or build for specific Python version only:
```
hatch run build-matrix.py3.11:complete
hatch run build-matrix.py3.12:complete
hatch run build-matrix.py3.13:complete
```

**Output**: Multiple wheels in `dist/`:
- `cefpython3-123.0-cp311-cp311-manylinux1_x86_64.whl`
- `cefpython3-123.0-cp312-cp312-manylinux1_x86_64.whl`
- `cefpython3-123.0-cp313-cp313-manylinux1_x86_64.whl`

**Note**: Each wheel is Python version-specific due to compiled Cython extensions


## Build Commands Reference

### Single Python Version Build

| Command | Description |
| --- | --- |
| `hatch run build:all` | Complete build for current Python version |
| `hatch run build:setup-cef` | Download and setup CEF binaries (one-time) |
| `hatch run build:build-libs` | Build C++ libraries and Cython extensions |
| `hatch run build:build-wheel` | Create wheel package from existing build |
| `hatch run build:checksums` | Generate SHA256 checksums for wheels |
| `hatch run build:prepare-envs` | Validate and create multi-version environments |

### Multi-Version Build (Python 3.11, 3.12, 3.13)

| Command | Description |
| --- | --- |
| `hatch run build-matrix:complete` | Build for all Python versions (3.11, 3.12, 3.13) |
| `hatch run build-matrix.py3.11:complete` | Build for Python 3.11 only |
| `hatch run build-matrix.py3.12:complete` | Build for Python 3.12 only |
| `hatch run build-matrix:wheel` | Build wheels for all versions (CEF setup must be done first) |
| `hatch run build-matrix.py3.11:wheel` | Build wheel for Python 3.11 only |

### Environment Management

| Command | Description |
| --- | --- |
| `hatch env show` | List all available environments |
| `hatch env create build-matrix` | Pre-create all Python version environments |
| `hatch env create build-matrix.py3.11` | Create Python 3.11 environment only |
| `hatch env remove build-matrix` | Remove all matrix environments |
| `hatch env prune` | Remove all unused environments |

### Wheel File Naming

Wheels follow the [PEP 427](https://peps.python.org/pep-0427/) standard:

```
{distribution}-{version}-{python}-{abi}-{platform}.whl
```

Examples:
- `cefpython3-123.0-cp312-cp312-win_amd64.whl`
  - Python 3.12 specific, Windows 64-bit
- `cefpython3-123.0-cp311-cp311-manylinux1_x86_64.whl`
  - Python 3.11 specific, Linux 64-bit

**Important**: The `cp3XX-cp3XX` tags indicate Python version-specific wheels.
Each wheel only works with its specific Python version due to compiled Cython extensions.


## Understanding Multi-Version Builds

### Why Multiple Wheels?

CEFPython contains compiled Cython extensions (`.pyd` on Windows, `.so` on Linux)
that use Python's C API. The C API changes between Python minor versions:

- Python 3.11 uses ABI `cp311`
- Python 3.12 uses ABI `cp312`
- Python 3.13 uses ABI `cp313`

A wheel compiled for Python 3.12 **will not work** on Python 3.11 or 3.13.

### How Matrix Builds Work

When you run `hatch run build-matrix:complete`, Hatch:

1. Creates isolated virtual environments for each Python version:
   ```
   .venv/
   ├── hatch-build-matrix.py3.11/
   ├── hatch-build-matrix.py3.12/
   └── hatch-build-matrix.py3.13/
   ```

2. Installs dependencies in each environment (Cython, setuptools, etc.)

3. Compiles Cython extensions separately for each Python version

4. Creates version-specific wheels in `dist/`

### Shared vs Per-Version

**Shared across all Python versions:**
- CEF binaries (`build/cef123_*/`) - Platform-specific, not Python-specific
- C++ libraries - Compiled once, used by all Python versions

**Per Python version:**
- Cython extensions - Must be recompiled for each Python version
- Wheel packages - Each contains its own compiled extensions

### Build Time Considerations

Building for multiple Python versions takes approximately 3x longer than a
single version build, as Cython extensions must be compiled separately for
each version. However, CEF binaries (the largest component, ~5.8GB) are
downloaded and built only once.

Typical build times on a modern system:
- Single version: ~10-15 minutes (after CEF download)
- Three versions: ~30-45 minutes total


## Testing Built Wheels

After building, you can test the wheels:

### Install and Test Single Wheel

```bash
# Create a test virtual environment
python3.12 -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install the wheel
pip install dist/cefpython3-123.0-cp312-cp312-win_amd64.whl

# Test the installation
python -c "import cefpython3; print(cefpython3.__version__)"

# Run an example
python -m cefpython3.examples.hello_world
```

### Verify Multi-Version Wheels

```bash
# Test with Python 3.11
python3.11 -m venv test-311
source test-311/bin/activate
pip install dist/cefpython3-123.0-cp311-cp311-*.whl
python -c "import cefpython3; print(cefpython3.__version__)"
deactivate

# Test with Python 3.12
python3.12 -m venv test-312
source test-312/bin/activate
pip install dist/cefpython3-123.0-cp312-cp312-*.whl
python -c "import cefpython3; print(cefpython3.__version__)"
deactivate

# Test with Python 3.13
python3.13 -m venv test-313
source test-313/bin/activate
pip install dist/cefpython3-123.0-cp313-cp313-*.whl
python -c "import cefpython3; print(cefpython3.__version__)"
deactivate
```

### Run Unit Tests

```bash
# Using Hatch's test environment
hatch test

# Run tests for all Python versions
hatch test --all

# Run tests for specific Python version
hatch test --python 3.12
```


## Requirements

Below are platform specific requirements. Do these first before
following instructions in the "All platforms" section that lists
requirements common for all platforms.

### Windows

* **Python 3.11 or later** (tested with Python 3.11, 3.12, 3.13)
  * For multi-version builds, install all target Python versions from [python.org](https://www.python.org/downloads/)
  * Alternative: Use [pyenv-win](https://github.com/pyenv-win/pyenv-win) to manage multiple Python versions
* **Visual Studio Build Tools 2022** or **Visual Studio 2022/2019** (Community, Professional, or Enterprise)
  * Download from: https://visualstudio.microsoft.com/downloads/
  * For Build Tools installer: Select "Desktop development with C++" workload
  * This includes CMake and required build tools
  * **IMPORTANT**: When using Build Tools (not full Visual Studio), you must run all build commands from:
    * "Developer Command Prompt for VS 2022", OR
    * "Developer PowerShell for VS 2022"
    * These are available in the Start Menu after installing Build Tools
* **Ninja** build system (recommended):
  * Download [ninja](https://github.com/ninja-build/ninja/releases) 1.7.2 or later and add to PATH, OR
  * Install via chocolatey: `choco install ninja`, OR
  * Available automatically when running from VS Developer Command Prompt
* **CMake** 3.0 or later (included with VS Build Tools, or download from https://cmake.org/download/)
* **Hatch** Python project manager: `pip install hatch`

**Note for Visual Studio Build Tools users**: The Build Tools don't register Visual Studio generators
with CMake in the same way as the full IDE. The build scripts now automatically try the Ninja generator
first (which works with Build Tools), then fall back to Visual Studio generators. Make sure to run from
the Developer Command Prompt/PowerShell to ensure all build tools are in your PATH.

**Troubleshooting Windows builds:**
* If CMake cannot find Visual Studio: You're likely using Build Tools without running from Developer Command Prompt
  * Solution: Open "Developer Command Prompt for VS 2022" or "Developer PowerShell for VS 2022" from Start Menu
  * **VSCode users**: Configure a custom terminal profile (see Quick Build Instructions step 6 above)
* If you see "ninja: command not found": Install ninja or it's not in PATH
  * Solution: `choco install ninja` or download from GitHub and add to PATH
  * Alternative: Ninja is available in VS Developer Command Prompt without separate installation
* If you prefer full Visual Studio IDE: Install Visual Studio Community 2022 with "Desktop development with C++" workload

**VSCode Terminal Configuration:**

For convenience, you can set up a permanent Developer Command Prompt terminal in VSCode.
This is especially useful when using Visual Studio Build Tools (not full VS).

Create or edit `.vscode/settings.json` in your project:

```json
{
    "terminal.integrated.profiles.windows": {
        "VS 2022 C++ Dev CMD": {
            "path": "cmd.exe",
            "args": [
                "/k",
                "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Auxiliary\\Build\\vcvars64.bat"
           ]
        },
        "VS 2022 C++ Dev CMD PowerShell": {
            "path": "powershell.exe",
            "args": [
                "-NoExit",
                "-Command",
                "& 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Auxiliary\\Build\\vcvars64.bat'"
            ]
        }
    }
}
```

This configuration:
- Adds "Dev CMD" and "Dev PowerShell" terminal profiles
- Automatically runs `vcvars64.bat` to set up Visual Studio environment
- Optionally sets "Dev CMD" as the default terminal

Access it via:
1. Terminal dropdown menu (click "+" dropdown)
2. Select "Dev CMD" or "Dev PowerShell"
3. All build commands will now have correct environment variables

**Path variations:**
- VS Build Tools 2022: `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat`
- VS Community 2022: `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat`
- VS Professional 2022: `C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat`
- VS Build Tools 2019: `C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat`

To find your vcvars64.bat path:
```cmd
dir "C:\Program Files*\Microsoft Visual Studio" /s /b | findstr vcvars64.bat
```


### Linux

* **Python 3.11 or later** (tested with Python 3.11, 3.12, 3.13)
  * For multi-version builds, install all target Python versions:
    * Ubuntu/Debian: `sudo apt-get install python3.11 python3.12 python3.13 python3.11-dev python3.12-dev python3.13-dev`
    * Alternative: Use [pyenv](https://github.com/pyenv/pyenv) to manage multiple Python versions
* Install required packages:
  ```
  sudo apt-get install python3 python3-pip cmake g++ ninja-build libgtk2.0-dev libgtkglext1-dev
  ```
* **Hatch** Python project manager: `pip3 install hatch`
* For Fedora build dependencies see [Issue #466](https://github.com/cztomczak/cefpython/issues/466#issuecomment-419794341)


### Mac

* **Python 3.11 or later** (tested with Python 3.11, 3.12, 3.13)
  * For multi-version builds, install all target Python versions:
    * Homebrew: `brew install python@3.11 python@3.12 python@3.13`
    * Alternative: Use [pyenv](https://github.com/pyenv/pyenv) to manage multiple Python versions
* **macOS 10.13+**, Xcode 10+ and Xcode command line tools. Only 64-bit builds
  are supported.
* Install Xcode command line tools: `xcode-select --install`
* **Ninja** build system:
  * Download [ninja](https://github.com/ninja-build/ninja/releases) 1.7.2 or later and add to PATH, OR
  * Install via Homebrew: `brew install ninja`
* **CMake**: Download from https://cmake.org/download/ or install via Homebrew: `brew install cmake`
* **Hatch** Python project manager: `pip3 install hatch`


### All platforms

* **Python 3.11+** is required (tested with Python 3.11, 3.12, 3.13)
* **Hatch** for modern build system: `pip install hatch`
* For multi-version builds, all target Python versions must be installed on the system

**Note**: CEFPython uses compiled Cython extensions, so wheels are Python version-specific.
A wheel built for Python 3.12 will not work on Python 3.11 or 3.13. Use the multi-version
build commands to create wheels for all supported Python versions.


## CEF Automated Builds (Spotify)

CEF Python uses prebuilt CEF binaries from the Spotify CDN:
* https://cef-builds.spotifycdn.com/index.html

The `hatch run build:setup-cef` command automatically downloads the correct
CEF version for your platform. The version is determined by the constants in
`src/version/` directory.


## Notes

When building for multiple Python versions on Linux/Mac use
pyenv to manage multiple Python installations, see
[Issue #249](https://github.com/cztomczak/cefpython/issues/249)
for details.

Official CEF Python binaries may come with additional patches applied
to CEF/Chromium depending on platform. These patches can be found
in the "cefpython/patches/" directory.


## How to patch mini tutorial

Create a patch from unstaged changes in current directory:
```
cd chromium/src/cef/
git diff --no-prefix --relative > issue251.patch
```

To create a patch from last two commits:
```
git diff --no-prefix --relative HEAD~2..HEAD > issue251.patch
# or
git format-patch --no-prefix -2 HEAD --stdout > issue251.patch
```

Apply a patch in current directory and ignore git index:
```
patch -p0 < issue251.patch
```

Apply a patch in current directory and do not ignore git index:
```
cd chromium/src/cef/
git apply -v -p0 issue251.patch
```
