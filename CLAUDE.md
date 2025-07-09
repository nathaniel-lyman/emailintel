# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a retail price cut monitoring system that scrapes news headlines, summarizes them using OpenAI, and delivers daily email digests. The system features a self-service settings interface for non-technical users to configure search terms without code changes.

## Architecture

The system follows a modular Flask-based architecture:

- **`app.py`** - Main Flask application with routes, APScheduler for background jobs, and CSRF protection
- **`config.py`** - Database settings management (load/save from SQLite `settings` table)
- **`summarizer.py`** - News scraping and OpenAI summarization pipeline (reads settings dynamically)
- **`emailer.py`** - Daily digest email generation and delivery
- **`db.sqlite3`** - SQLite database with tables: `headlines`, `summaries`, `settings`

### Key Data Flow

1. Settings configured via web UI are stored in SQLite `settings` table
2. `summarizer.py` reads settings to build Google News RSS queries
3. Headlines are scraped, deduplicated, and stored in `headlines` table
4. OpenAI GPT-4o summarizes articles (≤40 words) and stores in `summaries` table
5. Daily email digest pulls summaries from past 24h and groups by retailer
6. APScheduler handles background jobs; GitHub Actions provides production scheduling

## Development Commands

Since this is a Flask application, typical development workflow:

```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
# or
flask run

# Database initialization
python -c "from app import init_db; init_db()"
```

## Key Technical Decisions

- **SQLite** for persistence (simple, cost-effective for single-instance deployment)
- **OpenAI GPT-4o** for summarization with cost tracking
- **Tailwind CSS + htmx** for minimal JavaScript frontend
- **APScheduler** for embedded background jobs
- **GitHub Actions** for production scheduling (8 AM Central daily digest)
- **Fly.io** for production hosting with persistent SQLite storage

## Settings Management

The core feature is dynamic settings via the `/settings` route:
- Keywords and domains stored as CSV in database
- `config.py` provides helpers for loading/saving settings
- `summarizer.py` builds queries dynamically from current settings
- Default keywords: "retail price cut", "markdown", "rollback", "discount", "price drop"

## Rate Limiting & Scraping

- Respect robots.txt and throttle to 10 requests/min per domain
- Exponential backoff on 4xx/5xx errors
- Deduplication by link + date to prevent duplicate processing
- 3000 character limit on article text before summarization

## Environment Variables

Key environment variables (see PROJECT_PLAN.md for full list):
- `OPENAI_API_KEY` - OpenAI API access
- `SMTP_*` or `SENDGRID_*` - Email delivery credentials
- `KEYWORDS` - Default search terms (fallback)
- `DOMAINS` - Default domains to search (fallback)

## Task Tracking

This project uses TODO.md for comprehensive task tracking across 7 phases. Always update progress there and check off completed tasks. The TodoWrite tool should be used frequently to track implementation progress.

## Production Deployment

- **Fly.io** with `fly.toml` configuration
- **GitHub Actions** workflows for daily operations and CD
- **Logtail** integration for monitoring (optional)
- **SQLite** persistence via Fly.io volumes