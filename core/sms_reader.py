"""
Reads SMS messages from Android ContentResolver via pyjnius.
Falls back to an empty list on non-Android platforms (desktop testing).
"""

import threading
from .sms_parser import parse_sms
from .categorizer import categorize
from .database import Database

_ANDROID = False
try:
    from jnius import autoclass  # type: ignore
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Uri = autoclass('android.net.Uri')
    _ANDROID = True
except Exception:
    pass


def _read_android_sms(limit: int = 500) -> list[dict]:
    """Query Android inbox and return list of raw SMS dicts."""
    msgs = []
    try:
        context = PythonActivity.mActivity
        uri = Uri.parse('content://sms/inbox')
        cursor = context.getContentResolver().query(
            uri, None, None, None, 'date DESC'
        )
        if not cursor:
            return msgs
        idx_id = cursor.getColumnIndex('_id')
        idx_addr = cursor.getColumnIndex('address')
        idx_body = cursor.getColumnIndex('body')
        idx_date = cursor.getColumnIndex('date')
        count = 0
        while cursor.moveToNext() and count < limit:
            msgs.append({
                'id': str(cursor.getString(idx_id)),
                'address': cursor.getString(idx_addr) or '',
                'body': cursor.getString(idx_body) or '',
                'date_ms': cursor.getLong(idx_date),
            })
            count += 1
        cursor.close()
    except Exception as e:
        print(f'[sms_reader] Android query failed: {e}')
    return msgs


def _sample_sms_for_testing() -> list[dict]:
    """Return fake SMS samples so UI works on desktop."""
    return [
        {
            'id': 'test_001',
            'address': 'ALRAJHI',
            'body': 'تم الشراء بمبلغ 125.00 ريال لدى ستاربكس الرياض. الرصيد المتاح 3,450.75 ريال.',
            'date_ms': 1700000000000,
        },
        {
            'id': 'test_002',
            'address': 'SNB',
            'body': 'SAR 250.00 deducted from your account at Amazon.sa. Available balance: SAR 1,200.50',
            'date_ms': 1700100000000,
        },
        {
            'id': 'test_003',
            'address': 'RIYAD',
            'body': 'خُصم من حسابك 300.00 ريال لدى محطة أرامكو. رصيدك الحالي 2,100.00 ريال.',
            'date_ms': 1700200000000,
        },
        {
            'id': 'test_004',
            'address': 'ALINMA',
            'body': 'عملية شراء بقيمة 85.50 ر.س من مطعم البيك. الرصيد: 950.25 ر.س',
            'date_ms': 1700300000000,
        },
        {
            'id': 'test_005',
            'address': 'SNB',
            'body': 'SAR 5,000.00 credited to your account. Salary. Balance: SAR 6,200.50',
            'date_ms': 1700400000000,
        },
        {
            'id': 'test_006',
            'address': 'ALRAJHI',
            'body': 'تم الشراء بمبلغ 55.00 ريال لدى صيدلية النهدي. الرصيد المتاح 3,395.75 ريال.',
            'date_ms': 1700500000000,
        },
        {
            'id': 'test_007',
            'address': 'ALRAJHI',
            'body': 'تم الشراء بمبلغ 499.00 ريال لدى نتفليكس. الرصيد المتاح 2,896.75 ريال.',
            'date_ms': 1700600000000,
        },
        {
            'id': 'test_008',
            'address': 'RIYAD',
            'body': 'خُصم من حسابك 180.00 ريال لدى كارفور. رصيدك الحالي 1,920.00 ريال.',
            'date_ms': 1700700000000,
        },
    ]


def sync_sms(on_progress=None, on_done=None):
    """
    Read SMS, parse transactions, save new ones to DB.
    Runs in a background thread; calls on_progress(count) and on_done(total).
    """
    def _worker():
        db = Database.get()
        raw_list = _read_android_sms() if _ANDROID else _sample_sms_for_testing()
        saved = 0
        for raw in raw_list:
            sms_id = raw['id']
            if db.is_sms_processed(sms_id):
                continue
            tx = parse_sms(raw['body'], raw['address'], sms_id)
            if tx:
                tx['category'] = categorize(tx.get('merchant', ''), tx.get('raw_sms', ''))
                tx.pop('balance_after', None)
                tx.pop('_sms_id', None)
                db.insert_transaction(tx)
                db.mark_sms_processed(sms_id)
                saved += 1
                if on_progress:
                    on_progress(saved)
        if on_done:
            on_done(saved)

    threading.Thread(target=_worker, daemon=True).start()
