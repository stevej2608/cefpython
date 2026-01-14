#!/usr/bin/env python3
"""
Prepare build environments for all Python versions.

This script pre-creates all Hatch build-matrix environments to validate
that all required Python versions are available before starting builds.
"""

import subprocess
import sys
import json


def main():
    print("Checking available build environments...")

    # Get environment information
    result = subprocess.run(
        ["hatch", "env", "show", "--json"],
        capture_output=True,
        text=True,
        check=True
    )

    envs = json.loads(result.stdout)

    # Find all build-matrix environments
    build_envs = [
        name for name in envs.keys()
        if name.startswith("build-matrix.")
    ]

    if not build_envs:
        print("ERROR: No build-matrix environments found in pyproject.toml")
        sys.exit(1)

    print(f"Found {len(build_envs)} build environments:")
    for env in build_envs:
        py_version = env.split(".")[-1]  # e.g., py3.11 -> 3.11
        print(f"  - {env} (Python {py_version})")

    print("\nCreating environments...")

    failed = []
    for env in build_envs:
        print(f"\nCreating {env}...", end=" ")
        try:
            subprocess.run(
                ["hatch", "env", "create", env],
                check=True,
                capture_output=True
            )
            print("✓")
        except subprocess.CalledProcessError as e:
            print("✗")
            failed.append(env)
            print(f"  ERROR: {e.stderr.decode() if e.stderr else 'Unknown error'}")

    print("\n" + "="*60)
    if failed:
        print(f"FAILED: {len(failed)} environments could not be created:")
        for env in failed:
            print(f"  - {env}")
        print("\nPlease install missing Python versions and try again.")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {len(build_envs)} environments are ready!")
        print("\nYou can now run:")
        print("  hatch run build-matrix:wheel --all")


if __name__ == "__main__":
    main()
