# Build instructions

Table of contents:
* [Preface](#preface)
* [Quick build instructions for Windows](#quick-build-instructions-for-windows)
* [Quick build instructions for Linux](#quick-build-instructions-for-linux)
* [Requirements](#requirements)
  * [Windows](#windows)
  * [Linux](#linux)
  * [Mac](#mac)
  * [All platforms](#all-platforms)
* [Build using prebuilt CEF binaries and libraries](#build-using-prebuilt-cef-binaries-and-libraries)
* [Build using CEF binaries from Spotify Automated Builds](#build-using-cef-binaries-from-spotify-automated-builds)
* [Build upstream CEF from sources](#build-upstream-cef-from-sources)
  * [Building old unsupported version of Chromium](#building-old-unsupported-version-of-chromium)
  * [Possible errors](#possible-errors)
* [Build CEF manually](#build-cef-manually)
* [CEF Automated Builds (Spotify and Adobe)](#cef-automated-builds-spotify-and-adobe)
* [Notes](#notes)
* [How to patch mini tutorial](#how-to-patch-mini-tutorial)


## Preface

These instructions cover building CEF Python v50+ with the modern Hatch-based build system
(CEF 123+) and legacy build methods (v50-v66).

**For CEF 123+ (Chromium 123+) - Modern Build System:**
- Uses Hatch for project management
- Automatically downloads and builds CEF binaries
- Supports multi-platform builds
- See [Quick build instructions for Windows](#quick-build-instructions-for-windows)

**For older versions (v31-v66) - Legacy Build System:**
- Manual CEF binary downloads
- See sections further down for prebuilt binaries and manual builds

If you would like to quickly build the latest cefpython (CEF 123+), see the
[Quick build instructions for Windows](#quick-build-instructions-for-windows)
and [Quick build instructions for Linux](#quick-build-instructions-for-linux)
sections. These instructions are complete and you should be able to build
cefpython in less than 30 minutes (including CEF binary download time).

There are several types of builds described in this document:

1. **Modern (CEF 123+)**: Build using Hatch - automatically downloads CEF
   binaries from Spotify CDN and builds everything
2. **Legacy**: Build using prebuilt CEF binaries and libraries that were
   uploaded to GH releases (for older versions)
3. **Legacy**: Build using prebuilt CEF binaries from Spotify Automated Builds
4. **Advanced**: Build upstream CEF from sources (takes several hours)

Before you can build CEF Python or CEF you must satisfy
[requirements](#requirements) listed on this page.


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
git checkout cefpython123-multi-platform
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
git checkout cefpython123-multi-platform
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
* To build CEF from sources:
    * Use Windows 10/11 x64. 32-bit OS'es are not supported. For more details
     see [here](https://www.chromium.org/developers/how-tos/build-instructions-windows).
    * For CEF 123+ (Chromium 123+), Visual Studio 2022 or Build Tools 2022 is required
    * Install [CMake](https://cmake.org/) 3.0 or newer and add cmake.exe to PATH
    * Install [ninja](https://github.com/ninja-build/ninja/releases) and add ninja.exe to PATH
    * You need about 16 GB of RAM during linking. If there is an error
        just add additional virtual memory.

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
        "Dev CMD": {
            "path": "cmd.exe",
            "args": [
                "/k",
                "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Auxiliary\\Build\\vcvars64.bat"
            ]
        },
        "Dev PowerShell": {
            "path": "powershell.exe",
            "args": [
                "-NoExit",
                "-Command",
                "& 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Auxiliary\\Build\\vcvars64.bat'"
            ]
        }
    },
    "terminal.integrated.defaultProfile.windows": "Dev CMD"
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
* If building CEF from sources:
    * Official binaries are built on Ubuntu 14.04 (cmake 2.8.12, g++ 4.8.4) and these instructions apply to that OS
    * For Fedora build dependencies see [Issue #466](https://github.com/cztomczak/cefpython/issues/466#issuecomment-419794341)
    * Download [ninja](https://github.com/ninja-build/ninja/releases) 1.7.1 or later
      and copy it to /usr/bin and chmod 755.
    * Install/upgrade required packages using one of the four methods below
      (these packages should be upgraded each time you update to newer CEF):
        1. For 64-bit build, type this command: `sudo apt-get install bison build-essential cdbs curl devscripts dpkg-dev elfutils fakeroot flex g++ git-core git-svn gperf libapache2-mod-php5 libasound2-dev libav-tools libbrlapi-dev libbz2-dev libcairo2-dev libcap-dev libcups2-dev libcurl4-gnutls-dev libdrm-dev libelf-dev libexif-dev libffi-dev libgconf2-dev libgconf-2-4 libgl1-mesa-dev libglib2.0-dev libglu1-mesa-dev libgnome-keyring-dev libgtk2.0-dev libkrb5-dev libnspr4-dev libnss3-dev libpam0g-dev libpci-dev libpulse-dev libsctp-dev libspeechd-dev libsqlite3-dev libssl-dev libudev-dev libwww-perl libxslt1-dev libxss-dev libxt-dev libxtst-dev mesa-common-dev openbox patch perl php5-cgi pkg-config python python-cherrypy3 python-crypto python-dev python-psutil python-numpy python-opencv python-openssl python-yaml rpm ruby subversion ttf-dejavu-core ttf-indic-fonts ttf-kochi-gothic ttf-kochi-mincho fonts-thai-tlwg wdiff wget zip`
        2. For 32-bit build, type this command: `bison build-essential cdbs curl devscripts dpkg-dev elfutils fakeroot flex g++ git-core git-svn gperf libapache2-mod-php5 libasound2-dev libav-tools libbrlapi-dev libbz2-dev libcairo2-dev libcap-dev libcups2-dev libcurl4-gnutls-dev libdrm-dev libelf-dev libexif-dev libffi-dev libgconf2-dev libgl1-mesa-dev libglib2.0-dev libglu1-mesa-dev libgnome-keyring-dev libgtk2.0-dev libkrb5-dev libnspr4-dev libnss3-dev libpam0g-dev libpci-dev libpulse-dev libsctp-dev libspeechd-dev libsqlite3-dev libssl-dev libudev-dev libwww-perl libxslt1-dev libxss-dev libxt-dev libxtst-dev mesa-common-dev openbox patch perl php5-cgi pkg-config python python-cherrypy3 python-crypto python-dev python-psutil python-numpy python-opencv python-openssl python-yaml rpm ruby subversion ttf-dejavu-core ttf-indic-fonts ttf-kochi-gothic ttf-kochi-mincho fonts-thai-tlwg wdiff wget zip lib32gcc1 lib32stdc++6 libc6-i386 linux-libc-dev:i386 libasound2:i386 libcap2:i386 libelf-dev:i386 libfontconfig1:i386 libgconf-2-4:i386 libglib2.0-0:i386 libgpm2:i386 libgtk2.0-0:i386 libgtk-3-0:i386 libncurses5:i386 libnss3:i386 libpango1.0-0:i386 libssl1.0.0:i386 libtinfo-dev:i386 libxcomposite1:i386 libxcursor1:i386 libxdamage1:i386 libxi6:i386 libxrandr2:i386 libxss1:i386 libxtst6:i386`
        3. See the list of packages on the
           [cef/AutomatedBuildSetup.md](https://bitbucket.org/chromiumembedded/cef/wiki/AutomatedBuildSetup.md#markdown-header-linux-configuration)
            wiki page.
        4. Run the install-build-deps.sh script -
           instructions provided further down on this page.
    * To build on Debian 7 see
      [cef/BuildingOnDebian7.md](https://bitbucket.org/chromiumembedded/cef/wiki/BuildingOnDebian7.md) and
      [cef/#1575](https://bitbucket.org/chromiumembedded/cef/issues/1575),
      and [cef/#1697](https://bitbucket.org/chromiumembedded/cef/issues/1697)
* Building CEF 32-bit is only possible using cross-compiling on
  64-bit machine. See [Issue #328](https://github.com/cztomczak/cefpython/issues/328).
* Sometimes it is also required to install these packages (eg. chroot):
  `sudo apt-get install libnss3 libnspr4 libxss1 libgconf-2-4`


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
* For legacy build scripts, install dependencies with:
  `cd cefpython/tools/ && pip install --upgrade -r requirements.txt`.
  On Linux use `sudo`. You should run it each time you update to newer
  cefpython version to avoid issues.

**Note**: CEFPython uses compiled Cython extensions, so wheels are Python version-specific.
A wheel built for Python 3.12 will not work on Python 3.11 or 3.13. Use the multi-version
build commands to create wheels for all supported Python versions.


## Build using prebuilt CEF binaries and libraries

When cloning repository you should checkout a stable branch which
are named "cefpythonXX" where XX is Chromium version number.

1) Clone cefpython, checkout for example "cefpython57" branch
   that includes Chromium v57, then create a build/ directory and enter it:
```
git clone https://github.com/cztomczak/cefpython.git
cd cefpython/
git checkout cefpython57
mkdir build/
cd build/
```

2) Download binaries and libraries from
   [GH releases](https://github.com/cztomczak/cefpython/tags)
   tagged eg. 'v57-upstream' when building v57. The version
   of the binaries must match exactly the CEF version from
   the "cefpython/src/version/" directory (look for CEF_VERSION
   constant in .h file).

3) Extract the downloaded archive eg. "cef55_3.2883.1553.g80bd606_win32.zip"
   in the "build/" directory (using "extract here" option)

4) Run the build.py tool (xx.x is version number):
```
python ../tools/build.py xx.x
```


## Build using CEF binaries from Spotify Automated Builds

When cloning repository you should checkout a stable branch which
are named "cefpythonXX" where XX is Chromium version number.

1) Clone cefpython, checkout for example "cefpython57" branch
   that includes Chromium v57, then create a build/ directory and enter it:
```
git clone https://github.com/cztomczak/cefpython.git
cd cefpython/
git checkout cefpython57
mkdir build/
cd build/
```

2) Install python dependencies:
```
pip install --upgrade -r ../tools/requirements.txt
````

3) Download CEF binaries from [Spotify Automated Builds](https://cef-builds.spotifycdn.com/index.html).
   The version of the binaries must match exactly the CEF version
   from the "cefpython/src/version/" directory (look for CEF_VERSION
   constant in .h file).

4) Extract the downloaded archive eg.
   "cef_binary_3.2883.1553.g80bd606_windows32.tar.bz2"
   in the build/ directory (using "extract here" option)

5) Run the automate.py tool. After it completes you should see a new
   directory eg. "cef55_3.2883.1553.g80bd606_win32/".
```
python ../tools/automate.py --prebuilt-cef
```

5) Run the build.py tool (xx.x is version number):
```
python ../tools/build.py xx.x
```


## Build upstream CEF from sources


Building CEF from sources is a very long process that can take several
hours depending on your CPU speed and the platform you're building on.
To speed up the process you can pass the --fast-build flag, however
in such case result binaries won't be optimized.
You can optionally set how many parallel ninja jobs to run (by default
cores/2) with the --ninja-jobs flag passed to automate.py.

To build CEF from sources run the automate.py tool using the --build-cef
flag. The automate script will use version information from the
"cefpython/src/version/" directory. If you would like to use
a custom CEF branch
then use the --cef-branch flag, but note that this is only for advanced
users as this will require updating cefpython's C++/Cython code.

You should be fine by running automate.py with the default options,
but if you need to customize the build then use the --help flag to
see more options.

Remember to always upgrade packages listed in Requirements section each
time you update to newer CEF.

On Linux if there are errors about missing packages or others,
then see solutions in the [Possible errors](#possible-errors) section.


The commands below will build CEF from sources with custom CEF Python
patches applied and then build the CEF Python package. "xx.x" is version
number and "ninja-jobs 4" means to run 4 parallel jobs for compiling,
increase it if you have more CPU cores and want things to build faster.

The commands below checkout for example "cefpython57" branch that
includes Chromium v57. When cloning repository you should checkout
a stable branch which are named "cefpythonXX" where XX is Chromium
version number.

```
git clone https://github.com/cztomczak/cefpython.git
cd cefpython/
git checkout cefpython57
mkdir build/
cd build/
python ../tools/automate.py --build-cef --ninja-jobs 4
python ../tools/build.py xx.x
```

The automate.py tool should create eg. "cef55_3.2883.1553.g80bd606_win32/"
directory when it's done. Then the build.py tool will build the cefpython
module, make installer package, install the package and run unit tests
and examples. See the notes for commands for creating package installer
and/or wheel package for distribution.

### Building old unsupported version of Chromium 

When building an old version of Chromium you may get into issues.
For example as of this writing the latest CEF Python version is
v57, but current support Chromium version is v64. Now when building
v57 you may encounter issues since Chromium build tools had
many updates since v57. You have to checkout depot_tools from the
revision when Chromium v57 was released. When running automate.py
tool the depot_tools repository resides in `build_dir/depot_tools/`
directory. If you didn't run automate.py then you can find repository
url in automate-git.py script. For example for v57 release to checkout
an old revision of depot_tools you can use this command:

```
git checkout master@{2017-04-20}
```

After that set `DEPOT_TOOLS_UPDATE=0` environment variable and then
run automate.py tool.

### Possible errors

__Debug_GN_arm/ configuration error (Linux)__: Even though building
on Linux for Linux, Chromium still runs ARM configuration files. If
there is an error showing that pkg-config fails with GTK 3 library
then see solution in the third post in this topic on CEF Forum:
[Debug_GN_arm error when building on Linux, *not* arm](https://magpcss.org/ceforum/viewtopic.php?f=6&t=14976).

__MISSING PACKAGES (Linux)__: After the chromium sources are downloaded,
it will try to build cef projects and if it fails due to missing packages
make sure you've installed all the required packages listed in the
Requirements section further up on this page. If it still fails, you
can fix it by running the install-build-deps.sh script (intended for
Ubuntu systems, but you could edit it). When the "ttf-mscorefonts-installer"
graphical installer pops up don't install it - deny EULA.

```
cd build/chromium/src/build/
chmod 755 install-build-deps.sh
sudo ./install-build-deps.sh --no-chromeos-fonts --no-nacl --no-arm
```

After dependencies are satisifed re-run automate.py.


## Build CEF manually

CEF Python official binaries come with custom CEF binaries with
a few patches applied for our use case, see the Notes section further
down on this page.

On Linux before running any of CEF tools apply the issue73 patch
first.

To build CEF follow the instructions on the Branches and Building
CEF wiki page:
https://bitbucket.org/chromiumembedded/cef/wiki/BranchesAndBuilding

After it is successfully built, apply patches, rebuild and remake
distribs.

Note that CEF patches must be applied in the "download_dir/chromium/src/cef/"
directory, not in the "download_dir/cef/" directory.


## CEF Automated Builds (Spotify and Adobe)

There are two sites that provide automated CEF builds:
* Spotify - http://opensource.spotify.com/cefbuilds/index.html
  * This is the new build system
  * Since June 2016 all builds are without tcmalloc, see
    [cefpython/#73](https://github.com/cztomczak/cefpython/issues/73)
    and [cef/#1827](https://bitbucket.org/chromiumembedded/cef/issues/1827)
* Adobe - https://cefbuilds.com/
  * This is the old build system. Not tested whether it builds without
    tcmalloc.


## Notes

If you would like to update CEF version in cefpython then
see complete instructions provided in
[Issue #264](https://github.com/cztomczak/cefpython/issues/264).

When building for multiple Python versions on Linux/Mac use
pyenv to manage multiple Python installations, see
[Issue #249](https://github.com/cztomczak/cefpython/issues/249)
for details.

Command for making installer package is (xx.x is version number):
```
cd cefpython/build/
python ../tools/make_installer.py xx.x
```

To create a wheel package type:
```
cd cefpython/build/
python ../tools/make_installer.py xx.xx --wheel --universal
cd cefpython3_*/dist/
ls
```

Additional flags when using --wheel flag:
* `--python-tag cp27` to generate Python 2.7 only package
* `--universal` to build package for multiple Python versions
  (in such case you must first build multiple cefpython modules
   for each Python version)

CEF Python binaries are build using similar configuration as described
on the ["Automated Build Setup"](https://bitbucket.org/chromiumembedded/cef/wiki/AutomatedBuildSetup.md#markdown-header-platform-build-configurations) wiki page in upstream CEF. The automate.py tool incorporates most of
of the flags from these configurations.

To build the "libcef_dll_wrapper" library type these commands:
```
cd cef_binary*/
mkdir build
cd build/
cmake -G "Ninja" -DCMAKE_BUILD_TYPE=Release ..
ninja libcef_dll_wrapper
```

To build CEF sample applications type:
```
ninja cefclient cefsimple ceftests
```

Official CEF Python binaries may come with additional patches applied
to CEF/Chromium depending on platform. These patches can be found
in the "cefpython/patches/" directory. Whether you need these patches
depends on your use case, they may not be required and thus you could
use the Spotify Automated Builds. Spotify builds have the issue73 patch
(no tcmalloc) applied.

Currently (February 2017) only Linux releases have the custom
patches applied. Windows and Mac releases use CEF binaries from
Spotify Automated Builds.


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
