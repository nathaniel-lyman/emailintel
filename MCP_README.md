# MCP Integration for Email Intelligence

This directory contains documentation and configuration for Model Context Protocol (MCP) servers that enhance the Email Intelligence project.

## Quick Start

1. **Copy the example configuration**:
   ```bash
   # macOS
   cp claude_desktop_config.example.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Windows
   copy claude_desktop_config.example.json %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Update the configuration**:
   - Replace `/Users/mcnellymac/Developer/emailintel/` with your actual project path
   - Add your GitHub Personal Access Token if using GitHub MCP

3. **Restart Claude Desktop** to load the new MCP servers

## Available Documentation

### Core Documentation
- **[MCP_INTEGRATION.md](./MCP_INTEGRATION.md)** - Overview of all recommended MCP servers and their benefits
- **[claude_desktop_config.example.json](./claude_desktop_config.example.json)** - Example configuration file

### Setup Guides
- **[docs/mcp-sqlite-setup.md](./docs/mcp-sqlite-setup.md)** - Detailed SQLite MCP server setup and usage
- **[docs/mcp-fetch-setup.md](./docs/mcp-fetch-setup.md)** - Fetch MCP server configuration for web scraping

## MCP Servers Overview

### 1. SQLite MCP Server (Priority: High)
- **Purpose**: Direct database access and management
- **Key Benefits**: Query optimization, bulk operations, real-time analysis
- **Status**: ✅ Documentation complete

### 2. Fetch MCP Server (Priority: High)
- **Purpose**: Enhanced web content fetching
- **Key Benefits**: JavaScript support, automatic retries, content optimization
- **Status**: ✅ Documentation complete

### 3. GitHub MCP Server (Priority: Medium)
- **Purpose**: Repository and workflow automation
- **Key Benefits**: Issue tracking, workflow monitoring, deployment automation
- **Status**: 🔄 Documentation pending

### 4. Browserbase MCP Server (Priority: Medium)
- **Purpose**: Cloud browser automation for difficult sites
- **Key Benefits**: Anti-scraping bypass, distributed scraping
- **Status**: 🔄 Evaluation pending

### 5. Custom Email MCP Server (Priority: Low)
- **Purpose**: Email service integration
- **Key Benefits**: SendGrid/SMTP management, template handling
- **Status**: 📋 Specification pending

## Project Integration Points

### Current Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Scraper   │────▶│ Summarizer  │────▶│   Emailer   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                            │
                      ┌─────▼─────┐
                      │  SQLite   │
                      └───────────┘
```

### With MCP Integration
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Fetch MCP   │────▶│ Summarizer  │────▶│ Email MCP   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                            │
                      ┌─────▼─────┐
                      │SQLite MCP │
                      └───────────┘
                            │
                      ┌─────▼─────┐
                      │GitHub MCP │
                      └───────────┘
```

## Usage Examples

### Query Database with SQLite MCP
```sql
-- Get today's summaries
SELECT * FROM summaries 
WHERE DATE(created_at) = DATE('now')
ORDER BY created_at DESC;
```

### Fetch Content with Fetch MCP
```javascript
// Fetch and convert news article
fetch("https://retaildive.com/news/...")
  .convertToMarkdown()
  .extractMainContent()
  .limitTo(3000);
```

### Monitor Workflows with GitHub MCP
```javascript
// Check daily digest workflow status
github.getWorkflowRuns("daily-digest.yml")
  .filterByDate("today")
  .checkStatus();
```

## Development Workflow

1. **Local Development**:
   - Use SQLite MCP for database queries and debugging
   - Use Fetch MCP for testing new scraping targets
   
2. **Testing**:
   - SQLite MCP for test data management
   - Fetch MCP with caching for consistent test results

3. **Production Monitoring**:
   - GitHub MCP for workflow status
   - SQLite MCP (read-only) for production data analysis

## Security Best Practices

1. **Database Access**:
   - Use read-only mode for production SQLite MCP
   - Regular backups before write operations

2. **API Keys**:
   - Store all tokens in environment variables
   - Never commit tokens to version control

3. **Web Scraping**:
   - Configure appropriate user agents
   - Respect rate limits and robots.txt

## Troubleshooting

### MCP Servers Not Loading
1. Check Claude Desktop logs
2. Verify configuration file syntax
3. Ensure Node.js is installed
4. Check file paths are absolute

### Permission Issues
1. Verify database file permissions
2. Check API token validity
3. Ensure network connectivity

## Future Enhancements

1. **Custom MCP Servers**:
   - Email service integration
   - OpenAI cost tracking
   - Custom analytics

2. **Advanced Integration**:
   - Automated testing with MCP
   - Performance monitoring dashboard
   - Cost optimization recommendations

## Resources

- [Official MCP Documentation](https://modelcontextprotocol.io)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [Claude Desktop Documentation](https://docs.anthropic.com/en/docs/claude-desktop)

## Contributing

When adding new MCP servers:
1. Document the setup process
2. Include example configurations
3. Add integration examples
4. Update this README

## Support

For MCP-related issues:
- Check the troubleshooting section
- Review server-specific documentation
- Consult official MCP resources