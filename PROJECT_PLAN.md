# 📰 Retail Price Cut Summary App

## 📌 Objective

Build a lightweight, low‑cost system to:

* **Scrape** retail news headlines about price cuts (configurable keywords + sources)
* **Summarize** articles using OpenAI
* **Display** summaries on a simple web dashboard
* **Email** a daily digest to stakeholders at 8 AM Central

> **NEW:** A self‑service **Settings** screen lets non‑technical users edit search terms (keywords, domains, date filters) without touching code.

---

## 🛡️ Tech Stack – Final Recommendation

| Concern          | Tool/Service (why)                                        |
| ---------------- | --------------------------------------------------------- |
| Scraping         | `requests`, `feedparser`, `beautifulsoup4` – minimal deps |
| Summarization    | **OpenAI GPT‑4o** – best cost‑to‑quality ratio            |
| Persistence      | **SQLite** – tables: `headlines`, `summaries`, `settings` |
| Web Dashboard    | **Flask** + **WTForms** for settings UI                   |
| Front‑End        | Tailwind (CDN) + htmx for snappy, no‑JS reloads           |
| Background Jobs  | **APScheduler** embedded; manual `/refresh` endpoint      |
| Email            | `smtplib` / **SendGrid** for prod scalability             |
| Scheduler (prod) | **GitHub Actions cron** for scrape + email workflows      |
| Hosting (prod)   | **Fly.io** free tier – Flask + SQLite + small VM          |
| Monitoring       | Fly.io logs + optional Logtail free tier                  |

---

## 📂 Project Structure

```text
emailintel/
├── app.py                 # Flask app, routes, APScheduler
├── config.py              # Helper to load/update settings from DB
├── summarizer.py          # Fetch + summarise headlines (reads settings)
├── emailer.py             # Daily email sender
├── db.sqlite3             # Persistent store
├── templates/
│   ├── index.html         # Dashboard
│   └── settings.html      # Search‑config form
├── static/
│   └── styles.css         # Tailwind overrides (optional)
├── .github/workflows/
│   ├── daily-digest.yml   # Scrape + summarise + email
│   └── fly-deploy.yml     # CD pipeline for Fly.io
├── requirements.txt       # Python deps
└── PROJECT_PLAN.md        # This doc
```

---

## 🧫 Core Functionality (expanded)

### 1. **Configurable News Search (NEW)**

* `settings` table: `keywords` (CSV), `domains` (CSV, optional), `updated_at`.
* `/settings` GET renders current config; POST validates + saves edits.
* **Default keywords:** `retail price cut`, `markdown`, `rollback`, `discount`, `price drop`.
* Summariser loads keywords at runtime → builds Google News RSS query:
  `q="({keywords}) ("price" OR "discount")" site:{domains}`

### 2. **Scrape News Feeds**

* Use [`feedparser`](https://pypi.org/project/feedparser/) with user‑agent header.
* Deduplicate by `link` + date; persist raw headline in `headlines`.

### 3. **Summarise Content**

* Pull HTML (`requests`, 5 s timeout, 2 retries).
* Clean text, truncate 3 000 chars.
* Prompt GPT‑4o: *“Summarise in ≤40 words, highlighting retailer, product type, discount % or price point, and effective date if present.”*
* Save to `summaries` with FK to `headline_id`.

### 4. **Web Dashboard (Flask)**

* **Home `/`** → latest 25 summaries (tailwind cards).
* **Settings `/settings`** → WTForms form; CSRF token; writes to DB.
* **Refresh `/refresh?token=…`** → triggers `summarizer.py` on‑demand.

### 5. **Email Delivery**

* `emailer.py` selects summaries from past 24 h; groups by retailer; builds plaintext + optional HTML.
* Uses credentials in `.env`; aborts quietly if no new stories.

### 6. **Caching & Rate‑Limits**

* Respect robots.txt; throttle 10 req/min per domain.
* Exponential back‑off on 4xx/5xx.

### 7. **Logging & Monitoring**

* `logging.INFO` to STDOUT + rotating file for scrape errors.
* Fly log shipping to Logtail for alerting.

---

## 🛠️ Setup & Deployment

**Local Dev Quick‑start** (unchanged) …

### Secrets (.env example)

Add:

```ini
# Search UI defaults (comma‑separated)
KEYWORDS="retail price cut, markdown, rollback"
DOMAINS="cnbc.com, retaildive.com"
```

---

## 🕒 Scheduling Details (unchanged)

---

## ✅ TODO (next actions)

* [ ] Generate `requirements.txt` (Flask, WTForms, feedparser, beautifulsoup4, openai, APScheduler, python‑dotenv, htmx).
* [ ] Create `config.py` helper (load/save settings; ensure defaults).
* [ ] Build `settings.html` (Tailwind form) + Flask route with WTForms validation.
* [ ] Update `summarizer.py` to pull keywords/domains from DB.
* [ ] Extend DB migration to add `settings` table.
* [ ] Update `index.html` to show active search terms at top.
* [ ] Implement permissionless `/refresh` token auth.
* [ ] Fly.io secrets & first deploy; verify settings persistence.
* [ ] GitHub Actions workflow remains same (uses stored settings).
