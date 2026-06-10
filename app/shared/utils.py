import os, re, json
from datetime import datetime
from app.shared.constants import TRANSLATIONS_DIR

def slugify(text):
    return re.sub(r'[^a-z0-9_]', '_', text.lower()).strip('_')

def load_translations():
    translations = {}
    for fname in os.listdir(TRANSLATIONS_DIR):
        if fname.endswith(".json"):
            lang = fname.replace(".json", "")
            with open(os.path.join(TRANSLATIONS_DIR, fname), "r", encoding="utf-8") as f:
                translations[lang] = json.load(f)
    return translations

_translations_cache = None

def tr_static(lang, key, **kwargs):
    global _translations_cache
    if _translations_cache is None:
        _translations_cache = load_translations()
    text = _translations_cache.get(lang, {}).get(key) or _translations_cache.get("en", {}).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text

def today_iso():
    return datetime.now().strftime("%Y-%m-%d")

def month_start_iso():
    return datetime.now().strftime("%Y-%m-01")
