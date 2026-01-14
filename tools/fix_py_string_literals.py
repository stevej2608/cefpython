#!/usr/bin/env python3
"""
Fix py_string compatibility issues for Cython 3.x.

This script finds and fixes string literal assignments to py_string typed variables
and parameters, which are not allowed in Cython 3.x.
"""

import os
import re
import glob


def fix_file(filepath):
    """Fix py_string literal issues in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    changes = []

    # Pattern 1: Function calls with py_string parameters getting string literals
    # Example: GetSetting("some_string") -> GetSetting(<py_string>"some_string")
    # But we need to be careful not to double-cast

    # First, find all cpdef/cdef functions that take py_string parameters
    func_pattern = r'cp?def\s+\w+\s+(\w+)\s*\([^)]*py_string\s+(\w+)[^)]*\)'
    functions_with_py_string = {}

    for match in re.finditer(func_pattern, content):
        func_name = match.group(1)
        functions_with_py_string[func_name] = True

    # Pattern 2: Direct string literal assignments to py_string variables
    # Example: cdef py_string x = "value" -> cdef py_string x = <py_string>"value"
    pattern2 = r'(cdef\s+py_string\s+\w+\s*=\s*)("(?:[^"\\]|\\.)*")'
    def replace2(match):
        prefix = match.group(1)
        string_lit = match.group(2)
        if '<py_string>' in prefix:
            return match.group(0)  # Already fixed
        changes.append(f"  - Fixed variable initialization: {string_lit}")
        return f'{prefix}<py_string>{string_lit}'

    content = re.sub(pattern2, replace2, content)

    # Pattern 3: Method calls with string literals for known py_string parameters
    # Be more conservative - only fix calls we know about
    for func_name in functions_with_py_string:
        # Match: func_name("string") but not func_name(<py_string>"string")
        pattern3 = rf'{func_name}\s*\(\s*("(?:[^"\\]|\\.)*")'

        def replace3(match):
            string_lit = match.group(1)
            full_match = match.group(0)
            if '<py_string>' in full_match:
                return full_match  # Already fixed
            changes.append(f"  - Fixed call to {func_name}: {string_lit}")
            return f'{func_name}(<py_string>{string_lit}'

        content = re.sub(pattern3, replace3, content)

    # Pattern 4: return "" in cdef py_string functions
    # Example: return "" -> return <py_string>""
    # Find cdef py_string functions
    func_def_pattern = r'cdef\s+py_string\s+(\w+)\s*\([^)]*\):\s*\n((?:.*\n)*?)(?=\ncdef|\ncp?def|$)'

    def fix_returns_in_function(match):
        func_body = match.group(0)
        # Replace return "" with return <py_string>""
        fixed_body = re.sub(
            r'return\s+("")(?!\s*\))',  # Match return "" but not already in cast
            lambda m: f'return <py_string>{m.group(1)}' if '<py_string>' not in func_body[:m.start()] else m.group(0),
            func_body
        )
        return fixed_body

    # This is complex, skip for now

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        if changes:
            print(f"Fixed {filepath}:")
            for change in changes:
                print(change)
        return True
    return False


def main():
    src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')

    print(f"Scanning {src_dir} for py_string issues...")

    pyx_files = glob.glob(os.path.join(src_dir, '*.pyx'))
    pyx_files.extend(glob.glob(os.path.join(src_dir, '**', '*.pyx'), recursive=True))

    total_fixed = 0
    for filepath in pyx_files:
        if fix_file(filepath):
            total_fixed += 1

    print(f"\nFixed {total_fixed} file(s)")


if __name__ == "__main__":
    main()
