import re
from datetime import datetime
from typing import Optional
from Postfix.models import AmavisLog


# Amavis is like an antivirus for e-mails
# It uses SpamAssassin
def parse_amavis_log_line(line: str) -> Optional[AmavisLog]:
    if "amavis[" not in line:
        return None
    try:
        # Match the full ISO8601 timestamp with timezone
        timestamp_match = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)([+-]\d{2}:\d{2})', line)
        process_id_match = re.search(r'amavis\[(\d+)\]', line)
        session_id_match = re.search(r'\((\d+-\d+)\)', line)
        action_result_match = re.search(r'\) (\w+)\s+(\w+)\s+\{([^}]+)\}', line)

        client_sender_match = re.search(
            r'\[([\d\.]+)\]:\d+ \[([\d\.]+)\] \S+ <([^>]+)> -> <([^>]+)>', line)

        queue_id_match = re.search(r'Queue-ID: (\S+)', line)
        message_id_match = re.search(r'Message-ID: <([^>]+)>', line)

        spam_size_match = re.search(
            r'Hits: (-?\d+\.\d+), size: (\d+), queued_as: (\S+)', line)

        subject_match = re.search(r'Subject: "([^"]+)"', line)
        from_match = re.search(r'From: <([^>]+)>', line)

        if not (timestamp_match and process_id_match and session_id_match
                and action_result_match and client_sender_match and queue_id_match and spam_size_match):
            return None

        timestamp_str = timestamp_match.group(1) + timestamp_match.group(2)
        timestamp = datetime.fromisoformat(timestamp_str)

        return AmavisLog(
            timestamp=timestamp,
            process_id=int(process_id_match.group(1)),
            session_id=session_id_match.group(1),
            action=action_result_match.group(1),
            result=action_result_match.group(2),
            policy=action_result_match.group(3),
            client_ip=client_sender_match.group(1),
            sender_ip=client_sender_match.group(2),
            sender=client_sender_match.group(3),
            recipient=client_sender_match.group(4),
            queue_id=queue_id_match.group(1),
            message_id=message_id_match.group(1) if message_id_match else None,
            spam_hits=float(spam_size_match.group(1)),
            size=int(spam_size_match.group(2)),
            queued_as=spam_size_match.group(3) if spam_size_match.group(3) != '-' else None,
            Subject=subject_match.group(1) if subject_match else None,
            From=from_match.group(1) if from_match else None,
            raw=line,
        )
    except Exception as e:
        print(f"Error parsing line:\n{line}\n{e}")
        return None
