#!/usr/bin/env python3
"""
Yahoo Finance CSV Converter - Command Line Interface

This is the main entry point for the command-line interface.
"""
import sys

from src.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
