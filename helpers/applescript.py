import subprocess
import logging

logger = logging.getLogger(__name__)

def run_applescript(script):
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        return result.stdout.strip()
    elif result.stderr:
        logger.error(f"Error: {result.stderr}")

    return result.returncode == 0