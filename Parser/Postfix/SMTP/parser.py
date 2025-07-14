import re
from re import Pattern
from datetime import datetime
from Postfix.models import SmtpLog

timestamp_re = re.compile(r'^(\w{3} \d{1,2} \d{2}:\d{2}:\d{2})')
message_id_re = re.compile(r'postfix/\w+(?:/\w+)?\[\d+\]: ([A-F0-9]+):')

LOG_PATTERNS = [
    {
        "name": "connection timed out",
        "regex": re.compile(
            r"^(?P<timestamp>\S+) \S+ postfix/smtp\[\d+\]: connect to (?P<domain>[^\[]+)\[(?P<ip>[^\]]+)\]:(?P<port>\d+): (?P<error_msg>Connection timed out)$"
        )
    },
    {
        "name": "network unreachable",
        "regex": re.compile(
            r"^(?P<timestamp>\S+) \S+ postfix/smtp\[\d+\]: connect to (?P<domain>[^\[]+)\[(?P<ip>[^\]]+)\]:(?P<port>\d+): (?P<error_msg>Network is unreachable)$"
        )
    },
    {
        "name": "deferred status",
        "regex": re.compile(
            r"^(?P<timestamp>\S+) \S+ postfix/smtp\[\d+\]: (?P<queue_id>[A-Za-z0-9]+): to=<(?P<to>[^>]+)>, relay=(?P<relay>[^,]+), delay=(?P<delay>[^,]+), delays=(?P<delays>[^,]+), dsn=(?P<dsn>[^,]+), status=(?P<status>\w+) \((?P<status_msg>.+)\)$"
        )
    },
    {
        "name": "successful delivery",
        "regex": re.compile(
            r"^(?P<timestamp>\S+) \S+ postfix/smtp\[\d+\]: (?P<queue_id>[A-Za-z0-9]+): to=<(?P<to>[^>]+)>, relay=(?P<relay>[^,]+), delay=(?P<delay>[^,]+), delays=(?P<delays>[^,]+), dsn=(?P<dsn>[^,]+), status=(?P<status>\w+) \((?P<status_msg>.+)\)$"
        )
    },
    {
        "name": "tls connection established",
        "regex": re.compile(
            r"^(?P<timestamp>\S+) \S+ postfix/smtp\[\d+\]: Trusted TLS connection established to (?P<domain>[^\[]+)\[(?P<ip>[^\]]+)\]:(?P<port>\d+): TLS(?P<tls_version>[^\s]+) with cipher (?P<cipher>[^\s]+)(?: \(.+\))?$"
        )
    },
]


def parse_timestamp(timestamp_str: str) -> datetime:
    try:
        # Try ISO format first (2024-01-01T12:00:00+00:00)
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        # Try syslog format (Jul  4 07:58:20)
        current_year = datetime.now().year
        return datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")


def extract_common_fields(line: str, service: str) -> tuple[datetime, int] | None:
    timestamp_match = re.search(r'^(\d{4}-\d{2}-\d{2}T[\d:.+\-]+|\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', line)
    process_match = re.search(rf'postfix/{service}\[(\d+)\]:', line)

    if not timestamp_match or not process_match:
        return None

    timestamp = parse_timestamp(timestamp_match.group(1))
    process_id = int(process_match.group(1))

    return timestamp, process_id


def parse_smtp_log_line(line: str) -> SmtpLog | None:
    common_fields = extract_common_fields(line, 'smtp')
    if not common_fields:
        return None

    timestamp, process_id = common_fields

    delivery_match = re.search(
        r'([A-Za-z0-9]+): to=<([^>]+)>, relay=([^,]+), delay=([^,]+), delays=([^,]+), dsn=([^,]+), status=(\w+) \(([^)]+)\)',
        line
    )

    if not delivery_match:
        return None

    try:
        relay_info = delivery_match.group(3)
        relay_host = ""
        relay_ip = ""
        relay_port = 25  # default

        if '[' in relay_info and ']' in relay_info:
            relay_match = re.search(r'([^\[]+)\[([\d\.]+)\]:(\d+)', relay_info)
            if relay_match:
                relay_host = relay_match.group(1)
                relay_ip = relay_match.group(2)
                relay_port = int(relay_match.group(3))
        else:
            relay_host = relay_info
            relay_ip = relay_info if re.match(r'^\d+\.\d+\.\d+\.\d+$', relay_info) else ""

        delays_str = delivery_match.group(5)
        delay_parts = delays_str.split('/')
        if len(delay_parts) == 4:
            delay_detail = tuple(float(d) for d in delay_parts)
        else:
            delay_detail = (0.0, 0.0, 0.0, 0.0)

        return SmtpLog(
            timestamp=timestamp,
            process_id=process_id,
            queue_id=delivery_match.group(1),
            recipient=delivery_match.group(2),
            relay_host=relay_host,
            relay_ip=relay_ip,
            relay_port=relay_port,
            delay_total=float(delivery_match.group(4)),
            delay_detail=delay_detail,
            dsn=delivery_match.group(6),
            status=delivery_match.group(7),
            status_message=delivery_match.group(8),
            raw=line
        )
    except Exception as e:
        print(f"Error parsing smtp line: {e}")
        return None


def extract_timestamp(line):
    m = timestamp_re.match(line)
    if m:
        return m.group(1)
    return None
