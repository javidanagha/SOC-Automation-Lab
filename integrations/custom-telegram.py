#!/usr/bin/env python3

import sys
import json
import requests

alert_file = sys.argv[1]
bot_token = sys.argv[2]
chat_id = sys.argv[3]

try:
    with open(alert_file, 'r') as f:
        alert = json.load(f)
except Exception:
    sys.exit(1)

rule_id = alert.get('rule', {}).get('id', 'N/A')
level = alert.get('rule', {}).get('level', 'N/A')
description = alert.get('rule', {}).get('description', 'Web Attack Detected')
agent_name = alert.get('agent', {}).get('name', 'DVWA-Host')

data = alert.get('data', {})
transaction = data.get('transaction', {})

request_line = data.get('request', {}).get('request_line', alert.get('full_log', 'N/A'))

src_ip = (
    data.get('srcip')
    or transaction.get('remote_address')
    or alert.get('srcip')
    or 'N/A'
)

dest_port = transaction.get('local_port', 'N/A')
status = data.get('response', {}).get('status', 'N/A')

message = f"""*WAZUH SECURITY ALERT*

*Attack:* {description}
*Severity:* Level {level} (Rule: {rule_id})
*Source IP:* `{src_ip}`
*Target:* {agent_name}
*Port:* {dest_port}
*Response:* {status}

*Request:*
```
{request_line}
```
"""

url_api = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": message,
    "parse_mode": "Markdown"
}

try:
    requests.post(url_api, json=payload, timeout=10)
except Exception:
    sys.exit(1)
