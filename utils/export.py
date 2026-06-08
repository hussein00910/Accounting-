"""Export transactions to CSV."""

import csv
import os
from datetime import datetime


def export_to_csv(transactions: list, month: str = None) -> str:
    try:
        from android.storage import primary_external_storage_path  # type: ignore
        base = os.path.join(primary_external_storage_path(), 'Download')
    except ImportError:
        base = os.path.expanduser('~')

    os.makedirs(base, exist_ok=True)
    label = month or datetime.now().strftime('%Y-%m')
    path = os.path.join(base, f'expenses_{label}.csv')

    fields = ['date', 'amount', 'currency', 'merchant', 'category', 'bank_id', 'type']
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(transactions)

    return path
