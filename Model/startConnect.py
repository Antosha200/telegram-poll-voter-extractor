#!/usr/bin/env python3
import sys
from connection import run_test, set_session_path

def usage_and_exit():
    print("Usage: startConnect.py <full-path-to-session-file>", file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage_and_exit()

    set_session_path(sys.argv[1])

    run_test()
