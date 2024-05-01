import logging
from ocrmac import ocrmac
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

def ocr(path):
    return ocrmac.OCR(path, language_preference=['en-US'], recognition_level='fast').recognize()


def similar(a, b, thresh):
    if abs(len(b)-len(a)) > 10:
        return False
    sim = SequenceMatcher(None, a, b).ratio()
    if sim > thresh:
        return True
    return False

def is_commercial(path):
    ret = ocr(path)
    logger.debug(f'ocr: {ret}')
    if any('commercial break' in i[0].lower() for i in ret):
        return True
    if any('break in progress' in i[0].lower() for i in ret):
        return True
    TEXT = 'commercial break in progress'
    THRESH = 0.9
    if any(similar(i[0].lower(), TEXT, THRESH) for i in ret):
        return True
    return False