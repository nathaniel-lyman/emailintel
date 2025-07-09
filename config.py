"""
Configuration management module for Retail Price Cut Summary App.
Handles loading/saving settings from database and environment variables.
"""

import os
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    """Configuration management class."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
    DATABASE_PATH = DATABASE_URL.replace('sqlite:///', '')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Email Configuration - SMTP
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')
    SMTP_TO_EMAIL = os.getenv('SMTP_TO_EMAIL')
    
    # Email Configuration - SendGrid
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL')
    SENDGRID_TO_EMAIL = os.getenv('SENDGRID_TO_EMAIL')
    
    # Scheduler Configuration
    SCHEDULER_TIMEZONE = os.getenv('SCHEDULER_TIMEZONE', 'US/Central')
    DAILY_DIGEST_HOUR = int(os.getenv('DAILY_DIGEST_HOUR', '8'))
    DAILY_DIGEST_MINUTE = int(os.getenv('DAILY_DIGEST_MINUTE', '0'))
    
    # API Configuration
    API_TOKEN = os.getenv('API_TOKEN')
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '10'))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOGTAIL_SOURCE_TOKEN = os.getenv('LOGTAIL_SOURCE_TOKEN')
    
    # Production URLs
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate required configuration values."""
        errors = []
        
        # Check required fields
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        
        # Check email configuration (need either SMTP or SendGrid)
        has_smtp = all([cls.SMTP_USERNAME, cls.SMTP_PASSWORD, cls.SMTP_FROM_EMAIL, cls.SMTP_TO_EMAIL])
        has_sendgrid = all([cls.SENDGRID_API_KEY, cls.SENDGRID_FROM_EMAIL, cls.SENDGRID_TO_EMAIL])
        
        if not (has_smtp or has_sendgrid):
            errors.append("Email configuration required: Set either SMTP or SendGrid credentials")
        
        # Check API token for production
        if cls.FLASK_ENV == 'production' and not cls.API_TOKEN:
            errors.append("API_TOKEN is required in production")
        
        return errors


class SettingsManager:
    """Manages user-configurable settings stored in the database."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_PATH
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def load_settings(self) -> Dict[str, any]:
        """Load settings from database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT keywords, domains, updated_at FROM settings WHERE id = 1")
            row = cursor.fetchone()
            
            if row:
                return {
                    'keywords': row['keywords'],
                    'domains': row['domains'],
                    'updated_at': row['updated_at']
                }
            else:
                # Return defaults if no settings exist
                defaults = self.get_defaults()
                self.save_settings(defaults['keywords'], defaults['domains'])
                return defaults
                
        except sqlite3.Error as e:
            logger.error(f"Error loading settings: {e}")
            return self.get_defaults()
        finally:
            conn.close()
    
    def save_settings(self, keywords: str, domains: str) -> bool:
        """Save settings to database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Validate inputs
            keywords = self._validate_csv(keywords, 'keywords')
            domains = self._validate_csv(domains, 'domains', allow_empty=True)
            
            # Update or insert settings
            cursor.execute("""
                INSERT OR REPLACE INTO settings (id, keywords, domains, updated_at)
                VALUES (1, ?, ?, CURRENT_TIMESTAMP)
            """, (keywords, domains))
            
            conn.commit()
            logger.info("Settings saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_keywords_list(self) -> List[str]:
        """Get keywords as a list."""
        settings = self.load_settings()
        return [k.strip() for k in settings['keywords'].split(',') if k.strip()]
    
    def get_domains_list(self) -> List[str]:
        """Get domains as a list."""
        settings = self.load_settings()
        if not settings['domains']:
            return []
        return [d.strip() for d in settings['domains'].split(',') if d.strip()]
    
    def get_defaults(self) -> Dict[str, any]:
        """Get default settings."""
        defaults = {
            'keywords': os.getenv('KEYWORDS', 'retail price cut,markdown,rollback,discount,price drop'),
            'domains': os.getenv('DOMAINS', 'walmart.com,target.com,amazon.com,costco.com,kroger.com'),
            'updated_at': datetime.now().isoformat()
        }
        return defaults
    
    def _validate_csv(self, value: str, field_name: str, allow_empty: bool = False) -> str:
        """Validate CSV format."""
        if not value and not allow_empty:
            raise ValueError(f"{field_name} cannot be empty")
        
        # Clean up the CSV
        items = [item.strip() for item in value.split(',') if item.strip()]
        
        if not items and not allow_empty:
            raise ValueError(f"{field_name} must contain at least one item")
        
        # Validate individual items
        if field_name == 'domains':
            for domain in items:
                if not self._is_valid_domain(domain):
                    raise ValueError(f"Invalid domain: {domain}")
        
        return ','.join(items)
    
    def _is_valid_domain(self, domain: str) -> bool:
        """Check if domain format is valid."""
        # Basic domain validation
        parts = domain.split('.')
        if len(parts) < 2:
            return False
        
        # Check for valid characters
        import re
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.([a-zA-Z]{2,}\.)*[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    def ensure_defaults_exist(self) -> None:
        """Ensure default settings exist in database."""
        settings = self.load_settings()
        if not settings or settings == self.get_defaults():
            logger.info("Initializing default settings")
            defaults = self.get_defaults()
            self.save_settings(defaults['keywords'], defaults['domains'])


def get_config() -> Config:
    """Get configuration instance."""
    return Config


def get_settings_manager() -> SettingsManager:
    """Get settings manager instance."""
    return SettingsManager()


if __name__ == "__main__":
    # Test configuration
    config = get_config()
    errors = config.validate()
    
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration valid!")
    
    # Test settings manager
    manager = get_settings_manager()
    settings = manager.load_settings()
    print(f"\nCurrent settings:")
    print(f"  Keywords: {settings['keywords']}")
    print(f"  Domains: {settings['domains']}")
    print(f"  Updated: {settings['updated_at']}")