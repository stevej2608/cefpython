#!/usr/bin/env python3
"""Helper script for Hatch build tasks that need platform detection."""

import os
import platform
import subprocess
import sys


def get_platform():
    """Detect the current platform."""
    system = platform.system()
    if system == "Linux":
        return "linux64"
    elif system == "Darwin":
        return "macosx64"
    elif system == "Windows":
        return "windows64"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def run_bash_script(script_content):
    """Run a bash script on Unix or Git Bash on Windows."""
    system = platform.system()

    if system == "Windows":
        # On Windows, try to use bash from Git Bash
        bash_paths = [
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
            "bash.exe",  # If in PATH
        ]

        bash = None
        for path in bash_paths:
            try:
                subprocess.run([path, "--version"], capture_output=True, check=True)
                bash = path
                break
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue

        if not bash:
            print("Error: bash not found. Please install Git for Windows.", file=sys.stderr)
            sys.exit(1)

        # Run the script with bash
        result = subprocess.run([bash, "-c", script_content], shell=False)
    else:
        # On Unix systems, use bash directly
        result = subprocess.run(["bash", "-c", script_content])

    sys.exit(result.returncode)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: hatch_build_helper.py <command>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "platform":
        print(get_platform())
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
