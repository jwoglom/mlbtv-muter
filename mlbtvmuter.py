#!/usr/bin/env python3
import time
import logging

from helpers.screenshot import window, save_to_temp
from helpers.bounds import is_front
from helpers.ocr import is_commercial
from helpers.audio import mute, unmute, is_muted
from helpers.windows import is_windows

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def detect(args):
    w = window(args.app_name, args.title_keyword, args.ensure_front)
    if not w:
        logger.warning("could not find window")
        return None
    
    if args.skip_not_front and not args.ensure_front:
        if not is_front(args.app_name, args.title_keyword):
            logger.info("window is not at front, skipping")
            return None
        else:
            logger.info("window is at front")

    tmpfile = save_to_temp(w)
    logger.debug(f'{tmpfile=}')
    commercial = is_commercial(tmpfile)
    logger.info(f'{commercial=}')

    return commercial

muted_at = None
unmuted_at = None

def should_mute(args):
    global muted_at
    if is_muted(args.audio_method) in (False, None):
        logger.info('MUTING AUDIO')
        mute(args.audio_method, args.audio_device)
        muted_at = time.time()
        return 'mute'
    return 'stay_muted'

def should_unmute(args):
    global unmuted_at
    if is_muted(args.audio_method) in (True, None):
        logger.info('UNMUTING AUDIO')
        unmute(args.audio_method, args.audio_device)
        unmuted_at = time.time()
        return 'unmute'
    return 'stay_unmuted'


def next_action(args):
    d = detect(args)
    if d is True:
        return 'mute'
    elif d is False:
        if args.once:
            return 'unmute'
        return 'maybe_unmute'
    return d

seconds_waiting_unmute = 0
last_action = None
def run(args):
    global seconds_waiting_unmute, last_action

    t = time.time()
    if last_action:
        t = last_action
    a = next_action(args)
    n = time.time()
    duration = n - t
    last_action = n

    if a == 'mute':
        seconds_waiting_unmute = 0
        return should_mute(args)
    elif a == 'unmute':
        seconds_waiting_unmute = 0
        return should_unmute(args)
    elif a == 'maybe_unmute':
        if is_muted(args.audio_method) == False:
            return 'stay_unmuted'

        seconds_waiting_unmute += duration
        if seconds_waiting_unmute >= args.unmute_after:
            should_unmute(args)
            return 'unmute'
        else:
            return 'pending_unmute'

DEFAULT_UNMUTE_AFTER = 3
DEFAULT_APP_NAME = 'Google Chrome'
DEFAULT_TITLE_KEYWORD = "MLB.TV Web Player"
if __name__ == '__main__':
    import argparse

    default_audio_method = 'applescript'
    if is_windows():
        default_audio_method = 'windows'

    p = argparse.ArgumentParser(description='Automatically mute the system audio when commercials are playing on MLB.TV')
    p.add_argument('--interval', type=float, default=1, help='the interval in seconds in which the window status is checked')
    p.add_argument('--unmute-after', type=float, default=None, help='the interval in seconds in which the system audio should be unmuted once detected that a commercial is no longer playing')
    p.add_argument('--once', action='store_true', help='when set, runs once instead of in a loop')
    p.add_argument('--ensure-front', action='store_true', help='when set, forces the MLB.TV window to the foreground')
    p.add_argument('--skip-not-front', action='store_true', help='when set, ignores checking when the MLB.TV window is not in the foreground')
    p.add_argument('--app-name', default=DEFAULT_APP_NAME, help='the MacOS application name which contains the MLB.TV window. default: "%s"' % DEFAULT_APP_NAME)
    p.add_argument('--title-keyword', default=DEFAULT_TITLE_KEYWORD, help='a substring of the MacOS window name to check the status of. default: "%s"' % DEFAULT_TITLE_KEYWORD)
    p.add_argument('--audio-method', default=None, help='advanced: overrides the method of muting the audio. one of "applescript", "switchaudio", or "windows". default: "%s"' % default_audio_method)
    p.add_argument('--audio-device', default=None, help='advanced: custom audio device to control instead of the default system speaker device when using switchaudio mode')
    p.add_argument('--debug', '-d', action='store_true', help='advanced: enable debug logging')
    args = p.parse_args()

    if args.debug:
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict if not 'pil' in name.lower()]
        for logger in loggers:
            logger.setLevel(logging.DEBUG)

    if args.audio_method is None:
        args.audio_method = default_audio_method

    if args.once:
        if args.unmute_after is None:
            args.unmute_after = 0
        print(run(args))
    elif args.interval:
        if args.unmute_after is None:
            args.unmute_after = DEFAULT_UNMUTE_AFTER

        while True:
            t = time.time()
            r = run(args)
            duration = (time.time() - t)
            logger.info("run: %s (%.2fs)" % (r, duration))

            sleep = max(args.interval - duration, 0)
            logger.debug(f'{duration=} {sleep=}')
            time.sleep(sleep)


    