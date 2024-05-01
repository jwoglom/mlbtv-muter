import subprocess
import logging
import time

from .applescript import run_applescript

logger = logging.getLogger(__name__)

_fallback_mute_state = None

def mute(method=None, device=None):
    global _fallback_mute_state
    _fallback_mute_state = True

    if method == 'applescript' or method is None:
        return run_applescript('set volume with output muted')
    elif method == 'switchaudio':
        return switchaudio_mute(device, 'mute')

def unmute(method=None, device=None):
    global _fallback_mute_state
    _fallback_mute_state = False

    if method == 'applescript' or method is None:
        return run_applescript('set volume without output muted')
    elif method == 'switchaudio':
        return switchaudio_mute(device, 'unmute')

def is_muted(method=None):
    global _fallback_mute_state

    out = run_applescript('get volume settings')
    if out:
        if 'output muted:false' in out:
            return False
        elif 'output muted:true' in out:
            return True
        elif 'output muted:missing' in out and _fallback_mute_state is not None:
            logger.debug('no mute state present in volume settings, falling back on known prior state')
            return _fallback_mute_state

def switchaudio_mute(device, muting):
    if device:
        current_device = run_switchaudio('-c')
        if device.strip() != current_device.strip():
            def mute_device(d):
                run_switchaudio('-s', d)
                time.sleep(0.1)
                return run_switchaudio('-s', d, '-m', muting)
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
    logger.debug(f'SwitchAudioSource %s: %s', ' '.join(params), result.returncode)
    if result.returncode == 0 and result.stdout:
        return result.stdout.strip()
    elif result.stderr:
        logger.error(f"Error: {result.stderr}")

    return result.returncode == 0