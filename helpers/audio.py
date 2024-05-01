import logging

from .applescript import run_applescript

logger = logging.getLogger(__name__)

def mute():
    return run_applescript('set volume with output muted')

def unmute():
    return run_applescript('set volume without output muted')

def is_muted():
    out = run_applescript('get volume settings')
    if out:
        if 'output muted:false' in out:
            return False
        elif 'output muted:true' in out:
            return True