# Model Context Protocol (MCP) Integration Guide

This document outlines the MCP servers that can enhance the Email Intelligence project's capabilities.

## Overview

Model Context Protocol (MCP) provides standardized connections between AI models and data sources. By integrating MCP servers, we can enhance our retail price monitoring system with better data access, improved web scraping, and automated workflows.

## Recommended MCP Servers

### 1. SQLite MCP Server
**Priority**: High  
**Repository**: `@modelcontextprotocol/server-sqlite`

#### Benefits
- Direct read/write access to our SQLite database
- Schema inspection capabilities
- Query optimization suggestions
- Automated backup operations

#### Use Cases
- Bulk data operations on headlines and summaries
- Advanced analytics queries
- Database maintenance tasks
- Real-time data exploration

#### Configuration
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "db.sqlite3"]
    }
  }
}
```

### 2. Fetch MCP Server
**Priority**: High  
**Repository**: `@modelcontextprotocol/server-fetch`

#### Benefits
- Optimized web content fetching for LLMs
- Automatic HTML-to-markdown conversion
- Built-in rate limiting and caching
- Better handling of dynamic content

#### Use Cases
- Replace or augment current `requests` + `beautifulsoup4` approach
- Handle sites with complex JavaScript
- Improved content extraction
- Automatic retries with backoff

#### Configuration
```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}
```

### 3. GitHub MCP Server
**Priority**: Medium  
**Repository**: `@modelcontextprotocol/server-github`

#### Benefits
- Direct integration with GitHub Actions
- Automated issue creation for failures
- Repository and workflow management
- PR automation for updates

#### Use Cases
- Monitor daily digest workflow status
- Create issues for failed scrapes
- Automate deployment processes
- Track OpenAI API costs in issues

#### Configuration
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"
      }
    }
  }
}
```

### 4. Browserbase MCP Server
**Priority**: Medium  
**Repository**: `@browserbase/mcp-server-browserbase`

#### Benefits
- Cloud-based browser automation
- Bypass anti-scraping measures
- Handle JavaScript-heavy sites
- Distributed scraping capabilities

#### Use Cases
- Scrape news sites that block traditional methods
- Extract content from SPAs
- Handle CAPTCHA challenges
- Scale scraping operations

#### Configuration
```json
{
  "mcpServers": {
    "browserbase": {
      "command": "npx",
      "args": ["-y", "@browserbase/mcp-server-browserbase"],
      "env": {
        "BROWSERBASE_API_KEY": "<your-api-key>",
        "BROWSERBASE_PROJECT_ID": "<your-project-id>"
      }
    }
  }
}
```

### 5. Axiom MCP Server
**Priority**: Low  
**Repository**: `@axiomhq/mcp-server-axiom`

#### Benefits
- Natural language log queries
- Performance metrics tracking
- Cost analysis dashboards
- Alert configuration

#### Use Cases
- Monitor OpenAI API usage and costs
- Track scraping success rates
- Analyze email delivery metrics
- Debug production issues

#### Configuration
```json
{
  "mcpServers": {
    "axiom": {
      "command": "npx",
      "args": ["-y", "@axiomhq/mcp-server-axiom"],
      "env": {
        "AXIOM_API_TOKEN": "<your-token>",
        "AXIOM_ORG_ID": "<your-org-id>"
      }
    }
  }
}
```

## Custom MCP Servers to Develop

### 1. Email MCP Server
Since no direct email MCP server exists, we should create one for:

**Features**:
- SendGrid/SMTP integration
- Email template management
- Recipient list management
- Delivery status tracking
- Bounce handling
- Unsubscribe management

**Schema Example**:
```python
# email_mcp_server.py
class EmailMCPServer:
    async def send_digest(self, recipients: List[str], summaries: List[Dict]):
        """Send daily digest email"""
        pass
    
    async def get_delivery_status(self, email_id: str):
        """Check email delivery status"""
        pass
    
    async def manage_recipients(self, action: str, email: str):
        """Add/remove recipients"""
        pass
```

### 2. OpenAI Cost Tracker MCP
Custom server for monitoring AI costs:

**Features**:
- Real-time cost tracking
- Usage analytics by source
- Budget alerts
- Cost optimization suggestions
- Historical trend analysis

**Schema Example**:
```python
# openai_cost_mcp_server.py
class OpenAICostMCPServer:
    async def track_usage(self, tokens: int, model: str, source: str):
        """Track API usage and costs"""
        pass
    
    async def get_cost_report(self, date_range: str):
        """Generate cost report"""
        pass
    
    async def set_budget_alert(self, threshold: float):
        """Configure budget alerts"""
        pass
```

## Integration Steps

### Phase 1: Core MCP Setup
1. Install MCP CLI tools
2. Configure SQLite MCP server
3. Configure Fetch MCP server
4. Test basic operations

### Phase 2: Enhanced Capabilities
1. Set up GitHub MCP server
2. Configure GitHub Actions integration
3. Test automated workflows

### Phase 3: Advanced Features
1. Evaluate Browserbase for difficult sites
2. Set up Axiom for monitoring
3. Develop custom Email MCP server

### Phase 4: Optimization
1. Implement OpenAI Cost Tracker MCP
2. Optimize scraping with MCP servers
3. Create unified MCP dashboard

## Security Considerations

1. **API Keys**: Store all MCP server API keys in environment variables
2. **Database Access**: Limit SQLite MCP to read-only for production
3. **Rate Limiting**: Configure appropriate limits for all MCP servers
4. **Audit Logging**: Track all MCP server operations

## Monitoring & Maintenance

1. **Health Checks**: Regular verification of MCP server status
2. **Performance**: Monitor response times and resource usage
3. **Updates**: Keep MCP servers updated to latest versions
4. **Backup**: Regular backups of MCP configurations

## Cost Implications

- **Fetch MCP**: Free (self-hosted)
- **SQLite MCP**: Free (self-hosted)
- **GitHub MCP**: Free with GitHub account
- **Browserbase**: Usage-based pricing
- **Axiom**: Free tier available, then usage-based

## Next Steps

1. Start with SQLite and Fetch MCP servers for immediate benefits
2. Add GitHub MCP for workflow automation
3. Evaluate need for Browserbase based on scraping success
4. Develop custom MCP servers as project evolves