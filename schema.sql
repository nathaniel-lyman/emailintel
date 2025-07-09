-- Database schema for Retail Price Cut Summary App

-- Headlines table: stores scraped news headlines
CREATE TABLE IF NOT EXISTS headlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    link TEXT UNIQUE NOT NULL,
    published_date TIMESTAMP NOT NULL,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Indexes for performance
    CHECK (length(title) > 0),
    CHECK (length(link) > 0)
);

-- Create indexes for headlines table
CREATE INDEX IF NOT EXISTS idx_headlines_link ON headlines(link);
CREATE INDEX IF NOT EXISTS idx_headlines_published_date ON headlines(published_date);
CREATE INDEX IF NOT EXISTS idx_headlines_created_at ON headlines(created_at);

-- Summaries table: stores AI-generated summaries
CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    headline_id INTEGER NOT NULL,
    summary_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_time REAL, -- Time taken to generate summary in seconds
    FOREIGN KEY (headline_id) REFERENCES headlines(id) ON DELETE CASCADE,
    CHECK (length(summary_text) > 0)
);

-- Create index for summaries table
CREATE INDEX IF NOT EXISTS idx_summaries_headline_id ON summaries(headline_id);
CREATE INDEX IF NOT EXISTS idx_summaries_created_at ON summaries(created_at);

-- Settings table: stores configuration
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keywords TEXT NOT NULL DEFAULT 'retail price cut,markdown,rollback,discount,price drop',
    domains TEXT DEFAULT 'walmart.com,target.com,amazon.com,costco.com,kroger.com',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings if not exists
INSERT OR IGNORE INTO settings (id, keywords, domains) 
VALUES (1, 'retail price cut,markdown,rollback,discount,price drop', 'walmart.com,target.com,amazon.com,costco.com,kroger.com');

-- Create trigger to update timestamp on settings change
CREATE TRIGGER IF NOT EXISTS update_settings_timestamp 
AFTER UPDATE ON settings
BEGIN
    UPDATE settings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Processing log table (optional, for tracking and debugging)
CREATE TABLE IF NOT EXISTS processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type TEXT NOT NULL, -- 'scrape', 'summarize', 'email'
    status TEXT NOT NULL, -- 'success', 'failure'
    message TEXT,
    items_processed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for processing log
CREATE INDEX IF NOT EXISTS idx_processing_log_created_at ON processing_log(created_at);
CREATE INDEX IF NOT EXISTS idx_processing_log_operation_type ON processing_log(operation_type);