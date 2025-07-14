import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_batch
from typing import List, Union
from contextlib import contextmanager
from dotenv import load_dotenv
from Postfix.models import SmtpdLog, QmgrLog, SmtpLog, AmavisLog


load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'postfix_logs'),
            'user': os.getenv('DB_USER', 'postfix_user'),
            'password': os.getenv('DB_PASSWORD', 'secure_password_123')
        }
        self.buffer_size = int(os.getenv('BUFFER_SIZE', 1000))
        self.batch_size = int(os.getenv('BATCH_SIZE', 500))

        self.smtpd_buffer: List[SmtpdLog] = []
        self.qmgr_buffer: List[QmgrLog] = []
        self.smtp_buffer: List[SmtpLog] = []
        self.amavis_buffer: List[AmavisLog] = []

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def create_tables(self):
        with open('init.sql', 'r') as f:
            create_sql = f.read()

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(create_sql)
                conn.commit()
                print("Tables created successfully")

    def add_to_buffer(self, log_entry: Union[SmtpdLog, QmgrLog, SmtpLog, AmavisLog]):
        if isinstance(log_entry, SmtpdLog):
            self.smtpd_buffer.append(log_entry)
            if len(self.smtpd_buffer) >= self.buffer_size:
                self.flush_smtpd_buffer()
        elif isinstance(log_entry, QmgrLog):
            self.qmgr_buffer.append(log_entry)
            if len(self.qmgr_buffer) >= self.buffer_size:
                self.flush_qmgr_buffer()
        elif isinstance(log_entry, SmtpLog):
            self.smtp_buffer.append(log_entry)
            if len(self.smtp_buffer) >= self.buffer_size:
                self.flush_smtp_buffer()
        elif isinstance(log_entry, AmavisLog):
            self.amavis_buffer.append(log_entry)
            if len(self.amavis_buffer) >= self.buffer_size:
                self.flush_amavis_buffer()

    def flush_smtpd_buffer(self):
        if not self.smtpd_buffer:
            return

        insert_query = """
                       INSERT INTO smtpd_logs (timestamp, process_id, queue_id, client_host, client_ip,
                                               sasl_method, sasl_username, raw)
                       VALUES (%(timestamp)s, %(process_id)s, %(queue_id)s, %(client_host)s, %(client_ip)s,
                               %(sasl_method)s, %(sasl_username)s, %(raw)s) \
                       """

        data = []
        for log in self.smtpd_buffer:
            data.append({
                'timestamp': log.timestamp,
                'process_id': log.process_id,
                'queue_id': log.queue_id,
                'client_host': log.client_host,
                'client_ip': log.client_ip,
                'sasl_method': log.sasl_method,
                'sasl_username': log.sasl_username,
                'raw': log.raw
            })

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                execute_batch(cur, insert_query, data, page_size=self.batch_size)
                conn.commit()

        print(f"Inserted {len(self.smtpd_buffer)} SMTPD logs")
        self.smtpd_buffer.clear()

    def flush_qmgr_buffer(self):
        if not self.qmgr_buffer:
            return

        insert_query = """
                       INSERT INTO qmgr_logs (timestamp, process_id, queue_id, sender, size, nrcpt, queue_status, raw)
                       VALUES (%(timestamp)s, %(process_id)s, %(queue_id)s, %(sender)s, %(size)s, %(nrcpt)s, \
                               %(queue_status)s, %(raw)s) \
                       """

        data = []
        for log in self.qmgr_buffer:
            data.append({
                'timestamp': log.timestamp,
                'process_id': log.process_id,
                'queue_id': log.queue_id,
                'sender': log.sender,
                'size': log.size,
                'nrcpt': log.nrcpt,
                'queue_status': log.queue_status,
                'raw': log.raw
            })

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                execute_batch(cur, insert_query, data, page_size=self.batch_size)
                conn.commit()

        print(f"Inserted {len(self.qmgr_buffer)} QMGR logs")
        self.qmgr_buffer.clear()

    def flush_smtp_buffer(self):
        if not self.smtp_buffer:
            return

        insert_query = """
                       INSERT INTO smtp_logs (timestamp, process_id, queue_id, recipient, relay_host, relay_ip,
                                              relay_port, delay_total, delay_detail_a, delay_detail_b, delay_detail_c,
                                              delay_detail_d, dsn, status, status_message, raw)
                       VALUES (%(timestamp)s, %(process_id)s, %(queue_id)s, %(recipient)s, %(relay_host)s, %(relay_ip)s,
                               %(relay_port)s, %(delay_total)s, %(delay_detail_a)s, %(delay_detail_b)s, \
                               %(delay_detail_c)s,
                               %(delay_detail_d)s, %(dsn)s, %(status)s, %(status_message)s, %(raw)s) \
                       """

        data = []
        for log in self.smtp_buffer:
            data.append({
                'timestamp': log.timestamp,
                'process_id': log.process_id,
                'queue_id': log.queue_id,
                'recipient': log.recipient,
                'relay_host': log.relay_host,
                'relay_ip': log.relay_ip,
                'relay_port': log.relay_port,
                'delay_total': log.delay_total,
                'delay_detail_a': log.delay_detail[0],
                'delay_detail_b': log.delay_detail[1],
                'delay_detail_c': log.delay_detail[2],
                'delay_detail_d': log.delay_detail[3],
                'dsn': log.dsn,
                'status': log.status,
                'status_message': log.status_message,
                'raw': log.raw
            })

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                execute_batch(cur, insert_query, data, page_size=self.batch_size)
                conn.commit()

        print(f"Inserted {len(self.smtp_buffer)} SMTP logs")
        self.smtp_buffer.clear()

    def flush_amavis_buffer(self):
        if not self.amavis_buffer:
            return

        insert_query = """
                       INSERT INTO amavis_logs (timestamp, process_id, session_id, action, result, policy, client_ip,
                                                sender_ip, sender, recipient, queue_id, message_id, spam_hits, size,
                                                queued_as, subject, from_address, raw)
                       VALUES (%(timestamp)s, %(process_id)s, %(session_id)s, %(action)s, %(result)s, %(policy)s,
                               %(client_ip)s, %(sender_ip)s, %(sender)s, %(recipient)s, %(queue_id)s, %(message_id)s,
                               %(spam_hits)s, %(size)s, %(queued_as)s, %(subject)s, %(from_address)s, %(raw)s) \
                       """

        data = []
        for log in self.amavis_buffer:
            data.append({
                'timestamp': log.timestamp,
                'process_id': log.process_id,
                'session_id': log.session_id,
                'action': log.action,
                'result': log.result,
                'policy': log.policy,
                'client_ip': log.client_ip,
                'sender_ip': log.sender_ip,
                'sender': log.sender,
                'recipient': log.recipient,
                'queue_id': log.queue_id,
                'message_id': log.message_id,
                'spam_hits': log.spam_hits,
                'size': log.size,
                'queued_as': log.queued_as,
                'subject': log.Subject,
                'from_address': log.From,
                'raw': log.raw
            })

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                execute_batch(cur, insert_query, data, page_size=self.batch_size)
                conn.commit()

        print(f"Inserted {len(self.amavis_buffer)} Amavis logs")
        self.amavis_buffer.clear()

    def flush_all_buffers(self):
        self.flush_smtpd_buffer()
        self.flush_qmgr_buffer()
        self.flush_smtp_buffer()
        self.flush_amavis_buffer()