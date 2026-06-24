#!/usr/bin/env python3
"""Recursive syntax check for all .py files in the project"""

import py_compile
import sys
import os

def main():
    errors = 0
    for root, _, files in os.walk('.'):
        if '.venv' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    py_compile.compile(filepath, doraise=True)
                except py_compile.PyCompileError as e:
                    print(f"✗ Syntax error found in {filepath}:")
                    print(e)
                    errors += 1
    
    if errors == 0:
        print("✓ Syntax check passed for all files!")
        sys.exit(0)
    else:
        print(f"✗ Found {errors} syntax error(s).")
        sys.exit(1)

if __name__ == '__main__':
    main()
