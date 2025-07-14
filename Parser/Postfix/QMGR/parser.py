import re
from datetime import datetime
from typing import Optional
from Postfix.models import QmgrLog


def parse_qmgr_log_line(line: str) -> Optional[QmgrLog]:
    if "qmgr" not in line:
        return None

    try:
        process_id_match = re.search(r'postfix/qmgr\[(\d+)\]', line)
        if not process_id_match:
            return None
        process_id = int(process_id_match.group(1))

        # Match "queued" message - handles both empty and non-empty senders
        # 2025-06-08T06:46:05.575409+03:00 mail postfix/qmgr[3320558]: 4bFLZ53V3kz5WwFJ: from=<fwehhrert@test.com>, size=6226761, nrcpt=1 (queue active)
        m = re.match(
            r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}[+-]\d{2}:\d{2})\s+\S+\s+postfix/qmgr\[\d+\]: ([A-Za-z0-9]+): from=(?:<([^>]*)>|,), size=(\d+), nrcpt=(\d+)(?: \(([^)]+)\))?',
            line
        )
        if m:
            # Handle empty sender case
            sender = m.group(3) if m.group(3) is not None else ''
            # Extract queue status from parentheses, default to 'queued' if not present
            queue_status = m.group(6) if m.group(6) else 'queued'

            return QmgrLog(
                timestamp=datetime.fromisoformat(m.group(1)),
                process_id=process_id,
                queue_id=m.group(2),
                sender=sender,
                size=int(m.group(4)),
                nrcpt=int(m.group(5)),
                queue_status=queue_status,
                raw=line
            )

        # Match "removed" message
        # 2025-06-08T06:46:05.589597+03:00 mail postfix/qmgr[3320558]: 4bFLYw49Pmz5WsKV: removed
        m = re.match(
            r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}[+-]\d{2}:\d{2})\s+\S+\s+postfix/qmgr\[\d+\]: ([A-Za-z0-9]+): removed',
            line
        )
        if m:
            return QmgrLog(
                timestamp=datetime.fromisoformat(m.group(1)),
                process_id=process_id,
                queue_id=m.group(2),
                sender='',
                size=0,
                nrcpt=0,
                queue_status='removed',
                raw=line
            )

        # Match "expired" message
        # 2025-06-08T15:09:42.431135+03:00 mail postfix/qmgr[3320558]: 4bBSSh25v5z5Wxqd: from=<qqqqfwefwef@test.com>, status=expired, returned to sender
        m = re.match(
            r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}[+-]\d{2}:\d{2})\s+\S+\s+postfix/qmgr\[\d+\]: ([A-Za-z0-9]+): from=<([^>]*)>, status=expired, returned to sender',
            line
        )
        if m:
            return QmgrLog(
                timestamp=datetime.fromisoformat(m.group(1)),
                process_id=process_id,
                queue_id=m.group(2),
                sender=m.group(3),
                size=0,  # Size not provided in expired messages
                nrcpt=0,  # nrcpt not provided in expired messages
                queue_status='expired',
                raw=line
            )

        return None
    except Exception as e:
        print(f"Error parsing line:\n{line}\n{e}")
        return None