import PIL
import PIL.ImageGrab
import tempfile

from .bounds import get_window_bounds, bring_to_front

def fullscreen():
    return PIL.ImageGrab.grab()

def boundingbox(bbox):
    return PIL.ImageGrab.grab(bbox=bbox)

def window(app_name, title_keyword, ensure_front=True):
    if ensure_front:
        if not bring_to_front(app_name, title_keyword):
            return
    bounds = get_window_bounds(app_name, title_keyword)
    if bounds:
        return boundingbox(bounds)

def save_to_temp(img):
    if not img:
        return
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as t:
        img.save(t, 'PNG')
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