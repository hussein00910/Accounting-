"""
Rule-based transaction categorizer.
Loads category keywords from data/categories.json.
"""

import json
import os
import re

_CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'categories.json')


def _load_categories() -> list:
    try:
        with open(_CATEGORIES_PATH, encoding='utf-8') as f:
            return json.load(f)['categories']
    except Exception:
        return []


_CATEGORIES = _load_categories()

_RULES: list[tuple[str, list[re.Pattern]]] = []

for _cat in _CATEGORIES:
    if _cat['id'] == 'other':
        continue
    patterns = [re.compile(re.escape(kw), re.IGNORECASE) for kw in _cat['keywords'] if kw]
    _RULES.append((_cat['id'], patterns))


def categorize(merchant: str, raw_sms: str = '') -> str:
    text = (merchant + ' ' + raw_sms).strip()
    if not text:
        return 'other'
    for cat_id, patterns in _RULES:
        for p in patterns:
            if p.search(text):
                return cat_id
    return 'other'


def get_category_meta(cat_id: str) -> dict:
    for cat in _CATEGORIES:
        if cat['id'] == cat_id:
            return cat
    return {'id': 'other', 'name': 'أخرى', 'name_en': 'Other',
            'icon': 'dots-horizontal', 'color': '#B2BEC3'}


def all_categories() -> list:
    return _CATEGORIES
