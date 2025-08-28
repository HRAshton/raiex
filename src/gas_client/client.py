import base64
import hashlib
import json

import requests


def send_data(upload_url: str, integrity_hash_salt: str, transactions: list[dict]) -> None:
    print(f"Sending data to Google Sheets: {len(transactions)} records")

    data_to_send = {"transactions": transactions}

    json_string = json.dumps(data_to_send, ensure_ascii=False)
    integrity_hash = _calculate_integrity_hash(integrity_hash_salt, json_string)

    requests.post(upload_url, data=json_string, params={"hash": integrity_hash})


def _calculate_integrity_hash(integrity_hash_salt: str, data: str) -> str:
    raw_hash = hashlib.sha256((integrity_hash_salt + data).encode("utf-8")).digest()
    return base64.b64encode(raw_hash).decode()
