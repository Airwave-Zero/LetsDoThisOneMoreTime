CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    sender TEXT,
    subject TEXT,
    body TEXT,
    received_at TIMESTAMP,
    category TEXT
);