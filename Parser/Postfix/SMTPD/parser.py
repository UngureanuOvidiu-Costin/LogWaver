import re
from datetime import datetime
from typing import Optional
from Postfix.models import SmtpdLog

find_client = re.compile(r'client=([a-zA-Z0-9-._]+)\[(.+?)\]')
find_pid = re.compile(r'postfix/(?:[a-zA-Z0-9_/]+/)?smtpd\[(\d+)\]')  # Handles postfix/smtpd and postfix/submission/smtpd

def parse_smtpd_log_line(line: str) -> Optional[SmtpdLog]:
    if ": client=" not in line:
        return None

    try:
        # Try parsing ISO8601 timestamp if present
        timestamp: Optional[datetime] = None
        iso_match = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}))', line)
        if iso_match:
            timestamp = datetime.fromisoformat(iso_match.group(1))
        else:
            # Try format: "Jul 11 10:22:33"
            parts = line.split()
            timestamp_str = " ".join(parts[:3])
            timestamp = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
            timestamp = timestamp.replace(year=datetime.now().year)

        pid_match = find_pid.search(line)
        if not pid_match:
            return None
        process_id = int(pid_match.group(1))

        prefix = line.split(": client=")[0]
        queue_id = prefix.strip().split()[-1]

        client_match = find_client.search(line)
        if not client_match:
            return None
        client_host, client_ip = client_match.group(1), client_match.group(2)

        sasl_method = None
        sasl_username = None
        if "sasl_method=" in line:
            sasl_method = line.split("sasl_method=")[1].split(',')[0].strip()
        if "sasl_username=" in line:
            sasl_username = line.split("sasl_username=")[1].split(',')[0].strip()

        return SmtpdLog(
            timestamp=timestamp,
            process_id=process_id,
            queue_id=queue_id,
            client_host=client_host,
            client_ip=client_ip,
            sasl_method=sasl_method,
            sasl_username=sasl_username,
            raw=line
        )

    except Exception as e:
        return None