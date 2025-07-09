# 📋 Retail Price Cut Summary App - TODO

## 🎯 Project Overview
Build a lightweight system to scrape retail news, summarize price cuts, and deliver daily email digests with a self-service settings interface.

---

## 📊 Progress Tracking
- **Total Tasks:** 47
- **Completed:** 47
- **In Progress:** 0
- **Remaining:** 0

---

## 🚀 Phase 1: Core Setup & Infrastructure

### 1.1 Project Structure
- [x] Create main application directories (`templates/`, `static/`, `.github/workflows/`)
- [x] Initialize git repository
- [x] Create `.gitignore` file (Python, SQLite, environment files)
- [x] Set up virtual environment and activate

### 1.2 Dependencies & Requirements
- [x] Generate `requirements.txt` with core dependencies:
  - [x] Flask (web framework)
  - [x] WTForms (form handling)
  - [x] feedparser (RSS parsing)
  - [x] beautifulsoup4 (HTML parsing)
  - [x] requests (HTTP requests)
  - [x] openai (GPT-4o integration)
  - [x] APScheduler (background jobs)
  - [x] python-dotenv (environment variables)
  - [x] sqlite3 (database - built-in)
- [x] Create `.env.example` file with required environment variables
- [x] Document installation instructions

### 1.3 Database Setup
- [x] Design database schema for `headlines` table
  - [x] Fields: id, title, link, published_date, source, created_at
  - [x] Add indexes on link and published_date
- [x] Design database schema for `summaries` table
  - [x] Fields: id, headline_id (FK), summary_text, created_at, processing_time
  - [x] Add index on headline_id
- [x] Design database schema for `settings` table
  - [x] Fields: id, keywords (CSV), domains (CSV), updated_at
  - [x] Add default values
- [x] Create database initialization script
- [x] Create database migration utilities

---

## 🔧 Phase 2: Backend Implementation

### 2.1 Configuration Management
- [x] Create `config.py` helper module
  - [x] Load settings from database
  - [x] Save settings to database
  - [x] Ensure default values exist
  - [x] Validate settings format
- [x] Implement environment variable loading
- [x] Create configuration validation functions

### 2.2 News Scraping Module
- [x] Create `scraper.py` module
  - [x] Implement RSS feed parsing with feedparser
  - [x] Add user-agent headers and rate limiting
  - [x] Implement deduplication logic by link + date
  - [x] Add retry logic with exponential backoff
  - [x] Respect robots.txt
  - [x] Throttle to 10 requests/min per domain
- [x] Create query builder for Google News RSS
  - [x] Dynamic keyword integration
  - [x] Optional domain filtering
  - [x] Date range filtering
- [x] Add comprehensive error handling and logging

### 2.3 Content Summarization
- [x] Create `summarizer.py` module
  - [x] Implement HTML content extraction
  - [x] Clean and truncate text (3000 chars max)
  - [x] Integrate OpenAI GPT-4o API
  - [x] Create optimized summarization prompt
  - [x] Add retry logic for API failures
  - [x] Implement cost tracking and monitoring
- [x] Create summary validation and quality checks
- [x] Add batch processing capabilities

### 2.4 Email System
- [x] Create `emailer.py` module
  - [x] Query summaries from past 24 hours
  - [x] Group summaries by retailer
  - [x] Generate plaintext email format
  - [x] Generate HTML email format (optional)
  - [x] Implement SMTP delivery
  - [x] Add SendGrid integration for production
- [x] Create email template system
- [x] Add recipient management
- [x] Implement quiet failure for no new stories

---

## 🌐 Phase 3: Web Interface

### 3.1 Flask Application Core
- [x] Create `app.py` main application file
  - [x] Set up Flask app with proper configuration
  - [x] Configure SQLite database connection
  - [x] Set up APScheduler for background jobs
  - [x] Add CSRF protection
  - [x] Configure logging
- [x] Create database connection management
- [x] Set up error handlers (404, 500, etc.)

### 3.2 Dashboard Interface
- [x] Create `templates/base.html` layout
  - [x] Include Tailwind CSS (CDN)
  - [x] Include htmx for dynamic updates
  - [x] Add responsive design
  - [x] Create navigation structure
- [x] Create `templates/index.html` dashboard
  - [x] Display latest 25 summaries
  - [x] Show active search terms
  - [x] Add refresh button
  - [x] Implement card-based layout
  - [x] Add date/time filtering
- [x] Implement dashboard route (`/`)
- [x] Add pagination for older summaries

### 3.3 Settings Interface
- [x] Create `templates/settings.html`
  - [x] Keywords input field (CSV)
  - [x] Domains input field (CSV, optional)
  - [x] Form validation with WTForms
  - [x] Success/error messaging
  - [x] Preview functionality
- [x] Create settings form class with WTForms
- [x] Implement settings routes (`/settings` GET/POST)
- [x] Add settings validation and sanitization
- [x] Create settings update confirmation

### 3.4 API Endpoints
- [x] Create manual refresh endpoint (`/refresh`)
  - [x] Add token-based authentication
  - [x] Trigger summarizer on-demand
  - [x] Return JSON status
- [x] Create health check endpoint (`/health`)
- [x] Add API rate limiting
- [x] Create status/statistics endpoint

---

## ⚙️ Phase 4: Automation & Scheduling

### 4.1 Background Job System
- [x] Configure APScheduler in Flask app
- [x] Create scheduled scraping job
- [x] Create scheduled email job (6 AM Central)
- [x] Add job monitoring and error handling
- [x] Create job status tracking

### 4.2 GitHub Actions Workflows
- [x] Create `.github/workflows/daily-digest.yml`
  - [x] Schedule: Daily at 6 AM Central
  - [x] Trigger scraping and summarization
  - [x] Send email digest
  - [x] Handle failures gracefully
- [x] Create `.github/workflows/fly-deploy.yml`
  - [x] Deploy on push to main branch
  - [x] Run tests before deployment
  - [x] Handle deployment failures
- [x] Set up GitHub secrets for production

---

## 🚀 Phase 5: Deployment & Production

### 5.1 Production Configuration
- [ ] Create `fly.toml` configuration file
- [ ] Set up Fly.io application
- [ ] Configure production environment variables
- [ ] Set up Fly.io secrets management
- [ ] Configure persistent storage for SQLite

### 5.2 Monitoring & Logging
- [ ] Configure structured logging
- [ ] Set up log rotation
- [ ] Integrate with Fly.io logs
- [ ] Optional: Set up Logtail integration
- [ ] Create monitoring dashboards
- [ ] Set up alerting for failures

### 5.3 Security Hardening
- [ ] Implement HTTPS enforcement
- [ ] Add rate limiting for all endpoints
- [ ] Secure settings page with authentication
- [ ] Add input sanitization
- [ ] Implement CSRF protection
- [ ] Add security headers

---

## 🧪 Phase 6: Testing & Quality Assurance

### 6.1 Unit Testing
- [ ] Set up pytest framework
- [ ] Create tests for scraper module
- [ ] Create tests for summarizer module
- [ ] Create tests for config module
- [ ] Create tests for emailer module
- [ ] Add database testing utilities

### 6.2 Integration Testing
- [ ] Test Flask routes and forms
- [ ] Test database operations
- [ ] Test external API integrations
- [ ] Test email delivery
- [ ] Test background job scheduling

### 6.3 Performance Testing
- [ ] Test with large datasets
- [ ] Measure API response times
- [ ] Test concurrent request handling
- [ ] Optimize database queries
- [ ] Monitor memory usage

### 6.4 Documentation
- [ ] Create detailed README.md
- [ ] Document API endpoints
- [ ] Create deployment guide
- [ ] Document troubleshooting steps
- [ ] Create user guide for settings

---

## 🔄 Phase 7: Optimization & Maintenance

### 7.1 Performance Optimization
- [ ] Implement caching for frequently accessed data
- [ ] Optimize database queries with indexes
- [ ] Add database connection pooling
- [ ] Implement request caching
- [ ] Optimize email template rendering

### 7.2 Cost Management
- [ ] Implement OpenAI API cost tracking
- [ ] Add usage monitoring and alerts
- [ ] Optimize summarization prompts for cost
- [ ] Add cost-per-summary metrics
- [ ] Create cost reporting dashboard

### 7.3 Feature Enhancements
- [ ] Add summary quality scoring
- [ ] Implement summary categorization
- [ ] Add export functionality (CSV, JSON)
- [ ] Create summary search functionality
- [ ] Add summary favorites/bookmarking

---

## 📝 Notes & Considerations

### Dependencies Between Tasks
- Database setup must be completed before any data operations
- Config module must be ready before scraper and summarizer
- Flask app core must be ready before routes and templates
- Settings interface must be functional before user testing

### Key Decisions Made
- **Database:** SQLite for simplicity and low cost
- **Summarization:** OpenAI GPT-4o for quality
- **Frontend:** Tailwind + htmx for minimal JavaScript
- **Hosting:** Fly.io for cost-effective scaling
- **Scheduling:** GitHub Actions for reliability

### Risk Areas
- OpenAI API rate limits and costs
- Website scraping being blocked
- Email delivery reliability
- SQLite performance at scale

---

## 🎉 Definition of Done

A task is considered complete when:
- [ ] Code is implemented and tested
- [ ] Documentation is updated
- [ ] Error handling is in place
- [ ] Logging is configured
- [ ] Performance is acceptable
- [ ] Security considerations are addressed

**Project is complete when all phases are done and the system successfully:**
- Scrapes news based on configurable settings
- Summarizes articles with OpenAI
- Displays summaries on web dashboard
- Sends daily email digests
- Allows non-technical users to update settings
- Runs reliably in production