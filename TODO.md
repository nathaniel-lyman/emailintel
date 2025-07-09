# 📋 Retail Price Cut Summary App - TODO

## 🎯 Project Overview
Build a lightweight system to scrape retail news, summarize price cuts, and deliver daily email digests with a self-service settings interface.

---

## 📊 Progress Tracking
- **Total Tasks:** 47
- **Completed:** 14
- **In Progress:** 0
- **Remaining:** 33

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
- [ ] Create `config.py` helper module
  - [ ] Load settings from database
  - [ ] Save settings to database
  - [ ] Ensure default values exist
  - [ ] Validate settings format
- [ ] Implement environment variable loading
- [ ] Create configuration validation functions

### 2.2 News Scraping Module
- [ ] Create `scraper.py` module
  - [ ] Implement RSS feed parsing with feedparser
  - [ ] Add user-agent headers and rate limiting
  - [ ] Implement deduplication logic by link + date
  - [ ] Add retry logic with exponential backoff
  - [ ] Respect robots.txt
  - [ ] Throttle to 10 requests/min per domain
- [ ] Create query builder for Google News RSS
  - [ ] Dynamic keyword integration
  - [ ] Optional domain filtering
  - [ ] Date range filtering
- [ ] Add comprehensive error handling and logging

### 2.3 Content Summarization
- [ ] Create `summarizer.py` module
  - [ ] Implement HTML content extraction
  - [ ] Clean and truncate text (3000 chars max)
  - [ ] Integrate OpenAI GPT-4o API
  - [ ] Create optimized summarization prompt
  - [ ] Add retry logic for API failures
  - [ ] Implement cost tracking and monitoring
- [ ] Create summary validation and quality checks
- [ ] Add batch processing capabilities

### 2.4 Email System
- [ ] Create `emailer.py` module
  - [ ] Query summaries from past 24 hours
  - [ ] Group summaries by retailer
  - [ ] Generate plaintext email format
  - [ ] Generate HTML email format (optional)
  - [ ] Implement SMTP delivery
  - [ ] Add SendGrid integration for production
- [ ] Create email template system
- [ ] Add recipient management
- [ ] Implement quiet failure for no new stories

---

## 🌐 Phase 3: Web Interface

### 3.1 Flask Application Core
- [ ] Create `app.py` main application file
  - [ ] Set up Flask app with proper configuration
  - [ ] Configure SQLite database connection
  - [ ] Set up APScheduler for background jobs
  - [ ] Add CSRF protection
  - [ ] Configure logging
- [ ] Create database connection management
- [ ] Set up error handlers (404, 500, etc.)

### 3.2 Dashboard Interface
- [ ] Create `templates/base.html` layout
  - [ ] Include Tailwind CSS (CDN)
  - [ ] Include htmx for dynamic updates
  - [ ] Add responsive design
  - [ ] Create navigation structure
- [ ] Create `templates/index.html` dashboard
  - [ ] Display latest 25 summaries
  - [ ] Show active search terms
  - [ ] Add refresh button
  - [ ] Implement card-based layout
  - [ ] Add date/time filtering
- [ ] Implement dashboard route (`/`)
- [ ] Add pagination for older summaries

### 3.3 Settings Interface
- [ ] Create `templates/settings.html`
  - [ ] Keywords input field (CSV)
  - [ ] Domains input field (CSV, optional)
  - [ ] Form validation with WTForms
  - [ ] Success/error messaging
  - [ ] Preview functionality
- [ ] Create settings form class with WTForms
- [ ] Implement settings routes (`/settings` GET/POST)
- [ ] Add settings validation and sanitization
- [ ] Create settings update confirmation

### 3.4 API Endpoints
- [ ] Create manual refresh endpoint (`/refresh`)
  - [ ] Add token-based authentication
  - [ ] Trigger summarizer on-demand
  - [ ] Return JSON status
- [ ] Create health check endpoint (`/health`)
- [ ] Add API rate limiting
- [ ] Create status/statistics endpoint

---

## ⚙️ Phase 4: Automation & Scheduling

### 4.1 Background Job System
- [ ] Configure APScheduler in Flask app
- [ ] Create scheduled scraping job
- [ ] Create scheduled email job (8 AM Central)
- [ ] Add job monitoring and error handling
- [ ] Create job status tracking

### 4.2 GitHub Actions Workflows
- [ ] Create `.github/workflows/daily-digest.yml`
  - [ ] Schedule: Daily at 8 AM Central
  - [ ] Trigger scraping and summarization
  - [ ] Send email digest
  - [ ] Handle failures gracefully
- [ ] Create `.github/workflows/fly-deploy.yml`
  - [ ] Deploy on push to main branch
  - [ ] Run tests before deployment
  - [ ] Handle deployment failures
- [ ] Set up GitHub secrets for production

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