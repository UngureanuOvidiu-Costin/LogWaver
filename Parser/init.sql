-- Create database tables for Postfix logs

CREATE TABLE IF NOT EXISTS smtpd_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    process_id INTEGER NOT NULL,
    queue_id VARCHAR(255),
    client_host VARCHAR(255),
    client_ip INET,
    sasl_method VARCHAR(100),
    sasl_username VARCHAR(255),
    raw TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS qmgr_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    process_id INTEGER NOT NULL,
    queue_id VARCHAR(255) NOT NULL,
    sender VARCHAR(255),
    size INTEGER,
    nrcpt INTEGER,
    queue_status VARCHAR(50),
    raw TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS smtp_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    process_id INTEGER NOT NULL,
    queue_id VARCHAR(255) NOT NULL,
    recipient VARCHAR(255),
    relay_host VARCHAR(255),
    relay_ip INET,
    relay_port INTEGER,
    delay_total FLOAT,
    delay_detail_a FLOAT,
    delay_detail_b FLOAT,
    delay_detail_c FLOAT,
    delay_detail_d FLOAT,
    dsn VARCHAR(20),
    status VARCHAR(50),
    status_message TEXT,
    raw TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS amavis_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    process_id INTEGER NOT NULL,
    session_id VARCHAR(50),
    action VARCHAR(50),
    result VARCHAR(50),
    policy VARCHAR(100),
    client_ip INET,
    sender_ip INET,
    sender VARCHAR(255),
    recipient VARCHAR(255),
    queue_id VARCHAR(255),
    message_id VARCHAR(500),
    spam_hits FLOAT,
    size INTEGER,
    queued_as VARCHAR(255),
    subject TEXT,
    from_address VARCHAR(255),
    raw TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_smtpd_timestamp ON smtpd_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_smtpd_queue_id ON smtpd_logs(queue_id);
CREATE INDEX IF NOT EXISTS idx_smtpd_client_ip ON smtpd_logs(client_ip);

CREATE INDEX IF NOT EXISTS idx_qmgr_timestamp ON qmgr_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_qmgr_queue_id ON qmgr_logs(queue_id);
CREATE INDEX IF NOT EXISTS idx_qmgr_sender ON qmgr_logs(sender);

CREATE INDEX IF NOT EXISTS idx_smtp_timestamp ON smtp_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_smtp_queue_id ON smtp_logs(queue_id);
CREATE INDEX IF NOT EXISTS idx_smtp_recipient ON smtp_logs(recipient);

CREATE INDEX IF NOT EXISTS idx_amavis_timestamp ON amavis_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_amavis_queue_id ON amavis_logs(queue_id);
CREATE INDEX IF NOT EXISTS idx_amavis_sender ON amavis_logs(sender);
