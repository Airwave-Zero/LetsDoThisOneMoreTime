CREATE TABLE IF NOT EXISTS transaction_emails (
    id SERIAL PRIMARY KEY,
    received_at TIMESTAMP,
    amount DECIMAL,
    category TEXT
);