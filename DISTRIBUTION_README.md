# CEF Python 123.0 - Linux Distribution Packages

## Package Information

Successfully built Python distribution packages for CEF Python with CEF 123 support on Linux x86_64.

**Build Date**: January 11, 2026
**CEF Version**: 123.0.7+g6a21509+chromium-123.0.6312.46
**Chromium Version**: 123.0.6312.46
**Python Version**: 3.11 (compatible with 3.11-3.14)
**Platform**: Linux x86_64 (manylinux1)

## Available Packages

### 1. Wheel Distribution (Recommended)
**File**: `cefpython3-123.0-py3-none-manylinux1_x86_64.whl`
**Size**: 359 MB
**Location**: `./dist/cefpython3-123.0-py3-none-manylinux1_x86_64.whl`

**Installation**:
```bash
pip install dist/cefpython3-123.0-py3-none-manylinux1_x86_64.whl
```

**Advantages**:
- Fastest installation
- Pre-compiled binary
- All dependencies included
- Ready to use immediately

### 2. Source Distribution
**File**: `cefpython3-123.0.tar.gz`
**Size**: 289 MB
**Location**: `./dist/cefpython3-123.0.tar.gz`

**Installation**:
```bash
pip install dist/cefpython3-123.0.tar.gz
```

**Note**: This is a binary source distribution (includes pre-compiled .so files), not a true source package that compiles during installation.

## Package Contents

The distribution packages include:

### Core Library
- `cefpython_py311.so` (5.8 MB) - Python 3.11 extension module
- `subprocess` (1.4 MB) - CEF subprocess executable
- `__init__.py` - Python package initialization

### CEF Binaries (from Chromium 123)
- `libcef.so` - Main CEF library
- `libEGL.so`, `libGLESv2.so` - Graphics libraries
- `libvulkan.so.1`, `libvk_swiftshader.so` - Vulkan support
- `chrome-sandbox` - Sandbox helper (setuid binary)

### Resources
- `icudtl.dat` - ICU data file
- `v8_context_snapshot.bin` - V8 snapshot
- `snapshot_blob.bin` - V8 snapshot blob
- `chrome_100_percent.pak`, `chrome_200_percent.pak` - UI resources
- `resources.pak` - Additional resources
- `vk_swiftshader_icd.json` - Vulkan ICD manifest

### Locales (54 languages)
Complete set of locale .pak files in `locales/` directory:
- en-US, en-GB, de, fr, es, es-419, ja, zh-CN, zh-TW, ko, etc.

### Examples
- `hello_world.py` - Basic browser example
- `tutorial.py` - Tutorial example
- `tkinter_.py` - Tkinter integration
- `gtk2.py`, `gtk3.py` - GTK integration
- `qt.py` - Qt integration
- `wxpython.py` - wxPython integration
- `pysdl2.py` - PySDL2 integration
- `screenshot.py` - Screenshot example
- `pyinstaller/` - PyInstaller packaging examples
- `snippets/` - Code snippets for common tasks

### Documentation
- `LICENSE.txt` - CEF license
- `README.txt` - Package README
- `License` - CEF Python license

## Installation Instructions

### Quick Install (Recommended)

```bash
# Install from wheel
pip install dist/cefpython3-123.0-py3-none-manylinux1_x86_64.whl
```

### Verify Installation

```python
import cefpython3 as cef
print(f"CEF Python version: {cef.__version__}")
print(f"CEF version: {cef.GetVersion()}")
```

Expected output:
```
CEF Python version: 123.0
CEF version: {'chrome_version': '123.0.6312.46', 'cef_version': '123.0.7+g6a21509+chromium-123.0.6312.46', ...}
```

### Run Examples

```bash
# After installation, examples are in site-packages
python -m cefpython3.examples.hello_world
```

Or copy examples to your project:
```bash
# Examples are included in the wheel at cefpython3/examples/
cp -r /path/to/site-packages/cefpython3/examples/ ./
python examples/hello_world.py
```

## System Requirements

### Runtime Dependencies
- **Python**: 3.11, 3.12, 3.13, or 3.14
- **Operating System**: Linux x86_64 (Ubuntu 20.04+, Debian 10+, or equivalent)
- **GTK**: GTK 2.0 or 3.0 (for GTK examples)
- **Qt**: PyQt4, PyQt5, PySide, or PySide2 (for Qt examples)
- **Display**: X11 display server

### Required System Libraries
```bash
# GTK dependencies (for file dialogs and GTK examples)
sudo apt-get install libgtk2.0-0 libgtk-3-0

# X11 dependencies
sudo apt-get install libx11-6

# Graphics libraries (usually pre-installed)
sudo apt-get install libglib2.0-0 libgobject-2.0-0
```

## Usage Examples

### Minimal Hello World

```python
from cefpython3 import cefpython as cef
import sys

def main():
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    cef.Initialize()
    cef.CreateBrowserSync(url="https://www.google.com", window_title="Hello World")
    cef.MessageLoop()
    cef.Shutdown()

if __name__ == '__main__':
    main()
```

### With Settings

```python
from cefpython3 import cefpython as cef

settings = {
    "debug": False,
    "log_severity": cef.LOGSEVERITY_INFO,
    "log_file": "debug.log",
}

cef.Initialize(settings)
browser = cef.CreateBrowserSync(
    url="https://www.example.com",
    window_title="My Browser"
)
cef.MessageLoop()
cef.Shutdown()
```

## Known Issues

### Resource Path Discovery
CEF 123 removed the `CefOverridePath()` API. If you encounter issues with resource discovery (e.g., `icudtl.dat` not found):

1. **Option 1**: Ensure CEF resources are in the same directory as your executable
2. **Option 2**: Configure paths via settings:
   ```python
   settings = {
       "resources_dir_path": "/path/to/cefpython3/",
       "locales_dir_path": "/path/to/cefpython3/locales/",
   }
   cef.Initialize(settings)
   ```

### SetOsModalLoop
The `cef.SetOsModalLoop()` function is now a no-op (does nothing). Modal loop handling is managed internally by CEF 123. You can safely remove calls to this function.

### Chrome Sandbox
The `chrome-sandbox` binary requires special permissions:
```bash
# Set permissions (may require root)
sudo chown root:root /path/to/cefpython3/chrome-sandbox
sudo chmod 4755 /path/to/cefpython3/chrome-sandbox
```

Alternatively, disable sandbox (not recommended for production):
```python
settings = {
    "no_sandbox": True
}
cef.Initialize(settings)
```

## Distribution Details

### Wheel Metadata
```
Wheel-Version: 1.0
Generator: bdist_wheel
Root-Is-Purelib: false
Tag: py3-none-manylinux1_x86_64
```

### Package Structure
```
cefpython3/
├── __init__.py
├── cefpython_py311.so
├── subprocess
├── libcef.so
├── locales/
│   ├── en-US.pak
│   └── ... (54 locales)
├── examples/
│   ├── hello_world.py
│   ├── tutorial.py
│   └── ...
├── LICENSE.txt
└── README.txt
```

## Upgrading from Previous Versions

### API Changes from CEF 66

If upgrading from CEF Python 66.x:

1. **CefOverridePath removed**: Use settings instead
   ```python
   # Old (removed)
   # cef.CefOverridePath(cef.PK_DIR_EXE, "/path")

   # New
   settings = {"resources_dir_path": "/path"}
   cef.Initialize(settings)
   ```

2. **SetOsModalLoop removed**: Remove calls, it's automatic now
   ```python
   # Old (removed)
   # cef.SetOsModalLoop(True)

   # New - just remove the call
   ```

3. **File dialog API**: Internal changes (transparent to Python API)

4. **C++ standard**: Now requires C++17 (only relevant if building from source)

## Building from Source

If you need to rebuild the package:

```bash
# See CEF123_LINUX_UPGRADE.md for complete build instructions
cd /workspaces/reactpy/cefpython
source .venv/bin/activate
python tools/build.py 123.0 --fast
```

## Support & Resources

- **GitHub**: https://github.com/cztomczak/cefpython
- **Documentation**: See `examples/` directory for usage examples
- **Upgrade Guide**: See `CEF123_LINUX_UPGRADE.md` for API changes

## License

CEF Python is licensed under the BSD 3-Clause License.
CEF (Chromium Embedded Framework) is licensed under the BSD License.
Chromium is licensed under the BSD License and other licenses.

See `LICENSE.txt` for complete license information.

## Package Checksums

Generate checksums for verification:

```bash
# SHA256
sha256sum dist/cefpython3-123.0-py3-none-manylinux1_x86_64.whl
sha256sum dist/cefpython3-123.0.tar.gz

# MD5
md5sum dist/cefpython3-123.0-py3-none-manylinux1_x86_64.whl
md5sum dist/cefpython3-123.0.tar.gz
```

## Next Steps

1. Install the package: `pip install cefpython3-123.0-py3-none-manylinux1_x86_64.whl`
2. Try the hello world example: `python -c "from cefpython3.examples import hello_world; hello_world.main()"`
3. Explore the examples directory
4. Read the API documentation
5. Build your application!

---

**Generated**: January 11, 2026
**Package Version**: 123.0
**Build**: Linux x86_64 - Python 3.11
