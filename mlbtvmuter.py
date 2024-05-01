#!/usr/bin/env python3
import time
import logging

from helpers.screenshot import window, save_to_temp
from helpers.bounds import is_front
from helpers.ocr import is_commercial
from helpers.audio import mute, unmute, is_muted

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
    print(f'{commercial=}')

    return commercial

muted_at = None
unmuted_at = None

def should_mute(args):
    global muted_at
    if is_muted() is False:
        logger.info('MUTING AUDIO')
        mute()
        muted_at = time.time()
        return 'mute'
    return 'stay_muted'

def should_unmute(args):
    global unmuted_at
    if is_muted() is True:
        logger.info('UNMUTING AUDIO')
        unmute()
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
        if is_muted() == False:
            return 'stay_unmuted'

        seconds_waiting_unmute += duration
        if seconds_waiting_unmute >= args.unmute_after:
            should_unmute(args)
            return 'unmute'
        else:
            return 'pending_unmute'

if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('--interval', type=int, default=1)
    p.add_argument('--unmute-after', type=int, default=None)
    p.add_argument('--once', action='store_true')
    p.add_argument('--ensure-front', action='store_true')
    p.add_argument('--skip-not-front', action='store_true')
    p.add_argument('--app-name', default='Google Chrome')
    p.add_argument('--title-keyword', default='MLB.TV')
    p.add_argument('--debug', '-d', action='store_true')
    args = p.parse_args()

    if args.debug:
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict if not 'pil' in name.lower()]
        for logger in loggers:
            logger.setLevel(logging.DEBUG)

    if args.once:
        if args.unmute_after is None:
            args.unmute_after = 0
        print(run(args))
    elif args.interval:
        if args.unmute_after is None:
            args.unmute_after = 5

        while True:
            t = time.time()
            r = run(args)
            duration = (time.time() - t)
            logger.info("run: %s (%.2fs)" % (r, duration))

            sleep = max(args.interval - duration, 0)
            logger.debug(f'{duration=} {sleep=}')
            time.sleep(sleep)


    