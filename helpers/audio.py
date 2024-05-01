import subprocess
import logging

from .applescript import run_applescript

logger = logging.getLogger(__name__)

def mute(method=None, device=None):
    if method == 'applescript' or method is None:
        return run_applescript('set volume with output muted')
    elif method == 'switchaudio':
        return switchaudio_mute(device, 'mute')

def unmute(method=None, device=None):
    if method == 'applescript' or method is None:
        return run_applescript('set volume without output muted')
    elif method == 'switchaudio':
        return switchaudio_mute(device, 'unmute')

def is_muted(method=None):
    out = run_applescript('get volume settings')
    if out:
        if 'output muted:false' in out:
            return False
        elif 'output muted:true' in out:
            return True

def switchaudio_mute(device, muting):
    if device:
        current_device = run_switchaudio('-c')
        if device.strip() != current_device.strip():
            def mute_device(d):
                run_switchaudio('-s', d)
                return run_switchaudio('-m', muting)
            if ',' in device:
                ok = True
                for d in device.split(','):
                    ok = ok and mute_device(d)
                run_switchaudio('-s', current_device)
                return ok
            else:
                mute_device(device)
                run_switchaudio('-s', current_device)
                return ok
    return run_switchaudio('-m', muting)

# https://github.com/deweller/switchaudio-osx
def run_switchaudio(*params):
    result = subprocess.run(['SwitchAudioSource', *params], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        return result.stdout.strip()
    elif result.stderr:
        logger.error(f"Error: {result.stderr}")

    return result.returncode == 0