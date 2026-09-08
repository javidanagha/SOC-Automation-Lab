#!/usr/bin/env python3

import sys
import json
import requests

CORTEX_URL = "http://192.168.40.140:9001"
CORTEX_KEY = "CORTEX_API_KEY"
ABUSEIPDB_ID = "ANALYZER_ID"

alert_file = sys.argv[1]
hook_url = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else sys.argv[2]

try:
    with open(alert_file, 'r') as f:
        alert = json.load(f)
except Exception:
    sys.exit(1)

rule = alert.get('rule', {})
data = alert.get('data', {})
transaction = data.get('transaction', {})

src_ip = (
    data.get('srcip')
    or transaction.get('remote_address')
    or alert.get('srcip')
    or 'N/A'
)

payload = {
    "rule_id": rule.get('id', 'N/A'),
    "level": rule.get('level', 'N/A'),
    "description": rule.get('description', 'N/A'),
    "mitre": rule.get('mitre', {}).get('id', []),
    "agent": alert.get('agent', {}).get('name', 'N/A'),
    "timestamp": alert.get('timestamp', 'N/A'),
    "src_ip": src_ip,
    "dest_port": transaction.get('local_port', 'N/A'),
    "http_status": data.get('response', {}).get('status', 'N/A'),
    "request": data.get('request', {}).get('request_line', '')[:500],
    "location": alert.get('location', 'N/A')
}

# Cortex enrichment for the source IP
if src_ip and src_ip != 'N/A':
    try:
        r = requests.post(
            f"{CORTEX_URL}/api/analyzer/{ABUSEIPDB_ID}/run",
            headers={
                "Authorization": f"Bearer {CORTEX_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "data": src_ip,
                "dataType": "ip",
                "tlp": 2,
                "message": "Wazuh alert enrichment"
            },
            timeout=15
        )
        if r.status_code in (200, 201):
            payload["cortex_job_id"] = r.json().get("id", "N/A")
            payload["cortex_status"] = "submitted"
        else:
            payload["cortex_status"] = f"error_{r.status_code}"
    except Exception:
        payload["cortex_status"] = "unreachable"

try:
    requests.post(hook_url, json=payload, timeout=10)
except Exception:
