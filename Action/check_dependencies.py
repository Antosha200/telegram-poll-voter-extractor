import configparser
import importlib
import subprocess
import sys
import os
from Model.Logger.logger import logger

def load_dependencies(cfg_path):
    config = configparser.ConfigParser()
    config.read(cfg_path)

    if 'dependencies' in config and 'packages' in config['dependencies']:
        return [pkg.strip() for pkg in config['dependencies']['packages'].splitlines() if pkg.strip()]
    else:
        logger.info("No dependencies or packages found in config.")
        return []

def ensure_package_installed(package_name):
    try:
        importlib.import_module(package_name)
        logger.info(f"'{package_name}' is already installed.")
    except ImportError:
        logger.info(f"'{package_name}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        logger.info(f"'{package_name}' installed successfully.")

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    cfg_file = os.path.join(here, "requirements.cfg")

    if not os.path.exists(cfg_file):
        logger.error(f"Configuration file not found: {cfg_file}", file=sys.stderr)
        sys.exit(1)

    packages = load_dependencies(cfg_file)
    for pkg in packages:
        ensure_package_installed(pkg)

if __name__ == "__main__":
    main()
