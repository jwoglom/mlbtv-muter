#!/usr/bin/env python3
import time
import logging

from helpers.screenshot import window, save_to_temp, resize_image
from helpers.bounds import is_front
from helpers.ocr import ocr_windows, ocr_osx, is_commercial
from helpers.audio import mute, unmute, is_muted
from helpers.windows import is_windows

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def detect(args):
    img = window(args.app_name, args.title_keyword, args.ensure_front, args.all_monitors, args.only_monitor, args.only_monitor_if_width_gt)
    if not img:
        logger.warning("could not find window")
        return None
    
    if args.skip_not_front and not args.ensure_front:
        if not is_front(args.app_name, args.title_keyword):
            logger.info("window is not at front, skipping")
            return None
        else:
            logger.info("window is at front")

    if is_windows():
        if args.fast:
            img = resize_image(img)
        text = ocr_windows(img)
    else:
        tmpfile = save_to_temp(img, format='JPEG' if args.jpeg else 'PNG', fast=args.fast, center=args.crop_center)
        logger.debug(f'{tmpfile=}')
        text = ocr_osx(tmpfile)

    logger.debug(f'ocr: {text}')
    commercial = is_commercial(text)
    logger.info(f'{commercial=}')

    return commercial

muted_at = None
unmuted_at = None

def should_mute(args):
    global muted_at
    if is_muted(args) in (False, None):
        logger.info('MUTING AUDIO')
        mute(args)
        muted_at = time.time()
        return 'mute'
    return 'stay_muted'

def should_unmute(args):
    global unmuted_at
    if is_muted(args) in (True, None):
        logger.info('UNMUTING AUDIO')
        unmute(args)
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
loops_waiting_unmute = 0
last_action = None
def run(args):
    global seconds_waiting_unmute, loops_waiting_unmute, last_action

    t = time.time()
    if last_action:
        t = last_action
    a = next_action(args)
    n = time.time()
    duration = n - t
    last_action = n

    if a == 'mute':
        seconds_waiting_unmute = 0
        loops_waiting_unmute = 0
        return should_mute(args)
    elif a == 'unmute':
        seconds_waiting_unmute = 0
        loops_waiting_unmute = 0
        return should_unmute(args)
    elif a == 'maybe_unmute':
        if is_muted(args) == False:
            return 'stay_unmuted'

        seconds_waiting_unmute += duration
        loops_waiting_unmute += 1
        if seconds_waiting_unmute >= args.unmute_after and loops_waiting_unmute >= args.unmute_after_loops:
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
    p.add_argument('--unmute-after-loops', type=int, default=None, help='the interval in loops in which the system audio should be unmuted once detected that a commercial is no longer playing. must be met in addition to --unmute-after seconds if set')
    p.add_argument('--once', action='store_true', help='when set, runs once instead of in a loop')
    p.add_argument('--ensure-front', action='store_true', help='when set, forces the MLB.TV window to the foreground')
    p.add_argument('--skip-not-front', action='store_true', help='when set, ignores checking when the MLB.TV window is not in the foreground')
    p.add_argument('--all-monitors', action='store_true', help='when set, grabs the entire screen including all monitors on windows')
    p.add_argument('--only-monitor', default=None, help='when set, grabs the monitor on the "left" or "right" (naively by halving the entire screen output)')
    p.add_argument('--only-monitor-if-width-gt', default=0, help='when set, only applies --only-monitor if the screen width is greater than this value')
    p.add_argument('--crop-center', default=None, help='when set, crops the image which is OCRd to only the center')
    p.add_argument('--fast', '-f', action='store_true', help='make image smaller before OCR step')
    p.add_argument('--jpeg', '-j', action='store_true', help='use JPEG instead of PNG')
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
        if args.unmute_after_loops is None:
            args.unmute_after_loops = 0
        print(run(args))
    elif args.interval:
        if args.unmute_after is None:
            args.unmute_after = DEFAULT_UNMUTE_AFTER
        if args.unmute_after_loops is None:
            args.unmute_after_loops = 0

        while True:
            t = time.time()
            r = run(args)
            duration = (time.time() - t)
            logger.info("run: %s (%.2fs)" % (r, duration))

            sleep = max(args.interval - duration, 0)
            logger.debug(f'{duration=} {sleep=}')
            time.sleep(sleep)


    