#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    here = os.path.dirname(os.path.abspath(__file__))

    session_checker = os.path.join(here, 'check_session.py')
    try:
        result = subprocess.run(
            [sys.executable, session_checker],
            check=True,
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
        session_fp = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Session setup error: {e}", file=sys.stderr)
        sys.exit(1)

    model_dir  = os.path.normpath(os.path.join(here, '..', 'Model'))
    start_conn = os.path.join(model_dir, 'startConnect.py')
    get_poll   = os.path.join(model_dir, 'getPoll.py')

    #Checking dependencies and installing
    dep_checker = os.path.join(here, 'check_dependencies.py')
    try:
        subprocess.run([sys.executable, dep_checker], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to verify or install dependencies: {e}", file=sys.stderr)
        sys.exit(1)

    # Checking config file and values
    config_checker = os.path.join(here, 'check_config.py')
    try:
        subprocess.run([sys.executable, config_checker], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    # 1) Если сессии нет — запускаем startConnect.py и передаём ему полный путь
    if not os.path.exists(session_fp):
        print("Session not found — connection attempt...")
        try:
            subprocess.run(
                [sys.executable, start_conn, session_fp],
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
