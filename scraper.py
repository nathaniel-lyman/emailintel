"""
News scraping module for Retail Price Cut Summary App.
Handles RSS feed parsing, deduplication, and rate limiting.
"""

import feedparser
import requests
import sqlite3
import time
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, quote_plus
from urllib.robotparser import RobotFileParser
from collections import defaultdict
import hashlib

from config import Config, SettingsManager

# Configure logging
logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests_per_minute: int = 10):
        self.max_requests = max_requests_per_minute
        self.requests = defaultdict(list)
    
    def can_request(self, domain: str) -> bool:
        """Check if request can be made to domain."""
        now = time.time()
        minute_ago = now - 60
        
        # Remove old requests
        self.requests[domain] = [t for t in self.requests[domain] if t > minute_ago]
        
        # Check if under limit
        return len(self.requests[domain]) < self.max_requests
    
    def add_request(self, domain: str) -> None:
        """Record a request to domain."""
        self.requests[domain].append(time.time())
    
    def wait_if_needed(self, domain: str) -> None:
        """Wait if rate limit would be exceeded."""
        while not self.can_request(domain):
            time.sleep(1)


class RobotsChecker:
    """Check robots.txt compliance."""
    
    def __init__(self):
        self.robots_cache = {}
        self.user_agent = "RetailPriceCutBot/1.0"
    
    def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt."""
        try:
            parsed = urlparse(url)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            
            if domain not in self.robots_cache:
                rp = RobotFileParser()
                rp.set_url(f"{domain}/robots.txt")
                rp.read()
                self.robots_cache[domain] = rp
            
            return self.robots_cache[domain].can_fetch(self.user_agent, url)
        except:
            # If can't check robots.txt, assume we can fetch
            return True


class NewsScraper:
    """Main news scraping class."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.rate_limiter = RateLimiter(Config.MAX_REQUESTS_PER_MINUTE)
        self.robots_checker = RobotsChecker()
        self.settings_manager = SettingsManager(db_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RetailPriceCutBot/1.0 (https://github.com/yourusername/retailpricecut)'
        })
    
    def scrape_news(self, hours_back: int = 24) -> List[Dict]:
        """Scrape news based on current settings."""
        keywords = self.settings_manager.get_keywords_list()
        # Note: domains are ignored for broader Google News search
        
        all_articles = []
        
        # Build and execute queries
        for keyword in keywords:
            rss_url = self._build_google_news_url(keyword)
            articles = self._fetch_rss_feed(rss_url, keyword)
            all_articles.extend(articles)
        
        # Deduplicate and filter by date
        unique_articles = self._deduplicate_articles(all_articles)
        recent_articles = self._filter_by_date(unique_articles, hours_back)
        
        # Save to database
        saved_count = self._save_articles(recent_articles)
        logger.info(f"Scraped {len(recent_articles)} articles, saved {saved_count} new ones")
        
        return recent_articles
    
    def _build_google_news_url(self, keyword: str, domains: List[str] = None) -> str:
        """Build Google News RSS URL with keyword (domain filtering disabled for broader search)."""
        base_url = "https://news.google.com/rss/search"
        
        # Build query - just use keyword without domain filtering
        query = keyword
        encoded_query = quote_plus(query)
        
        # Add parameters for better results
        params = {
            'q': encoded_query,
            'hl': 'en-US',
            'gl': 'US',
            'ceid': 'US:en'
        }
        
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    def _fetch_rss_feed(self, url: str, keyword: str) -> List[Dict]:
        """Fetch and parse RSS feed with retries."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Check rate limit
                domain = urlparse(url).netloc
                self.rate_limiter.wait_if_needed(domain)
                
                # Check robots.txt (temporarily disabled for Google News)
                # if not self.robots_checker.can_fetch(url):
                #     logger.warning(f"Robots.txt disallows fetching {url}")
                #     return []
                
                # Fetch feed
                logger.info(f"Fetching RSS feed for keyword: {keyword} (attempt {attempt + 1})")
                self.rate_limiter.add_request(domain)
                
                response = self.session.get(url, timeout=Config.REQUEST_TIMEOUT)
                response.raise_for_status()
                
                # Parse feed
                feed = feedparser.parse(response.content)
                
                if feed.bozo:
                    logger.warning(f"Feed parsing error: {feed.bozo_exception}")
                
                articles = []
                for entry in feed.entries:
                    article = {
                        'title': entry.get('title', 'No title'),
                        'link': entry.get('link', ''),
                        'published': self._parse_date(entry.get('published')),
                        'source': entry.get('source', {}).get('title', 'Unknown'),
                        'keyword': keyword
                    }
                    
                    if article['link']:  # Only add if has link
                        articles.append(article)
                
                logger.info(f"Found {len(articles)} articles for keyword: {keyword}")
                return articles
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch feed after {max_retries} attempts")
                    return []
            except Exception as e:
                logger.error(f"Unexpected error fetching feed: {e}")
                return []
    
    def _parse_date(self, date_string: Optional[str]) -> datetime:
        """Parse date from various formats."""
        if not date_string:
            return datetime.now()
        
        # Try common date formats
        formats = [
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except:
                continue
        
        # If all fail, return current time
        logger.warning(f"Could not parse date: {date_string}")
        return datetime.now()
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Deduplicate articles by link."""
        seen = set()
        unique = []
        
        for article in articles:
            link_hash = hashlib.md5(article['link'].encode()).hexdigest()
            if link_hash not in seen:
                seen.add(link_hash)
                unique.append(article)
        
        return unique
    
    def _filter_by_date(self, articles: List[Dict], hours_back: int) -> List[Dict]:
        """Filter articles by date range."""
        cutoff = datetime.now() - timedelta(hours=hours_back)
        return [a for a in articles if a['published'] >= cutoff]
    
    def _save_articles(self, articles: List[Dict]) -> int:
        """Save articles to database, return count of new articles saved."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        saved_count = 0
        
        try:
            for article in articles:
                try:
                    cursor.execute("""
                        INSERT INTO headlines (title, link, published_date, source)
                        VALUES (?, ?, ?, ?)
                    """, (
                        article['title'],
                        article['link'],
                        article['published'].isoformat(),
                        article['source']
                    ))
                    saved_count += 1
                except sqlite3.IntegrityError:
                    # Article already exists (unique constraint on link)
                    pass
            
            conn.commit()
            
            # Log the operation
            cursor.execute("""
                INSERT INTO processing_log (operation_type, status, message, items_processed)
                VALUES (?, ?, ?, ?)
            """, ('scrape', 'success', f'Scraped {len(articles)} articles', saved_count))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving articles: {e}")
            conn.rollback()
            
            # Log the failure
            cursor.execute("""
                INSERT INTO processing_log (operation_type, status, message)
                VALUES (?, ?, ?)
            """, ('scrape', 'failure', str(e)))
            
            conn.commit()
            
        finally:
            conn.close()
        
        return saved_count
    
    def get_recent_headlines(self, hours: int = 24) -> List[Dict]:
        """Get recently saved headlines from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT id, title, link, published_date, source, created_at
            FROM headlines
            WHERE published_date >= ?
            ORDER BY published_date DESC
        """, (cutoff.isoformat(),))
        
        headlines = []
        for row in cursor.fetchall():
            headlines.append({
                'id': row['id'],
                'title': row['title'],
                'link': row['link'],
                'published_date': row['published_date'],
                'source': row['source'],
                'created_at': row['created_at']
            })
        
        conn.close()
        return headlines


if __name__ == "__main__":
    # Test the scraper
    import sys
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database if needed
    if not os.path.exists('db.sqlite3'):
        print("Database not found. Please run init_db.py first.")
        sys.exit(1)
    
    # Test scraping
    scraper = NewsScraper()
    articles = scraper.scrape_news(hours_back=24)
    
    print(f"\nScraped {len(articles)} articles:")
    for i, article in enumerate(articles[:5]):  # Show first 5
        print(f"\n{i+1}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Date: {article['published']}")
        print(f"   Link: {article['link'][:50]}...")