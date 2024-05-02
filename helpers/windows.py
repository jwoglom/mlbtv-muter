import subprocess
import logging
import os
import platform

logger = logging.getLogger(__name__)

def is_windows():
    return 'windows' in (platform.system() or '').lower()

def run_nircmd(args):
    bin_folder = os.path.join(os.path.dirname(__file__), 'bin')
    result = subprocess.run(['nircmd.exe', *args], capture_output=True, text=True, cwd=bin_folder)
    if result.returncode == 0 and result.stdout:
        return result.stdout.strip()
    elif result.stderr:
        logger.error(f"Error: {result.stderr}")

    return result.returncode == 0