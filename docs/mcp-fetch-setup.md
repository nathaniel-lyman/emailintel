# Fetch MCP Server Setup Guide

This guide provides detailed instructions for setting up the Fetch MCP server to enhance web scraping capabilities in the Email Intelligence project.

## Overview

The Fetch MCP server is designed specifically for efficient web content fetching optimized for LLM usage. It provides superior content extraction compared to traditional scraping methods.

## Prerequisites

- Node.js 16+ installed
- npm or npx available
- Basic understanding of web scraping concepts

## Installation

### Option 1: Global Installation

```bash
# Install globally
npm install -g @modelcontextprotocol/server-fetch
```

### Option 2: Project Installation

```bash
# Install as project dependency
npm install --save-dev @modelcontextprotocol/server-fetch
```

### Option 3: Direct Usage with npx

```bash
# No installation needed
npx @modelcontextprotocol/server-fetch
```

## Configuration

### 1. Basic Claude Desktop Configuration

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

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

### 2. Advanced Configuration with Options

```json
{
  "mcpServers": {
    "fetch-enhanced": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-fetch"
      ],
      "env": {
        "FETCH_USER_AGENT": "EmailIntel/1.0 (Retail Price Monitor)",
        "FETCH_TIMEOUT": "30000",
        "FETCH_MAX_RETRIES": "3",
        "FETCH_CACHE_TTL": "3600"
      }
    }
  }
}
```

## Key Features for Email Intelligence

### 1. Automatic Content Conversion

The Fetch MCP automatically converts HTML to markdown, which is ideal for:
- Cleaner content for OpenAI summarization
- Reduced token usage
- Better structure preservation

### 2. Built-in Rate Limiting

Respects rate limits automatically:
- Per-domain request throttling
- Exponential backoff on failures
- Concurrent request management

### 3. JavaScript Rendering Support

Handles modern web applications:
- SPAs and dynamic content
- Client-side rendered news sites
- AJAX-loaded content

## Integration with Email Intelligence

### 1. Replace Current Scraping Logic

Current approach in `summarizer.py`:
```python
# Current implementation
response = requests.get(url, timeout=5)
soup = BeautifulSoup(response.content, 'html.parser')
text = soup.get_text()
```

With Fetch MCP:
```python
# Using Fetch MCP
content = fetch_mcp.fetch_content(
    url=article_url,
    options={
        "convert_to_markdown": True,
        "include_metadata": True,
        "max_content_length": 3000
    }
)
```

### 2. Enhanced RSS Feed Processing

```python
# Fetch MCP can handle RSS feeds directly
feed_content = fetch_mcp.fetch_feed(
    url="https://news.google.com/rss/search",
    params={
        "q": "retail price cut",
        "hl": "en-US",
        "gl": "US",
        "ceid": "US:en"
    }
)
```

### 3. Batch Processing

```python
# Process multiple URLs efficiently
urls = [article.link for article in headlines]
contents = fetch_mcp.fetch_batch(
    urls=urls,
    options={
        "parallel": 5,
        "timeout": 10000,
        "retry_failed": True
    }
)
```

## Use Cases

### 1. News Article Extraction

```javascript
// Fetch news article with optimal settings
fetch_mcp.fetch({
  url: "https://www.retaildive.com/news/...",
  options: {
    convertToMarkdown: true,
    extractMainContent: true,
    removeAds: true,
    preserveLinks: true
  }
})
```

### 2. Handling Paywalls

```javascript
// Use different strategies for paywall sites
fetch_mcp.fetch({
  url: "https://wsj.com/articles/...",
  options: {
    userAgent: "Googlebot/2.1",
    acceptCookies: false,
    javascriptEnabled: false
  }
})
```

### 3. Monitoring Changes

```javascript
// Check if content has changed
fetch_mcp.fetch({
  url: "https://cnbc.com/retail/",
  options: {
    returnHash: true,
    compareWithCache: true,
    onlyIfChanged: true
  }
})
```

## Performance Optimization

### 1. Caching Configuration

```json
{
  "mcpServers": {
    "fetch-cached": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"],
      "env": {
        "FETCH_CACHE_ENABLED": "true",
        "FETCH_CACHE_TTL": "3600",
        "FETCH_CACHE_SIZE": "100MB",
        "FETCH_CACHE_PATH": "./cache/fetch"
      }
    }
  }
}
```

### 2. Request Optimization

```javascript
// Optimize for news content
const newsConfig = {
  timeout: 15000,
  followRedirects: true,
  maxRedirects: 3,
  compression: true,
  // Only fetch text content
  acceptTypes: ["text/html", "application/xml"],
  // Skip multimedia
  skipResources: ["image", "video", "font", "stylesheet"]
};
```

### 3. Error Handling

```javascript
// Robust error handling
try {
  const content = await fetch_mcp.fetch(url, {
    retries: 3,
    retryDelay: 1000,
    onRetry: (error, attemptNumber) => {
      console.log(`Retry ${attemptNumber} for ${url}: ${error.message}`);
    }
  });
} catch (error) {
  if (error.code === 'TIMEOUT') {
    // Handle timeout
  } else if (error.code === 'BLOCKED') {
    // Handle blocking
  }
}
```

## Comparison with Current Approach

| Feature | Current (requests + BS4) | Fetch MCP |
|---------|-------------------------|-----------|
| JavaScript Support | ❌ No | ✅ Yes |
| Auto-retry | ❌ Manual | ✅ Built-in |
| Rate Limiting | ❌ Manual | ✅ Automatic |
| Content Conversion | ❌ Manual | ✅ Automatic |
| Caching | ❌ No | ✅ Built-in |
| Resource Efficiency | ⚠️ Medium | ✅ Optimized |

## Security Considerations

### 1. URL Validation

```javascript
// Validate URLs before fetching
const allowedDomains = [
  'cnbc.com',
  'retaildive.com',
  'businessinsider.com'
];

fetch_mcp.setConfig({
  urlFilter: (url) => {
    const domain = new URL(url).hostname;
    return allowedDomains.some(allowed => 
      domain.endsWith(allowed)
    );
  }
});
```

### 2. Content Sanitization

```javascript
// Sanitize fetched content
fetch_mcp.setConfig({
  sanitize: true,
  removeScripts: true,
  removeStyles: true,
  maxContentSize: 1024 * 1024 // 1MB limit
});
```

## Monitoring and Debugging

### 1. Enable Debug Logging

```json
{
  "mcpServers": {
    "fetch-debug": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-fetch",
        "--debug"
      ],
      "env": {
        "DEBUG": "fetch:*",
        "LOG_LEVEL": "debug"
      }
    }
  }
}
```

### 2. Performance Metrics

```javascript
// Track fetch performance
fetch_mcp.on('fetch:complete', (metrics) => {
  console.log({
    url: metrics.url,
    duration: metrics.duration,
    size: metrics.contentSize,
    cached: metrics.fromCache,
    retries: metrics.retryCount
  });
});
```

## Migration Strategy

### Phase 1: Parallel Testing
1. Keep existing scraper.py
2. Implement fetch_mcp_scraper.py
3. Compare results for accuracy

### Phase 2: Gradual Migration
1. Use Fetch MCP for problematic sites
2. Fall back to requests for simple sites
3. Monitor performance differences

### Phase 3: Full Migration
1. Replace all scraping with Fetch MCP
2. Remove requests and beautifulsoup4 dependencies
3. Update documentation

## Troubleshooting

### Common Issues

1. **Timeout Errors**
   - Increase timeout value
   - Check network connectivity
   - Verify site availability

2. **Content Not Found**
   - Enable JavaScript rendering
   - Check for dynamic loading
   - Inspect page structure

3. **Rate Limiting**
   - Reduce concurrent requests
   - Add delays between requests
   - Use proxy rotation

## Best Practices

1. **Always Set User-Agent**: Identify your bot properly
2. **Respect robots.txt**: Check site policies
3. **Cache Aggressively**: Reduce unnecessary requests
4. **Handle Errors Gracefully**: Implement fallback strategies
5. **Monitor Performance**: Track success rates and response times

## Next Steps

1. Test Fetch MCP with sample news sites
2. Compare extraction quality with current method
3. Implement error handling strategies
4. Set up performance monitoring
5. Create migration plan for production