"""
Content summarization module for Retail Price Cut Summary App.
Handles article content extraction and OpenAI GPT-4o summarization.
"""

import requests
import sqlite3
import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import openai
from openai import OpenAI

from config import Config

# Configure logging
logger = logging.getLogger(__name__)


class ContentExtractor:
    """Extract and clean article content from web pages."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; RetailPriceCutBot/1.0)'
        })
    
    def extract_content(self, url: str) -> Optional[str]:
        """Extract main content from article URL."""
        try:
            response = self.session.get(url, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content
            content = self._find_article_content(soup)
            
            if not content:
                # Fallback to all paragraph text
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text() for p in paragraphs])
            
            # Clean and truncate
            content = self._clean_text(content)
            content = content[:3000]  # Limit to 3000 chars
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def _find_article_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Try to find the main article content."""
        # Common article containers
        containers = [
            {'name': 'article'},
            {'class_': 'article-content'},
            {'class_': 'article-body'},
            {'class_': 'post-content'},
            {'class_': 'entry-content'},
            {'class_': 'content-body'},
            {'id': 'article-body'},
            {'role': 'main'},
            {'itemprop': 'articleBody'}
        ]
        
        for selector in containers:
            element = soup.find(**selector)
            if element:
                return element.get_text()
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove extra whitespace
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        text = ' '.join(lines)
        
        # Remove multiple spaces
        while '  ' in text:
            text = text.replace('  ', ' ')
        
        return text.strip()


class TopicClassifier:
    """AI-powered topic classification for news summaries."""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Define topic categories
        self.topics = [
            "Electronics & Gaming",      # PlayStation, Xbox, phones, computers, etc.
            "Home & Garden",            # Appliances, furniture, home improvement
            "Clothing & Fashion",       # Apparel, shoes, accessories
            "Health & Beauty",          # Personal care, cosmetics, health products
            "Food & Beverages",         # Groceries, restaurants, food delivery
            "Toys & Baby",             # Children's items, baby products
            "Sports & Outdoors",        # Sporting goods, outdoor equipment
            "Automotive",              # Cars, parts, services
            "Books & Media",           # Books, movies, music
            "General Retail"           # Broad sales, store-wide discounts, other
        ]
    
    def classify_topic(self, summary_text: str, headline_title: str = "") -> str:
        """Classify a summary into one of the predefined topic categories."""
        
        try:
            # Combine summary and headline for better context
            content = f"Headline: {headline_title}\nSummary: {summary_text}".strip()
            
            # Create prompt for topic classification
            topics_list = "\n".join([f"- {topic}" for topic in self.topics])
            
            prompt = f"""Classify this retail price cut news into ONE of these categories:

{topics_list}

Content to classify:
{content}

Instructions:
- Choose the MOST SPECIFIC category that fits
- If about a specific product type (like PlayStation, iPhone), choose the category it belongs to
- If about general store sales or multiple categories, choose "General Retail"
- Respond with ONLY the category name, exactly as listed above

Category:"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use mini for cost efficiency
                messages=[
                    {"role": "system", "content": "You are a news categorization expert. Classify retail news into specific product categories."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20,
                temperature=0.1
            )
            
            classified_topic = response.choices[0].message.content.strip()
            
            # Validate the response is one of our topics
            if classified_topic in self.topics:
                return classified_topic
            else:
                logger.warning(f"Invalid topic returned: {classified_topic}, defaulting to General Retail")
                return "General Retail"
                
        except Exception as e:
            logger.error(f"Error classifying topic: {e}")
            return "General Retail"


class Summarizer:
    """Main summarization class using OpenAI GPT-4o."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.content_extractor = ContentExtractor()
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.cost_tracker = CostTracker()
        self.topic_classifier = TopicClassifier()
    
    def summarize_new_headlines(self) -> int:
        """Summarize all headlines without summaries."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get headlines without summaries
        cursor.execute("""
            SELECT h.id, h.title, h.link, h.source
            FROM headlines h
            LEFT JOIN summaries s ON h.id = s.headline_id
            WHERE s.id IS NULL
            ORDER BY h.published_date DESC
            LIMIT 50
        """)
        
        headlines = cursor.fetchall()
        conn.close()
        
        if not headlines:
            logger.info("No new headlines to summarize")
            return 0
        
        logger.info(f"Found {len(headlines)} headlines to summarize")
        
        # Process in batches
        summarized_count = 0
        for headline in headlines:
            success = self._summarize_headline(headline)
            if success:
                summarized_count += 1
            
            # Small delay to avoid rate limits
            time.sleep(0.5)
        
        # Log the operation
        self._log_operation(summarized_count, len(headlines))
        
        return summarized_count
    
    def _summarize_headline(self, headline: sqlite3.Row) -> bool:
        """Summarize a single headline."""
        start_time = time.time()
        
        try:
            # Extract article content
            content = self.content_extractor.extract_content(headline['link'])
            
            if not content:
                logger.warning(f"Could not extract content from {headline['link']}")
                # Use title as fallback
                content = headline['title']
            
            # Generate summary
            summary = self._generate_summary(
                title=headline['title'],
                content=content,
                source=headline['source']
            )
            
            if not summary:
                return False
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Save summary
            self._save_summary(headline['id'], summary, processing_time, headline['title'])
            
            logger.info(f"Summarized: {headline['title'][:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error summarizing headline {headline['id']}: {e}")
            return False
    
    def _generate_summary(self, title: str, content: str, source: str) -> Optional[str]:
        """Generate summary using OpenAI GPT-4o."""
        try:
            # Create optimized prompt
            prompt = f"""Summarize this retail price cut news article in 40 words or less. 
Focus on: retailer name, product/category, discount percentage or amount, and timeframe.
Be specific and factual. Avoid marketing language.

Title: {title}
Source: {source}
Content: {content[:2000]}

Summary:"""
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using mini for cost efficiency
                messages=[
                    {"role": "system", "content": "You are a concise news summarizer focusing on retail price cuts and discounts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60,
                temperature=0.3,  # Lower temperature for more consistent output
                n=1
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Track costs
            self.cost_tracker.add_usage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                model="gpt-4o-mini"
            )
            
            # Validate summary length
            word_count = len(summary.split())
            if word_count > 40:
                # Truncate to 40 words
                words = summary.split()[:40]
                summary = ' '.join(words) + '...'
            
            return summary
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def _save_summary(self, headline_id: int, summary: str, processing_time: float, headline_title: str = "") -> None:
        """Save summary to database with topic classification."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Classify the topic
            topic = self.topic_classifier.classify_topic(summary, headline_title)
            
            cursor.execute("""
                INSERT INTO summaries (headline_id, summary_text, topic, processing_time)
                VALUES (?, ?, ?, ?)
            """, (headline_id, summary, topic, processing_time))
            
            conn.commit()
            logger.info(f"Saved summary for headline {headline_id} with topic: {topic}")
            
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _log_operation(self, summarized: int, total: int) -> None:
        """Log summarization operation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            status = 'success' if summarized > 0 else 'failure'
            message = f"Summarized {summarized} of {total} headlines"
            
            cursor.execute("""
                INSERT INTO processing_log (operation_type, status, message, items_processed)
                VALUES (?, ?, ?, ?)
            """, ('summarize', status, message, summarized))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error logging operation: {e}")
        finally:
            conn.close()
    
    def get_recent_summaries(self, hours: int = 24) -> List[Dict]:
        """Get recent summaries from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.id, s.summary_text, s.created_at,
                   h.title, h.link, h.source, h.published_date
            FROM summaries s
            JOIN headlines h ON s.headline_id = h.id
            WHERE s.created_at >= datetime('now', '-{} hours')
            ORDER BY h.published_date DESC
        """.format(hours))
        
        summaries = []
        for row in cursor.fetchall():
            summaries.append({
                'id': row['id'],
                'summary': row['summary_text'],
                'title': row['title'],
                'link': row['link'],
                'source': row['source'],
                'published_date': row['published_date'],
                'created_at': row['created_at']
            })
        
        conn.close()
        return summaries


class CostTracker:
    """Track OpenAI API usage and costs."""
    
    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        'gpt-4o': {'input': 2.50, 'output': 10.00},
        'gpt-4o-mini': {'input': 0.15, 'output': 0.60}
    }
    
    def __init__(self, cost_file: str = 'openai_costs.json'):
        self.cost_file = cost_file
        self.load_costs()
    
    def load_costs(self) -> None:
        """Load existing cost data."""
        try:
            with open(self.cost_file, 'r') as f:
                self.costs = json.load(f)
        except FileNotFoundError:
            self.costs = {
                'total_input_tokens': 0,
                'total_output_tokens': 0,
                'total_cost': 0.0,
                'daily_costs': {}
            }
    
    def save_costs(self) -> None:
        """Save cost data."""
        with open(self.cost_file, 'w') as f:
            json.dump(self.costs, f, indent=2)
    
    def add_usage(self, prompt_tokens: int, completion_tokens: int, model: str) -> None:
        """Add API usage."""
        # Update totals
        self.costs['total_input_tokens'] += prompt_tokens
        self.costs['total_output_tokens'] += completion_tokens
        
        # Calculate cost
        input_cost = (prompt_tokens / 1_000_000) * self.PRICING[model]['input']
        output_cost = (completion_tokens / 1_000_000) * self.PRICING[model]['output']
        total_cost = input_cost + output_cost
        
        self.costs['total_cost'] += total_cost
        
        # Update daily costs
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.costs['daily_costs']:
            self.costs['daily_costs'][today] = {
                'input_tokens': 0,
                'output_tokens': 0,
                'cost': 0.0
            }
        
        self.costs['daily_costs'][today]['input_tokens'] += prompt_tokens
        self.costs['daily_costs'][today]['output_tokens'] += completion_tokens
        self.costs['daily_costs'][today]['cost'] += total_cost
        
        # Save
        self.save_costs()
        
        logger.info(f"API usage: {prompt_tokens} input, {completion_tokens} output, ${total_cost:.4f}")


if __name__ == "__main__":
    # Test the summarizer
    import sys
    import os
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Check for API key
    if not Config.OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not set in environment")
        sys.exit(1)
    
    # Initialize database if needed
    if not os.path.exists('db.sqlite3'):
        print("Database not found. Please run init_db.py first.")
        sys.exit(1)
    
    # Test summarization
    summarizer = Summarizer()
    count = summarizer.summarize_new_headlines()
    
    print(f"\nSummarized {count} headlines")
    
    # Show recent summaries
    summaries = summarizer.get_recent_summaries(hours=24)
    print(f"\nRecent summaries ({len(summaries)} total):")
    
    for i, summary in enumerate(summaries[:5]):  # Show first 5
        print(f"\n{i+1}. {summary['title']}")
        print(f"   Summary: {summary['summary']}")
        print(f"   Source: {summary['source']}")
        print(f"   Date: {summary['published_date']}")