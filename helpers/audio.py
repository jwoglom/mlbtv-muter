import subprocess
import logging
import time

from .applescript import run_applescript
from .windows import run_svcl

logger = logging.getLogger(__name__)

_fallback_mute_state = None

def mute(args):
    global _fallback_mute_state
    _fallback_mute_state = True

    method = args.audio_method
    device = args.audio_device

    if method == 'applescript' or method is None:
        return run_applescript('set volume with output muted')
    elif method == 'windows':
        return run_svcl('/Mute', args.app_name)
    elif method == 'switchaudio':
        return switchaudio_mute(device, 'mute')

def unmute(args):
    global _fallback_mute_state
    _fallback_mute_state = False

    method = args.audio_method
    device = args.audio_device

    if method == 'applescript' or method is None:
        return run_applescript('set volume without output muted')
    elif method == 'windows':
        return run_svcl('/Unmute', args.app_name)
    elif method == 'switchaudio':
        return switchaudio_mute(device, 'unmute')

def is_muted(args):
    global _fallback_mute_state

    method = args.audio_method

    if method == 'applescript' or method is None:
        out = run_applescript('get volume settings')
        if out:
            if 'output muted:false' in out:
                return False
            elif 'output muted:true' in out:
                return True
            elif 'output muted:missing' in out and _fallback_mute_state is not None:
                logger.debug('no mute state present in volume settings, falling back on known prior state')
                return _fallback_mute_state
    elif method == 'windows':
        out = run_svcl('/GetMute', args.app_name, '/Stdout')
        if out:
            out = out.strip()
            return out == 1
        
        logger.debug('no mute state present in svcl volume output, falling back on known prior state')
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