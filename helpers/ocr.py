import logging
from difflib import SequenceMatcher

from .windows import is_windows

logger = logging.getLogger(__name__)

def ocr_osx(path):
    try:
        from ocrmac import ocrmac
        return ocrmac.OCR(path, language_preference=['en-US'], recognition_level='fast').recognize()
    except AttributeError:
        # catalina doesn't support language_preference ('VNRecognizeTextRequest' object has no attribute' supportedRecognitionLanguagesAndReturnError_')
        return ocrmac.OCR(path, recognition_level='fast').recognize()

def ocr_windows(path):
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    raw = pytesseract.image_to_string(path)
    logger.info(f'raw tesseract OCR: {raw=}')

    return sequenceize(raw)

def sequenceize(raw, ns=None):
    words = (raw or '').split()
    seqs = []
    if ns is None:
        ns = [2, 3, 4]
    for n in ns:
        if len(words) <= n:
            seqs.append((' '.join(words),))
        else:
            for i in range(n,1+len(words)):
                seq = words[i-n:i]
                seqs.append((' '.join(seq),))
    return seqs
        

def similar(a, b, thresh):
    if abs(len(b)-len(a)) > 10:
        return False
    sim = SequenceMatcher(None, a, b).ratio()
    if sim > thresh:
        return True
    return False

def is_commercial(path):
    if is_windows():
        ret = ocr_windows(path)
    else:
        ret = ocr_osx(path)
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