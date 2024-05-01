import logging

from .applescript import run_applescript

logger = logging.getLogger(__name__)

def get_window_bounds(app_name, title_keyword):
    script = f"""
    tell application "System Events"
        tell application process "{app_name}"
            set frontWindow to the first window whose name contains "{title_keyword}"
            set boundsVar to frontWindow's position & frontWindow's size
            return boundsVar
        end tell
    end tell
    """
    bounds = run_applescript(script)
    if bounds:
        bounds = tuple(map(int, bounds.split(', ')))
        # if the screen is partially off the screen, and is in the negative dimension,
        # this causes the output to be warped unless we remove the un-rendered part
        # which is not part of the displayable screen area. this only seems to be
        # a problem when the X or Y dimension is negative.
        if bounds[0] < 0: # to left of screen, remove width
            return (0, bounds[1], bounds[2] + bounds[0], bounds[3])
        if bounds[1] < 0: # above screen, remove height
            return (bounds[0], 0, bounds[2], bounds[3] + bounds[1])
        if bounds[2] < 0 or bounds[3] < 0:
            logger.warn(f"invalid {bounds=}")
            return None
        return bounds


def is_front(app_name, title_keyword):
    ret = run_applescript(f"""
    tell application "System Events"
        set isFrontmost to the frontmost of the first process whose name is "{app_name}" and front window's name contains "{title_keyword}"
        return isFrontmost
    end tell
    """)

    return ret == 'true'

def bring_to_front(app_name, title_keyword):
    return run_applescript(f"""
    tell application "{app_name}"
        activate
        repeat with win in windows
            if name of win contains "{title_keyword}" then
                set index of win to 1 -- This makes the window the primary window
                exit repeat
            end if
        end repeat
    end tell
    """)


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('action')
    p.add_argument('--app-name')
    p.add_argument('--title-keyword')
    args = p.parse_args()

    if args.action == 'get_window_bounds':
        print(get_window_bounds(args.app_name, args.title_keyword))
    elif args.action == 'bring_to_front':
        print(bring_to_front(args.app_name, args.title_keyword))
    elif args.action == 'is_front':
        print(is_front(args.app_name, args.title_keyword))