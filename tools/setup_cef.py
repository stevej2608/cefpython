#!/usr/bin/env python3
"""Download and setup CEF binaries if not present."""

import os
import sys
import platform
import subprocess
import urllib.request
import tarfile
import shutil

CEF_VERSION = "123.0.7+g6a21509+chromium-123.0.6312.46"

def get_platform_info():
    """Detect the current platform and return OS_POSTFIX2 and CEF_POSTFIX2."""
    system = platform.system()
    if system == "Linux":
        return "linux64", "linux64"
    elif system == "Darwin":
        return "mac64", "macosx64"
    elif system == "Windows":
        return "win64", "windows64"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

def main():
    print("Starting CEF setup...")

    OS_POSTFIX2, CEF_POSTFIX2 = get_platform_info()
    print(f"Platform: {OS_POSTFIX2}")

    CEF_DIR = f"cef123_{CEF_VERSION}_{OS_POSTFIX2}"
    CEF_DOWNLOAD_NAME = f"cef_binary_{CEF_VERSION}_{CEF_POSTFIX2}"
    CEF_URL = f"https://cef-builds.spotifycdn.com/{CEF_DOWNLOAD_NAME}.tar.bz2"

    build_dir = "build"
    cef_path = os.path.join(build_dir, CEF_DIR)

    if not os.path.exists(cef_path):
        print(f"CEF binaries not found. Downloading from {CEF_URL}...")
        print("This will download approximately 5.8GB. Please be patient...")

        os.makedirs(build_dir, exist_ok=True)

        # Download
        tar_path = os.path.join(build_dir, "cef_binary.tar.bz2")
        print("Downloading...")
        urllib.request.urlretrieve(CEF_URL, tar_path)

        # Extract
        print("Extracting CEF binaries...")
        os.chdir(build_dir)
        with tarfile.open("cef_binary.tar.bz2", "r:bz2") as tar:
            tar.extractall()

        # Rename
        os.rename(CEF_DOWNLOAD_NAME, CEF_DIR)

        # Clean up
        os.chdir("..")
        if os.path.exists("cef_binary.tar.bz2"):
            os.remove("cef_binary.tar.bz2")

        print(f"CEF binaries downloaded: {CEF_DIR}")
    else:
        print(f"CEF binaries already present: {cef_path}")

    # Ensure wrapper library is built and in the right place
    os.chdir(cef_path)

    # Check if wrapper library exists
    wrapper_lib_path = None
    if CEF_POSTFIX2 == "windows64":
        wrapper_lib_path = os.path.join("lib", "libcef_dll_wrapper_MD.lib")
    else:
        wrapper_lib_path = os.path.join("lib", "libcef_dll_wrapper.a")

    if not os.path.exists(wrapper_lib_path):
        print("Building libcef_dll_wrapper...")
        build_path = "build"
        os.makedirs(build_path, exist_ok=True)

        # Store current directory to return to it
        cef_root = os.getcwd()
        os.chdir(build_path)

        if CEF_POSTFIX2 == "windows64":
            # Try Visual Studio generators first, then Ninja as fallback
            cmake_success = False
            build_config = None

            # Try Visual Studio generators (more reliable on Windows)
            for generator in ["Visual Studio 17 2022", "Visual Studio 16 2019"]:
                try:
                    print(f"Trying CMake with {generator}...")
                    subprocess.run(["cmake", "..", "-G", generator, "-A", "x64"], check=True)
                    cmake_success = True
                    build_config = "vs"
                    print(f"Successfully configured with {generator}")
                    break
                except subprocess.CalledProcessError:
                    # Clean up before trying next generator
                    if os.path.exists("CMakeCache.txt"):
                        os.remove("CMakeCache.txt")
                    if os.path.exists("CMakeFiles"):
                        shutil.rmtree("CMakeFiles")
                    continue

            # If VS generators failed, try Ninja with explicit MSVC compiler
            if not cmake_success:
                try:
                    print("Trying CMake with Ninja generator...")
                    # Explicitly set compilers to avoid picking up MinGW
                    subprocess.run([
                        "cmake", "..", "-G", "Ninja",
                        "-DCMAKE_BUILD_TYPE=Release",
                        "-DCEF_RUNTIME_LIBRARY_FLAG=/MD",
                        "-DCMAKE_C_COMPILER=cl.exe",
                        "-DCMAKE_CXX_COMPILER=cl.exe"
                    ], check=True, capture_output=True)
                    cmake_success = True
                    build_config = "ninja"
                    print("Successfully configured with Ninja")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    if os.path.exists("CMakeCache.txt"):
                        os.remove("CMakeCache.txt")
                    if os.path.exists("CMakeFiles"):
                        shutil.rmtree("CMakeFiles")

            if not cmake_success:
                print("\nERROR: Could not configure CMake.")
                print("Please ensure one of the following:")
                print("  1. Install Visual Studio 2019 or 2022 (Community Edition)")
                print("  2. Run from Visual Studio Developer Command Prompt/PowerShell with Ninja installed")
                sys.exit(1)

            # Build based on which configuration succeeded
            if build_config == "vs":
                subprocess.run(["cmake", "--build", ".", "--config", "Release", "--target", "libcef_dll_wrapper"], check=True)
            else:  # ninja
                subprocess.run(["ninja", "libcef_dll_wrapper"], check=True)
        else:
            # Linux/Mac: use Ninja
            subprocess.run(["cmake", "..", "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Release"], check=True)
            subprocess.run(["ninja", "libcef_dll_wrapper"], check=True)

        # Return to CEF root
        os.chdir(cef_root)

        # Create lib directory
        os.makedirs("lib", exist_ok=True)

        # Copy wrapper library to lib directory
        if CEF_POSTFIX2 == "windows64":
            # Try Ninja output location first, then VS generator location
            built_lib_ninja = os.path.join("build", "libcef_dll_wrapper", "libcef_dll_wrapper.lib")
            built_lib_vs = os.path.join("build", "libcef_dll_wrapper", "Release", "libcef_dll_wrapper.lib")

            built_lib = None
            if os.path.exists(built_lib_ninja):
                built_lib = built_lib_ninja
            elif os.path.exists(built_lib_vs):
                built_lib = built_lib_vs

            if built_lib:
                shutil.copy2(built_lib, os.path.join("lib", "libcef_dll_wrapper_MD.lib"))
                print(f"Copied wrapper library from {built_lib} to lib/libcef_dll_wrapper_MD.lib")
            else:
                print(f"ERROR: Built library not found at either:")
                print(f"  - {built_lib_ninja} (Ninja build)")
                print(f"  - {built_lib_vs} (VS generator build)")
                sys.exit(1)

            # Also copy libcef.lib from Release to lib directory
            libcef_src = os.path.join("Release", "libcef.lib")
            if os.path.exists(libcef_src):
                shutil.copy2(libcef_src, os.path.join("lib", "libcef.lib"))
                print(f"Copied libcef.lib to lib/")
        else:
            built_lib = os.path.join("build", "libcef_dll_wrapper", "libcef_dll_wrapper.a")
            if os.path.exists(built_lib):
                shutil.copy2(built_lib, os.path.join("lib", "libcef_dll_wrapper.a"))
                print(f"Copied wrapper library to lib/libcef_dll_wrapper.a")
            else:
                print(f"ERROR: Built library not found at {built_lib}")
                sys.exit(1)
    else:
        print(f"Wrapper library already present: {wrapper_lib_path}")

    # Ensure libcef.lib is also in lib directory for Windows
    if CEF_POSTFIX2 == "windows64":
        libcef_lib = os.path.join("lib", "libcef.lib")
        if not os.path.exists(libcef_lib):
            libcef_src = os.path.join("Release", "libcef.lib")
            if os.path.exists(libcef_src):
                os.makedirs("lib", exist_ok=True)
                shutil.copy2(libcef_src, libcef_lib)
                print(f"Copied libcef.lib to lib/")

    # Ensure bin directory exists
    if not os.path.exists("bin"):
        os.makedirs("bin")
        if os.path.exists("Release"):
            for item in os.listdir("Release"):
                src = os.path.join("Release", item)
                dst = os.path.join("bin", item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
        if os.path.exists("Resources"):
            for item in os.listdir("Resources"):
                src = os.path.join("Resources", item)
                dst = os.path.join("bin", item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)

if __name__ == "__main__":
    main()
