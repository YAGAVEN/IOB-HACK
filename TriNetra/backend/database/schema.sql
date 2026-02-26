-- TriNetra Supabase Schema
-- Run this in your Supabase SQL editor to create all required tables

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_id TEXT UNIQUE NOT NULL,
    from_account TEXT NOT NULL,
    to_account TEXT NOT NULL,
    amount REAL NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    transaction_type TEXT,
    suspicious_score REAL DEFAULT 0.0,
    pattern_type TEXT,
    scenario TEXT
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_scenario ON transactions(scenario);
CREATE INDEX IF NOT EXISTS idx_transactions_from_account ON transactions(from_account);
CREATE INDEX IF NOT EXISTS idx_transactions_to_account ON transactions(to_account);

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    account_name TEXT,
    account_type TEXT,
    country TEXT,
    risk_level TEXT
);

-- Account risk scores table
CREATE TABLE IF NOT EXISTS account_risk_scores (
    account_id TEXT PRIMARY KEY,
    risk_score REAL DEFAULT 0.0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (optional - allows public read for demo)
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE account_risk_scores ENABLE ROW LEVEL SECURITY;

-- Allow read access with anon key (for demo purposes)
CREATE POLICY "Allow public read" ON transactions FOR SELECT USING (true);
CREATE POLICY "Allow public insert" ON transactions FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON transactions FOR UPDATE USING (true);

CREATE POLICY "Allow public read" ON accounts FOR SELECT USING (true);
CREATE POLICY "Allow public insert" ON accounts FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read" ON account_risk_scores FOR SELECT USING (true);
CREATE POLICY "Allow public insert" ON account_risk_scores FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON account_risk_scores FOR UPDATE USING (true);
