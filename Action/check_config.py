import os
import json
import sys
from Model.Logger.logger import logger

REQUIRED_FIELDS = ["api_id", "api_hash", "session_name", "chat_username"]
TEMPLATE = {
    "api_id": "",
    "api_hash": "",
    "session_name": "",
    "chat_username": ""
}

def validate_config(config):
    missing = []
    for field in REQUIRED_FIELDS:
        if field not in config or not config[field]:
            missing.append(field)
    return missing

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.normpath(os.path.join(here, '..'))
    config_path = os.path.join(root_dir, "config.json")

    if not os.path.exists(config_path):
        logger.warning(f"Config file not found. Creating template: {config_path}")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(TEMPLATE, f, indent=2)
        logger.info("Template created. Please fill in the missing fields in config.json.")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse config.json: {e}", file=sys.stderr)
        sys.exit(1)

    missing_fields = validate_config(config)
    if missing_fields:
        logger.error(f"Config is missing required fields or values: {', '.join(missing_fields)}", file=sys.stderr)
        sys.exit(1)

    logger.info("Config loaded and validated.")

if __name__ == "__main__":
    main()
