# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a retail price cut monitoring system that scrapes news headlines, summarizes them using OpenAI, and delivers daily email digests. The system features a self-service settings interface for non-technical users to configure search terms without code changes.

## Architecture

The system follows a modular Flask-based architecture with clear separation of concerns:

**Core Components:**
- **`app.py`** - Main Flask application with routes, WTForms integration, APScheduler for background jobs, and CSRF protection
- **`config.py`** - Centralized configuration management with database settings persistence and environment variable loading
- **`scraper.py`** - News scraping module with RSS feed parsing, rate limiting, robots.txt compliance, and Google News integration
- **`summarizer.py`** - OpenAI GPT-4o integration for article summarization with cost tracking and content extraction
- **`emailer.py`** - Email delivery system supporting both SMTP and SendGrid with HTML/plaintext digest generation
- **`init_db.py`** - Database initialization, schema management, and health checking utilities

**Database Schema:**
- `headlines` - Scraped news articles with deduplication by link
- `summaries` - AI-generated summaries linked to headlines
- `settings` - User-configurable search keywords and domains (CSV format)
- `processing_log` - Operation tracking for monitoring and debugging

### Key Data Flow

1. **Configuration**: Settings managed via web UI (`/settings`) stored in SQLite `settings` table
2. **Scraping**: `scraper.py` reads current settings to build dynamic Google News RSS queries
3. **Processing**: Headlines scraped, deduplicated by link+date, stored in `headlines` table
4. **Summarization**: OpenAI GPT-4o processes articles (≤40 words, 3000 char limit) → `summaries` table
5. **Email Delivery**: Daily digest groups summaries by retailer, sends via configured email service
6. **Scheduling**: APScheduler runs scraping every 2 hours, email digest daily at 6 AM Central

## Development Commands

```bash
# Environment setup
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements_minimal.txt  # Use minimal if lxml fails

# Database management
python init_db.py                 # Initialize database
python init_db.py reset          # Reset database
python init_db.py check          # Health check

# Application execution
python app.py                     # Run Flask app (default port 5000)
PORT=5001 python app.py          # Run on alternate port

# Testing and validation
python test_backend.py           # Test backend modules
python test_web.py              # Test web interface (requires running app)

# Configuration
cp .env.example .env            # Create environment file
# Edit .env with your OpenAI API key and email credentials
```

## Configuration Architecture

**Environment Variables (`.env`):**
- `OPENAI_API_KEY` - Required for article summarization
- `SMTP_*` or `SENDGRID_*` - Email delivery credentials
- `KEYWORDS` - Default search terms fallback
- `DOMAINS` - Default domains fallback
- `DAILY_DIGEST_HOUR` - Email schedule (default 6 AM Central)

**Runtime Settings (Database):**
- Keywords and domains stored as CSV in `settings` table
- Managed via `SettingsManager` class in `config.py`
- Real-time updates through web interface without restart

## Background Job System

**APScheduler Integration:**
- **Periodic Scraping**: Every 2 hours, triggers `run_scraping_and_summarization()`
- **Daily Digest**: Configured time (6 AM Central), triggers `run_daily_digest()`
- **Thread Safety**: Uses `scheduler_lock` for safe initialization
- **Graceful Shutdown**: `atexit` handler ensures clean scheduler shutdown

## Web Interface Architecture

**Flask Application (`app.py`):**
- **Routes**: `/` (dashboard), `/settings` (configuration), `/refresh` (manual trigger), `/health`, `/stats`
- **Forms**: WTForms with CSRF protection for settings management
- **Templates**: Tailwind CSS + htmx for dynamic updates without page reloads
- **Error Handling**: Custom 404/500 pages with proper error logging

**Template Structure:**
- `base.html` - Common layout with navigation, flash messages, responsive design
- `index.html` - Dashboard with summaries display, statistics, empty states
- `settings.html` - Configuration interface with live preview and validation

## Rate Limiting & Scraping Protocol

- **Robots.txt Compliance**: `RobotsChecker` class validates URL access
- **Rate Limiting**: 10 requests/min per domain via `RateLimiter` class
- **Retry Logic**: Exponential backoff on 4xx/5xx errors
- **Deduplication**: MD5 hash of links prevents duplicate processing
- **Content Limits**: 3000 character truncation before summarization

## Cost Management

**OpenAI API Tracking:**
- `CostTracker` class logs token usage and costs to `openai_costs.json`
- Uses GPT-4o-mini for cost efficiency while maintaining quality
- Daily cost breakdown and cumulative tracking
- Configurable summary length (40 words max)

## Testing Strategy

**Backend Testing (`test_backend.py`):**
- Configuration validation
- Database health checks
- Individual module testing (scraper, summarizer, emailer)
- Dependency verification

**Web Testing (`test_web.py`):**
- Flask route testing
- API endpoint validation
- Health check verification
- Connection testing

## Task Tracking

This project uses `TODO.md` for comprehensive task tracking across 7 phases. Progress is tracked with completion status and the TodoWrite tool should be used for implementation progress tracking.

## Production Considerations

**Deployment**: Designed for Fly.io with SQLite persistence
**Monitoring**: Comprehensive logging with configurable levels
**Security**: CSRF protection, input validation, no hardcoded secrets
**Scalability**: Single-instance design with embedded SQLite and APScheduler