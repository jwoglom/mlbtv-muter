import PIL
import PIL.Image
import PIL.ImageGrab
import tempfile
import logging

from .bounds import get_window_bounds, bring_to_front
from .windows import is_windows

logger = logging.getLogger(__name__)

def fullscreen(**kwargs):
    return PIL.ImageGrab.grab(**kwargs)

def fullscreen_all_monitors():
    return fullscreen(bbox=None, include_layered_windows=False, all_screens=True)

def split_only_monitor(image, half, if_width_gt=None):
    w, h = image.size

    if not if_width_gt or w > float(if_width_gt):
        if half == 'left':
            return image.crop((0, 0, int(w/2), h))
        elif half == 'right':
            return image.crop((int(w/2), 0, w, h))
    return image

def boundingbox(bbox):
    return PIL.ImageGrab.grab(bbox=bbox)

def window(app_name, title_keyword, ensure_front=True, all_monitors=False, only_monitor=None, only_monitor_if_width_gt=None):
    def _fullscreen():
        if only_monitor:
            return split_only_monitor(fullscreen_all_monitors(), only_monitor, only_monitor_if_width_gt)
        if all_monitors:
            return fullscreen_all_monitors()
        return fullscreen()
    if is_windows(): # window-specific grabbing not supported
        return _fullscreen()

    if all_monitors or only_monitor:
        return _fullscreen()

    if ensure_front:
        if not bring_to_front(app_name, title_keyword):
            return
    bounds = get_window_bounds(app_name, title_keyword)
    logger.debug(f'{bounds=}')
    if bounds:
        try:
            return boundingbox(bounds)
        except Exception as e:
            logger.error(f"boundingbox capture: {e=}")
    try:
        return _fullscreen()
    except Exception as e:
        logger.error(f"fullscreen capture: {e=}")

def resize_image(img):
    w, h = img.size
    return img.resize((int(w / 2), int(h / 2))).convert('RGB')

def save_to_temp(img, format='PNG', fast=False):
    if not img:
        return
    with tempfile.NamedTemporaryFile(suffix='.%s' % format.lower(), delete=False) as t:
        if fast:
            img = resize_image(img)
        img.save(t, format)
        return t.name

# python3 -m helpers.screenshot
if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('action')
    p.add_argument('--app-name')
    p.add_argument('--title-keyword')
    args = p.parse_args()

    if args.action == 'window':
        print(save_to_temp(window(args.app_name, args.title_keyword)))
    elif args.action == 'fullscreen':
        print(save_to_temp(fullscreen()))
    elif args.action == 'fullscreen_all_monitors':
        print(save_to_temp(fullscreen_all_monitors()))
    elif args.action == 'left':
        print(save_to_temp(split_only_monitor(fullscreen_all_monitors(), 'left')))
    elif args.action == 'right':
        print(save_to_temp(split_only_monitor(fullscreen_all_monitors(), 'right')))