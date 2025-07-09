# Retail Price Cut Summary App

A lightweight system that scrapes retail news headlines, summarizes them using OpenAI, and delivers daily email digests. Features a self-service settings interface for non-technical users to configure search terms without code changes.

## Installation

### Prerequisites

- Python 3.8 or higher
- SQLite3 (included with Python)
- OpenAI API key
- Email credentials (SMTP or SendGrid)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd emailintel
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your credentials
   nano .env  # or use your preferred editor
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`

## Project Structure

```
emailintel/
├── templates/           # HTML templates
├── static/             # Static files (CSS, JS)
├── .github/workflows/  # GitHub Actions workflows
├── schema.sql          # Database schema
├── init_db.py          # Database initialization script
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── .gitignore         # Git ignore rules
```

## Configuration

Edit the `.env` file to configure:

- **OpenAI API Key**: Required for article summarization
- **Email Settings**: SMTP or SendGrid credentials
- **Default Keywords**: Search terms for news scraping
- **Default Domains**: News sources to monitor

## Database Management

- **Initialize database**: `python init_db.py`
- **Reset database**: `python init_db.py reset`
- **Check database health**: `python init_db.py check`

## Development

To contribute to this project:

1. Create a feature branch
2. Make your changes
3. Run tests (when available)
4. Submit a pull request

## License

[License information to be added]