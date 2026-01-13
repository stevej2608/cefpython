#!/usr/bin/env python3
"""Build wheel package for cefpython3."""

import os
import sys
import platform
import subprocess
import shutil
import glob


def get_platform_info():
    """Detect the current platform."""
    system = platform.system()
    if system == "Linux":
        return "linux64", True
    elif system == "Darwin":
        return "mac64", True
    elif system == "Windows":
        return "win64", False
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def strip_binaries(platform_name, setup_dir):
    """Strip debug symbols from binaries to reduce package size."""
    if platform_name == "linux64":
        print("Stripping debug symbols from binaries to reduce package size...")
        binaries = [
            "cefpython3/lib*.so*",
            "cefpython3/subprocess",
            "cefpython3/chrome-sandbox",
        ]
        for pattern in binaries:
            for binary in glob.glob(os.path.join(setup_dir, pattern)):
                try:
                    subprocess.run(["strip", "--strip-unneeded", binary], check=False)
                except Exception as e:
                    print(f"Warning: Failed to strip {binary}: {e}")

        # Show libcef.so size
        libcef = os.path.join(setup_dir, "cefpython3/libcef.so")
        if os.path.exists(libcef):
            size = os.path.getsize(libcef) / (1024 * 1024)
            print(f"libcef.so size: {size:.1f} MB")

    elif platform_name == "mac64":
        print("Stripping debug symbols from binaries to reduce package size...")
        binaries = glob.glob(os.path.join(setup_dir, "cefpython3/*.so"))
        binaries.extend(glob.glob(os.path.join(setup_dir, "cefpython3/*.dylib")))
        for binary in binaries:
            try:
                subprocess.run(["strip", "-x", binary], check=False)
            except Exception as e:
                print(f"Warning: Failed to strip {binary}: {e}")

    print("Stripped binaries. Package size should be significantly reduced.")


def main():
    print("Building wheel package...")

    platform_name, has_strip = get_platform_info()
    print(f"Platform: {platform_name}")

    # Get Python tag
    pytag = f"cp{sys.version_info.major}{sys.version_info.minor}"
    print(f"Python tag: {pytag}")

    # Setup directory
    setup_dir = f"build/cefpython3_123.0_{platform_name}"

    if not os.path.exists(setup_dir):
        print(f"ERROR: Setup directory not found: {setup_dir}")
        print("Make sure to run build.py first to generate the package structure")
        sys.exit(1)

    print(f"Building wheel for platform: {platform_name} with Python tag: {pytag}")

    # Run make_installer.py to prepare the package
    print("Running make_installer.py...")
    subprocess.run([sys.executable, "tools/make_installer.py", "123.0"], check=True)

    # Change to setup directory
    print(f"Changing to setup directory: {setup_dir}")
    os.chdir(setup_dir)

    # Strip binaries if supported
    if has_strip:
        strip_binaries(platform_name, ".")

    # Build wheel
    print("Building wheel with setup.py...")
    subprocess.run([sys.executable, "setup.py", "bdist_wheel"], check=True)

    # Copy wheel to dist/
    print("Copying wheel to dist/...")
    dist_dir = os.path.join("..", "..", "dist")
    os.makedirs(dist_dir, exist_ok=True)

    for wheel in glob.glob("dist/*.whl"):
        shutil.copy(wheel, dist_dir)
        print(f"Copied: {wheel} -> {dist_dir}")

    os.chdir("../..")
    print("Wheel created successfully in dist/")


if __name__ == "__main__":
    main()
