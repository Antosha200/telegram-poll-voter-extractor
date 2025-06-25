#!/usr/bin/env python3
import sys
from connection import run_test, set_session_path

def usage_and_exit():
    print("Usage: startConnect.py <full-path-to-session-file>", file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    # 1) Проверяем, что нам передали ровно один аргумент
    if len(sys.argv) != 2:
        usage_and_exit()

    # 2) Устанавливаем путь к сессии в connection.py
    set_session_path(sys.argv[1])

    # 3) Запускаем run_test (он уже будет брать наш session_path)
    run_test()
