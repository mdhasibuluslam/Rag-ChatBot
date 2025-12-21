import pytesseract, hashlib
from PIL import Image
from cache.ocr_cache import get_ocr_cache, set_ocr_cache

def extract_image_text(path):
    h = hashlib.md5(open(path,'rb').read()).hexdigest()
    cached = get_ocr_cache(h)
    if cached:
        return cached

    text = pytesseract.image_to_string(Image.open(path))
    set_ocr_cache(h, text)
    return text
