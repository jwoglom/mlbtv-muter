import PIL
import PIL.Image
import PIL.ImageGrab
import tempfile
import logging

from .bounds import get_window_bounds, bring_to_front
from .windows import is_windows

logger = logging.getLogger(__name__)

def fullscreen():
    return PIL.ImageGrab.grab()

def boundingbox(bbox):
    return PIL.ImageGrab.grab(bbox=bbox)

def window(app_name, title_keyword, ensure_front=True):
    if is_windows(): # window-specific grabbing not supported
        return fullscreen()

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
        return fullscreen()
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