import os
import json
import sys

def load_config():
    here = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.normpath(os.path.join(here, '..'))
    cfg_path = os.path.join(root_dir, 'config.json')
    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Cannot load config.json: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    config = load_config()
    session_name = config.get('session_name')
    if not session_name:
        print("❌ 'session_name' not set in config.json", file=sys.stderr)
        sys.exit(1)

    here = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.normpath(os.path.join(here, '..'))
    session_dir = os.path.join(root_dir, 'Session')

    if not os.path.isdir(session_dir):
        print(f"📁 Session directory doesn’t exist, creating: {session_dir}", file=sys.stderr)
        try:
            os.makedirs(session_dir, exist_ok=True)
            print(f"✅ Created directory {session_dir}", file=sys.stderr)
        except Exception as e:
            print(f"❌ Failed to create session directory: {e}", file=sys.stderr)
            sys.exit(1)

    session_fp = os.path.join(session_dir, f"{session_name}.session")
    print(session_fp)

if __name__ == '__main__':
    main()
