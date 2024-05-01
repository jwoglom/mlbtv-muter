import logging
from ocrmac import ocrmac
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

def ocr(path):
    try:
        return ocrmac.OCR(path, language_preference=['en-US'], recognition_level='fast').recognize()
    except AttributeError:
        # catalina doesn't support language_preference ('VNRecognizeTextRequest' object has no attribute' supportedRecognitionLanguagesAndReturnError_')
        return ocrmac.OCR(path, recognition_level='fast').recognize()


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
    return is_commercial_text(ret)

def is_commercial_text(ret):
    texts = [
        'commercial break in progress',
        'commercial break',
        'break in progress'
    ]
    for text in texts:
        if any(text in i[0].lower() for i in ret):
            return True

    THRESH = 0.85
    for text in texts:
        if any(similar(i[0].lower(), text, THRESH) for i in ret):
            return True
    return False