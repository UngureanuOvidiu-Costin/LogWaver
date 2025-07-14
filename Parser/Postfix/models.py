from datetime import datetime
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SmtpdLog:
    timestamp: datetime
    process_id: int
    queue_id: str
    client_host: str
    client_ip: str
    sasl_method: str | None
    sasl_username: str | None
    raw: str


@dataclass
class QmgrLog:
    timestamp: datetime
    process_id: int
    queue_id: str
    sender: str
    size: int
    nrcpt: int
    queue_status: str
    raw: str


@dataclass
class SmtpLog:
    timestamp: datetime
    process_id: int
    queue_id: str
    recipient: str
    relay_host: str
    relay_ip: str
    relay_port: int
    delay_total: float
    delay_detail: tuple[float, float, float, float]
    dsn: str
    status: str
    status_message: str
    raw: str


@dataclass
class AmavisLog:
    timestamp: datetime
    process_id: int
    session_id: str
    action: str
    result: str
    policy: str
    client_ip: str
    sender_ip: str
    sender: str
    recipient: str
    queue_id: str
    message_id: Optional[str]
    spam_hits: float
    size: int
    queued_as: Optional[str]
    Subject: Optional[str]
    From: Optional[str]
    raw: str


@dataclass
class AmavisPostfixLink:
    original_queue_id: str
    new_queue_id: str
    message_id: str
    amavis_session_id: str
