CREATE TABLE IF NOT EXISTS BoA_Reporter (
    id SERIAL PRIMARY KEY,
    received_at TIMESTAMP,
    amount DECIMAL,
    category TEXT
);