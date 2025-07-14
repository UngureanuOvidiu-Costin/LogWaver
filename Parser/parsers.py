from Postfix.AMAVIS.parser import parse_amavis_log_line
from Postfix.QMGR.parser import parse_qmgr_log_line
from Postfix.SMTP.parser import parse_smtp_log_line
from Postfix.SMTPD.parser import parse_smtpd_log_line
from Postfix.models import SmtpdLog, QmgrLog, SmtpLog, AmavisLog


def parse_postfix_log_line(line: str) -> SmtpdLog | QmgrLog | SmtpLog | AmavisLog | None:
    if 'smtpd[' in line:
        return parse_smtpd_log_line(line)
    elif 'qmgr[' in line:
        return parse_qmgr_log_line(line)
    elif 'postfix/smtp[' in line:
        return parse_smtp_log_line(line)
    elif 'amavis' in line:
        return parse_amavis_log_line(line)
    else:
        return None