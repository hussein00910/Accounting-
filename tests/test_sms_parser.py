"""Unit tests for sms_parser — no Android dependency."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.sms_parser import parse_sms


SAMPLES = [
    # (sender, body, expected_amount, expected_type, expected_bank)
    (
        'ALRAJHI',
        'تم الشراء بمبلغ 125.00 ريال لدى ستاربكس الرياض. الرصيد المتاح 3,450.75 ريال.',
        125.00, 'debit', 'RAJHI',
    ),
    (
        'SNB',
        'SAR 250.00 deducted from your account at Amazon.sa. Available balance: SAR 1,200.50',
        250.00, 'debit', 'SNB',
    ),
    (
        'RIYAD',
        'خُصم من حسابك 300.00 ريال لدى محطة أرامكو. رصيدك الحالي 2,100.00 ريال.',
        300.00, 'debit', 'RIYAD',
    ),
    (
        'ALINMA',
        'عملية شراء بقيمة 85.50 ر.س من مطعم البيك. الرصيد: 950.25 ر.س',
        85.50, 'debit', 'ALINMA',
    ),
    (
        'SNB',
        'SAR 5,000.00 credited to your account. Salary. Balance: SAR 6,200.50',
        5000.00, 'credit', 'SNB',
    ),
    (
        'SABB',
        'SAR 199.00 deducted from your account at Netflix. Available balance SAR 800.00',
        199.00, 'debit', 'SABB',
    ),
    (
        'FAB',
        'AED 150.00 debited from your account at Carrefour. Balance: AED 2,350.00',
        150.00, 'debit', 'FAB',
    ),
    (
        'EmiratesNBD',
        'AED 3,500.00 credited to your account. Salary. Bal: AED 4,000.00',
        3500.00, 'credit', 'EMIRATESNBD',
    ),
]

NON_BANK_SAMPLES = [
    ('friend', 'يا عمر متى تيجي؟', None),
    ('OTP', 'رمز التحقق: 123456', None),
    ('', 'Hello, this is a general message', None),
]


def test_bank_samples():
    passed = failed = 0
    for sender, body, exp_amount, exp_type, exp_bank in SAMPLES:
        result = parse_sms(body, sender)
        ok = (
            result is not None
            and abs(result['amount'] - exp_amount) < 0.01
            and result['type'] == exp_type
            and result['bank_id'] == exp_bank
        )
        status = 'PASS' if ok else 'FAIL'
        if not ok:
            failed += 1
            print(f'[{status}] {sender}: expected ({exp_amount}, {exp_type}, {exp_bank}), got {result}')
        else:
            passed += 1
    print(f'\nBank samples: {passed} passed, {failed} failed')
    return failed == 0


def test_non_bank_samples():
    passed = failed = 0
    for sender, body, _ in NON_BANK_SAMPLES:
        result = parse_sms(body, sender)
        ok = result is None
        if not ok:
            failed += 1
            print(f'[FAIL] Non-bank SMS incorrectly parsed: {body[:40]} → {result}')
        else:
            passed += 1
    print(f'Non-bank samples: {passed} passed, {failed} failed')
    return failed == 0


def test_categorizer():
    from core.categorizer import categorize
    cases = [
        ('ستاربكس', '', 'food'),
        ('أرامكو', '', 'fuel'),
        ('صيدلية النهدي', '', 'health'),
        ('نتفليكس', '', 'subscriptions'),
        ('أمازون', '', 'shopping'),
        ('رسوم كهرباء', '', 'bills'),
        ('شيء غريب جداً', '', 'other'),
    ]
    passed = failed = 0
    for merchant, sms, expected in cases:
        result = categorize(merchant, sms)
        ok = result == expected
        if not ok:
            failed += 1
            print(f'[FAIL] categorize("{merchant}") → {result}, expected {expected}')
        else:
            passed += 1
    print(f'Categorizer: {passed} passed, {failed} failed')
    return failed == 0


if __name__ == '__main__':
    all_ok = True
    all_ok &= test_bank_samples()
    all_ok &= test_non_bank_samples()
    all_ok &= test_categorizer()
    print('\n' + ('✅ All tests passed!' if all_ok else '❌ Some tests failed'))
    sys.exit(0 if all_ok else 1)
