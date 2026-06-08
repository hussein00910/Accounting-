"""
Parses raw SMS text from Arab bank messages into structured transaction dicts.
Loads patterns from data/bank_patterns.json at import time.
"""

import re
import json
import os
from datetime import datetime


_PATTERNS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'bank_patterns.json')

# Arabic-Indic digit map
_AR_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

# Generic fallback patterns used when bank-specific pattern fails
_GENERIC_AMOUNT = re.compile(
    r'(?:SAR|AED|USD|KWD|BHD|OMR|QAR|EGP|JOD|ر\.س|ريال|درهم)\s*([\d,]+\.?\d*)'
    r'|([\d,]+\.?\d*)\s*(?:SAR|AED|USD|KWD|BHD|OMR|QAR|EGP|JOD|ر\.س|ريال|درهم)',
    re.IGNORECASE
)
_GENERIC_BALANCE = re.compile(
    r'(?:رصيد|رصيدك|balance|bal)[^\d٠-٩]*([\d,٠-٩]+\.?\d*)',
    re.IGNORECASE
)
_DATE_PATTERN = re.compile(
    r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2})'
)


def _load_bank_configs() -> list:
    try:
        with open(_PATTERNS_PATH, encoding='utf-8') as f:
            return json.load(f)['banks']
    except Exception:
        return []


_BANKS = _load_bank_configs()


def _normalise(text: str) -> str:
    return text.translate(_AR_DIGITS).strip()


def _parse_amount(text: str, pattern: str) -> float | None:
    norm = _normalise(text)
    try:
        m = re.search(pattern, norm, re.IGNORECASE)
        if m:
            raw = (m.group(1) or m.group(2) or '').replace(',', '')
            return float(raw) if raw else None
    except re.error:
        pass
    m = _GENERIC_AMOUNT.search(norm)
    if m:
        raw = (m.group(1) or m.group(2) or '').replace(',', '')
        return float(raw) if raw else None
    return None


def _parse_balance(text: str) -> float | None:
    norm = _normalise(text)
    m = _GENERIC_BALANCE.search(norm)
    if m:
        raw = m.group(1).replace(',', '')
        try:
            return float(raw)
        except ValueError:
            return None
    return None


def _parse_merchant(text: str, pattern: str) -> str:
    try:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()[:60]
    except re.error:
        pass
    return ''


def _parse_date(text: str) -> str:
    m = _DATE_PATTERN.search(_normalise(text))
    if m:
        raw = m.group(1)
        for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%Y-%m-%d',
                    '%d/%m/%y', '%d-%m-%y'):
            try:
                return datetime.strptime(raw, fmt).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _detect_type(text: str, bank: dict) -> str:
    low = text.lower()
    for kw in bank.get('credit_keywords', []):
        if kw.lower() in low:
            return 'credit'
    for kw in bank.get('debit_keywords', []):
        if kw.lower() in low:
            return 'debit'
    return 'debit'


def _match_bank(sender: str) -> dict | None:
    sender_up = (sender or '').upper()
    # Exact match first (highest priority)
    for bank in _BANKS:
        for s in bank.get('senders', []):
            if s.upper() == sender_up:
                return bank
    # Prefix/substring match second (sender starts with bank token or vice versa)
    for bank in _BANKS:
        for s in bank.get('senders', []):
            su = s.upper()
            # Require the token to be at a word boundary to avoid SNB matching EmiratesNBD
            if sender_up.startswith(su) or su.startswith(sender_up):
                return bank
    return None


def parse_sms(body: str, sender: str = '', sms_id: str = '') -> dict | None:
    """Return a transaction dict or None if SMS is not a bank transaction."""
    if not body:
        return None

    bank = _match_bank(sender)

    if bank:
        amount = _parse_amount(body, bank['amount_pattern'])
        tx_type = _detect_type(body, bank)
        merchant = _parse_merchant(body, bank['merchant_pattern'])
        currency = bank['currency']
        bank_id = bank['id']
    else:
        # Generic detection: must contain an amount + transaction keyword
        debit_kw = ['deducted', 'debited', 'purchase', 'خُصم', 'خصم',
                    'تم الشراء', 'مدين', 'سحب', 'pos']
        credit_kw = ['credited', 'deposited', 'إيداع', 'تم إيداع', 'salary']
        low = body.lower()
        has_kw = any(k in low for k in debit_kw + credit_kw)
        if not has_kw:
            return None

        norm = _normalise(body)
        m = _GENERIC_AMOUNT.search(norm)
        if not m:
            return None
        raw = (m.group(1) or m.group(2) or '').replace(',', '')
        try:
            amount = float(raw)
        except ValueError:
            return None

        tx_type = 'credit' if any(k in low for k in credit_kw) else 'debit'
        merchant = ''
        currency = 'SAR'
        bank_id = 'UNKNOWN'

    if not amount or amount <= 0:
        return None

    return {
        'date': _parse_date(body),
        'amount': amount,
        'currency': currency,
        'merchant': merchant,
        'category': 'other',
        'bank_id': bank_id,
        'raw_sms': body[:500],
        'sms_address': sender,
        'type': tx_type,
        'balance_after': _parse_balance(body),
        '_sms_id': sms_id,
    }
