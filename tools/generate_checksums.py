#!/usr/bin/env python3
"""Generate checksums for wheel packages."""

import hashlib
import os
import glob


def main():
    print("Generating checksums...")

    if not os.path.exists("dist"):
        print("ERROR: dist/ directory not found")
        return

    os.chdir("dist")
    wheels = sorted(glob.glob("*.whl"))

    if not wheels:
        print("WARNING: No wheel files found in dist/")
        return

    print(f"Found {len(wheels)} wheel(s)")

    # Generate SHA256SUMS
    with open("SHA256SUMS", "w") as f:
        for wheel in wheels:
            print(f"  SHA256: {wheel}")
            with open(wheel, "rb") as wf:
                sha256 = hashlib.sha256(wf.read()).hexdigest()
                f.write(f"{sha256}  {wheel}\n")

    # Generate MD5SUMS
    with open("MD5SUMS", "w") as f:
        for wheel in wheels:
            print(f"  MD5: {wheel}")
            with open(wheel, "rb") as wf:
                md5 = hashlib.md5(wf.read()).hexdigest()
                f.write(f"{md5}  {wheel}\n")

    print("\nChecksums generated:")
    print("  - dist/SHA256SUMS")
    print("  - dist/MD5SUMS")


if __name__ == "__main__":
    main()
