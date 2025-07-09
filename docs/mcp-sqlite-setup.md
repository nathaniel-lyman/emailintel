# SQLite MCP Server Setup Guide

This guide provides detailed instructions for setting up the SQLite MCP server for the Email Intelligence project.

## Prerequisites

- Node.js 16+ installed
- npm or npx available
- Access to the `db.sqlite3` database file

## Installation

### Option 1: Direct Installation (Recommended for Development)

```bash
# Install globally
npm install -g @modelcontextprotocol/server-sqlite

# Or install locally in project
npm install --save-dev @modelcontextprotocol/server-sqlite
```

### Option 2: Using npx (No Installation Required)

```bash
# Run directly with npx
npx @modelcontextprotocol/server-sqlite path/to/db.sqlite3
```

## Configuration

### 1. Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "emailintel-sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "/Users/mcnellymac/Developer/emailintel/db.sqlite3"
      ]
    }
  }
}
```

### 2. Environment-Specific Configuration

For different environments, use environment variables:

```json
{
  "mcpServers": {
    "emailintel-sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite"],
      "env": {
        "SQLITE_DB_PATH": "${DB_PATH:-./db.sqlite3}"
      }
    }
  }
}
```

## Available Operations

### 1. Query Operations

```sql
-- Get recent headlines
SELECT * FROM headlines 
ORDER BY published_date DESC 
LIMIT 25;

-- Get summaries from last 24 hours
SELECT s.*, h.title, h.source 
FROM summaries s
JOIN headlines h ON s.headline_id = h.id
WHERE s.created_at > datetime('now', '-1 day')
ORDER BY s.created_at DESC;

-- Get current settings
SELECT * FROM settings 
ORDER BY updated_at DESC 
LIMIT 1;
```

### 2. Data Analysis Queries

```sql
-- Count summaries by source
SELECT h.source, COUNT(*) as count
FROM summaries s
JOIN headlines h ON s.headline_id = h.id
GROUP BY h.source
ORDER BY count DESC;

-- Average processing time by day
SELECT DATE(created_at) as date, 
       AVG(processing_time) as avg_time
FROM summaries
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Keywords performance
SELECT keywords, COUNT(*) as headlines_found
FROM settings s
JOIN headlines h ON h.created_at > s.updated_at
GROUP BY keywords;
```

### 3. Maintenance Queries

```sql
-- Check for duplicate headlines
SELECT link, COUNT(*) as duplicates
FROM headlines
GROUP BY link
HAVING COUNT(*) > 1;

-- Find orphaned summaries
SELECT s.* FROM summaries s
LEFT JOIN headlines h ON s.headline_id = h.id
WHERE h.id IS NULL;

-- Database statistics
SELECT 
  (SELECT COUNT(*) FROM headlines) as total_headlines,
  (SELECT COUNT(*) FROM summaries) as total_summaries,
  (SELECT COUNT(*) FROM settings) as settings_entries;
```

## Security Considerations

### 1. Read-Only Mode for Production

For production environments, configure read-only access:

```json
{
  "mcpServers": {
    "emailintel-sqlite-readonly": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "--readonly",
        "/path/to/db.sqlite3"
      ]
    }
  }
}
```

### 2. Access Control

Limit database file permissions:

```bash
# Set appropriate permissions
chmod 644 db.sqlite3  # Read for all, write for owner only

# For read-only access
chmod 444 db.sqlite3  # Read-only for all
```

### 3. Backup Strategy

Before using MCP server in production:

```bash
# Create backup
cp db.sqlite3 db.sqlite3.backup

# Automated daily backup
0 2 * * * cp /path/to/db.sqlite3 /path/to/backups/db.sqlite3.$(date +\%Y\%m\%d)
```

## Integration with Email Intelligence

### 1. Data Exploration

Use the SQLite MCP to explore data patterns:

```sql
-- Find most successful keywords
SELECT 
  s.keywords,
  COUNT(DISTINCT h.id) as headlines,
  COUNT(DISTINCT su.id) as summaries
FROM settings s
JOIN headlines h ON h.created_at BETWEEN s.updated_at AND 
  COALESCE((SELECT MIN(updated_at) FROM settings WHERE updated_at > s.updated_at), datetime('now'))
LEFT JOIN summaries su ON su.headline_id = h.id
GROUP BY s.keywords
ORDER BY summaries DESC;
```

### 2. Performance Monitoring

```sql
-- Monitor scraping performance
SELECT 
  DATE(created_at) as date,
  COUNT(*) as headlines_scraped,
  COUNT(DISTINCT source) as unique_sources
FROM headlines
WHERE created_at > datetime('now', '-7 days')
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- OpenAI API usage tracking
SELECT 
  DATE(created_at) as date,
  COUNT(*) as summaries_created,
  SUM(processing_time) as total_processing_time,
  AVG(processing_time) as avg_processing_time
FROM summaries
WHERE created_at > datetime('now', '-30 days')
GROUP BY DATE(created_at);
```

### 3. Email Digest Preparation

```sql
-- Get summaries for daily digest
SELECT 
  h.source as retailer,
  h.title,
  h.link,
  s.summary_text,
  h.published_date
FROM summaries s
JOIN headlines h ON s.headline_id = h.id
WHERE s.created_at > datetime('now', '-1 day')
ORDER BY h.source, h.published_date DESC;
```

## Troubleshooting

### Common Issues

1. **Database Locked Error**
   ```bash
   # Check for active connections
   fuser db.sqlite3
   
   # Enable WAL mode for better concurrency
   sqlite3 db.sqlite3 "PRAGMA journal_mode=WAL;"
   ```

2. **Permission Denied**
   ```bash
   # Fix permissions
   chmod 664 db.sqlite3
   chown $USER:$GROUP db.sqlite3
   ```

3. **MCP Server Not Found**
   ```bash
   # Verify installation
   npm list -g @modelcontextprotocol/server-sqlite
   
   # Clear npm cache if needed
   npm cache clean --force
   ```

### Debug Mode

Enable verbose logging:

```json
{
  "mcpServers": {
    "emailintel-sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "--verbose",
        "db.sqlite3"
      ]
    }
  }
}
```

## Best Practices

1. **Regular Backups**: Implement automated backups before write operations
2. **Query Optimization**: Use EXPLAIN QUERY PLAN for complex queries
3. **Index Management**: Create indexes for frequently queried columns
4. **Connection Pooling**: Limit concurrent connections in production
5. **Monitoring**: Track query performance and database growth

## Next Steps

1. Test basic read operations
2. Implement automated backup strategy
3. Create custom queries for common tasks
4. Set up monitoring for database performance
5. Document team-specific queries and procedures