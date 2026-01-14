#!/usr/bin/env python3
"""
Top-level build script for cefpython3.

This script orchestrates the complete build process:
1. Setup CEF binaries (download and build libcef_dll_wrapper)
2. Build C++ libraries and Cython extensions
3. Build wheel package
4. Generate checksums
"""

import os
import sys
import subprocess
import platform


def run_step(name, command):
    """Run a build step and handle errors."""
    print(f"\n{'='*60}")
    print(f"STEP: {name}")
    print(f"{'='*60}\n")

    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"\nERROR: Step '{name}' failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    print(f"\n✓ Step '{name}' completed successfully\n")


def main():
    print("CEFPython Build System")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    print()

    # Get the project root directory (parent of tools/)
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(tools_dir)
    os.chdir(project_root)

    # Step 1: Setup CEF binaries
    run_step(
        "Setup CEF binaries",
        f"{sys.executable} tools/setup_cef.py"
    )

    # Step 2: Build C++ libraries and Cython extensions
    run_step(
        "Build libraries",
        f"{sys.executable} tools/build_libs_only.py 123.0 --fast"
    )

    # Step 3: Build wheel using Python build module
    run_step(
        "Build wheel",
        f"{sys.executable} -m build --wheel --no-isolation"
    )

    # Step 4: Generate checksums
    run_step(
        "Generate checksums",
        f"{sys.executable} tools/generate_checksums.py"
    )

    print("\n" + "="*60)
    print("BUILD COMPLETE!")
    print("="*60)
    print("\nWheel packages are in the dist/ directory")


if __name__ == "__main__":
    main()
