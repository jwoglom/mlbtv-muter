import subprocess
import logging

from .applescript import run_applescript

logger = logging.getLogger(__name__)

def mute(method=None, device=None):
    if method == 'applescript' or method is None:
        return run_applescript('set volume with output muted')
    elif method == 'switchaudio':
        return run_switchaudio(device, ['-m', 'mute'])

def unmute(method=None, device=None):
    if method == 'applescript' or method is None:
        return run_applescript('set volume without output muted')
    elif method == 'switchaudio':
        return run_switchaudio(device, ['-m', 'unmute'])

def is_muted(method=None):
    out = run_applescript('get volume settings')
    if out:
        if 'output muted:false' in out:
            return False
        elif 'output muted:true' in out:
            return True


def run_switchaudio(device, args):
    # https://github.com/deweller/switchaudio-osx
    params = []
    if device:
        params += ['-s', device]
    else:
        params += ['-c']
    
    params += args

    result = subprocess.run(['SwitchAudioSource', *params], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        return result.stdout.strip()
    elif result.stderr:
        logger.error(f"Error: {result.stderr}")

    return result.returncode == 0