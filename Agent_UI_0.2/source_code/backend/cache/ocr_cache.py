# from cache.ocr_cache import get_ocr_cache, set_ocr_cache

# ocr_cache.py
ocr_data = {}

def get_ocr_cache(key):
    return ocr_data.get(key)

def set_ocr_cache(key, value):
    ocr_data[key] = value
