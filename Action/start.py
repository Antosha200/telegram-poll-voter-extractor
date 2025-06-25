#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    here       = os.path.dirname(os.path.abspath(__file__))
    model_dir  = os.path.normpath(os.path.join(here, '..', 'Model'))
    session_fp = os.path.join(model_dir, 'poll_session.session')
    start_conn = os.path.join(model_dir, 'startConnect.py')
    get_poll   = os.path.join(model_dir, 'getPoll.py')

    # 1) Если сессии нет — запускаем startConnect.py
    if not os.path.exists(session_fp):
        print("Session not found — connection attempt...")
        try:
            subprocess.run(
                [sys.executable, start_conn],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Connection error: {e}", file=sys.stderr)
            sys.exit(1)

    # 2) Проверяем снова
    if os.path.exists(session_fp):
        # запускаем getPoll.py
        print("Active session, no new connection required")
        try:
            #здесь используем процессы для текущей системы
            #позже процессы будут перенесены по иерархии выше
            subprocess.run(
                [sys.executable, get_poll],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error when receiving the poll: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # если сессии до сих пор нет — фатальная ошибка
        raise FileNotFoundError(
            f"Failed to create a session file: {session_fp}"
        )

if __name__ == '__main__':
    main()
