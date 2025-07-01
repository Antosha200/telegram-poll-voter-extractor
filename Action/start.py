import os
import sys
import subprocess
import argparse

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from Model.Logger.logger import logger

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    session_checker = os.path.join(here, 'check_session.py')
    parser = argparse.ArgumentParser()
    parser.add_argument('--poll_id', type=int, help='ID of the poll in message to fetch')
    args = parser.parse_args()
    try:
        result = subprocess.run(
            [sys.executable, session_checker],
            check=True,
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
        session_fp = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Session setup error: {e}", file=sys.stderr)
        sys.exit(1)

    model_dir  = os.path.normpath(os.path.join(here, '..', 'Model'))
    start_conn = os.path.join(model_dir, 'startConnect.py')
    get_poll   = os.path.join(model_dir, 'getPoll.py')

    #Checking dependencies and installing
    dep_checker = os.path.join(here, 'check_dependencies.py')
    try:
        subprocess.run([sys.executable, dep_checker], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to verify or install dependencies: {e}", file=sys.stderr)
        sys.exit(1)

    # Checking config file and values
    config_checker = os.path.join(here, 'check_config.py')
    try:
        subprocess.run([sys.executable, config_checker], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    # If there is no session, launching startConnect.py and give him the full path.
    if not os.path.exists(session_fp):
        logger.info("Session not found — connection attempt...")
        try:
            subprocess.run(
                [sys.executable, start_conn, session_fp],
                check=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Connection error: {e}", file=sys.stderr)
            sys.exit(1)

    #
    if os.path.exists(session_fp):
        logger.info("Active session, no new connection required")
        try:
            cmd = [sys.executable, get_poll]
            if args.poll_id:
                cmd.extend(['--poll_id', str(args.poll_id)])

            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error when receiving the poll: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # if there is still no session -> fatal error
        raise FileNotFoundError(
            f"Failed to create a session file: {session_fp}"
        )

if __name__ == '__main__':
    main()
