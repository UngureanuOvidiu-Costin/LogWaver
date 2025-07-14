import re
import gzip
import mysql.connector
from datetime import datetime
from typing import Iterator, Optional, List, Union
from pathlib import Path
from models import ImapLogEntry, MailboxActionEntry


ParsedLogEntry = Union[ImapLogEntry, MailboxActionEntry]


def parse_imap_mailbox_actions(line: str) -> Optional[ParsedLogEntry]:
    if "copy from" not in line and "expunge:" not in line and "delete:" not in line and "Mailbox created:" not in line:
        return None

    try:
        match = re.match(
            r'^(\d{4}-\d{2}-\d{2}T[^ ]+)\s+\S+\s+dovecot: imap\(([^)]+)\)[^:]+:\s+(.+?):\s+(.*)$',
            line
        )
        if not match:
            return None

        timestamp_str, user, action, rest = match.groups()
        timestamp = datetime.fromisoformat(timestamp_str)

        if len(action) > 100:
            print(f"Action too long: {action} (len={len(action)})")


        # Handle 'Mailbox operations' separately
        if action == "Mailbox created" or action == "Mailbox deleted" or action == "Mailbox renamed":
            return MailboxActionEntry(
                timestamp=timestamp,
                user=user,
                action=action,
                box=rest.strip(),
                uid=-1,
                msgid="",
                size=-1,
                msg_from="",
                subject="",
                flags="",
                raw=line.strip()
            )

        # Common actions: copy, delete, expunge
        fields = {
            'box': '',
            'uid': '',
            'msgid': '',
            'size': '',
            'from': '',
            'subject': '',
            'flags': ''
        }

        for key in fields.keys():
            regex = re.search(rf"{key}=((\"[^\"]*\"|\([^)]+\)|<[^>]+>|[^,]+))", rest)
            if regex:
                val = regex.group(1).strip()
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                fields[key] = val

        uid = int(fields['uid']) if fields['uid'] and str(fields['uid']).isdigit() else -1
        size = int(fields['size']) if fields['size'] and str(fields['size']).isdigit() else -1

        return MailboxActionEntry(
            timestamp=timestamp,
            user=user,
            action=action,
            box=fields['box'],
            uid=uid,
            msgid=fields['msgid'],
            size=size,
            msg_from=fields['from'],
            subject=fields['subject'],
            flags=fields['flags'],
            raw=line.strip()
        )

    except Exception as e:
        return None

