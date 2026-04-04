#!/usr/bin/env python3
"""Simple syntax check for main.py"""

import py_compile
import sys

try:
    py_compile.compile('main.py', doraise=True)
    print("✓ Syntax check passed!")
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f"✗ Syntax error found:")
    print(e)
    sys.exit(1)
