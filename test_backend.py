#!/usr/bin/env python3
"""
Test script for backend modules.
Tests configuration, scraping, summarization, and email functionality.
"""

import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_config():
    """Test configuration module."""
    print("Testing configuration module...")
    
    try:
        from config import Config, SettingsManager
        
        # Test config validation
        config = Config()
        errors = config.validate()
        
        if errors:
            print("  ⚠️  Configuration validation errors:")
            for error in errors:
                print(f"    - {error}")
        else:
            print("  ✅ Configuration validation passed")
        
        # Test settings manager
        manager = SettingsManager()
        settings = manager.load_settings()
        
        print(f"  ✅ Settings loaded: {len(settings['keywords'].split(','))} keywords")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


def test_database():
    """Test database connectivity."""
    print("Testing database connectivity...")
    
    try:
        # Initialize database if needed
        if not os.path.exists('db.sqlite3'):
            from init_db import init_database
            init_database()
            print("  ✅ Database initialized")
        else:
            print("  ✅ Database exists")
        
        # Test database health
        from init_db import check_database_health
        if check_database_health():
            print("  ✅ Database health check passed")
            return True
        else:
            print("  ❌ Database health check failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False


def test_scraper():
    """Test scraper module."""
    print("Testing scraper module...")
    
    try:
        from scraper import NewsScraper
        
        scraper = NewsScraper()
        
        # Test with limited scraping
        print("  🔍 Testing news scraping (limited)...")
        articles = scraper.scrape_news(hours_back=1)  # Limited to 1 hour
        
        print(f"  ✅ Scraper test completed: found {len(articles)} articles")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Scraper test failed: {e}")
        return False


def test_summarizer():
    """Test summarizer module."""
    print("Testing summarizer module...")
    
    try:
        from summarizer import Summarizer
        from config import Config
        
        if not Config.OPENAI_API_KEY:
            print("  ⚠️  OpenAI API key not configured - skipping summarizer test")
            return True
        
        summarizer = Summarizer()
        
        # Test with existing headlines
        count = summarizer.summarize_new_headlines()
        print(f"  ✅ Summarizer test completed: processed {count} headlines")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Summarizer test failed: {e}")
        return False


def test_emailer():
    """Test emailer module."""
    print("Testing emailer module...")
    
    try:
        from emailer import DailyDigest, EmailSender
        from config import Config
        
        # Check email configuration
        has_smtp = all([Config.SMTP_USERNAME, Config.SMTP_PASSWORD, 
                       Config.SMTP_FROM_EMAIL, Config.SMTP_TO_EMAIL])
        has_sendgrid = all([Config.SENDGRID_API_KEY, Config.SENDGRID_FROM_EMAIL, 
                           Config.SENDGRID_TO_EMAIL])
        
        if not (has_smtp or has_sendgrid):
            print("  ⚠️  Email configuration not complete - skipping email test")
            return True
        
        # Test email sender initialization
        sender = EmailSender()
        print(f"  ✅ Email sender initialized: {'SendGrid' if sender.use_sendgrid else 'SMTP'}")
        
        # Test digest generation (without sending)
        digest = DailyDigest()
        print("  ✅ Daily digest initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Email test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing backend modules for Retail Price Cut Summary App")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_config),
        ("Database", test_database),
        ("Scraper", test_scraper),
        ("Summarizer", test_summarizer),
        ("Emailer", test_emailer),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All backend modules are working correctly!")
        print("You can now proceed to Phase 3: Web Interface")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration and try again.")
        print("Make sure you have:")
        print("  - Created a .env file with your credentials")
        print("  - Installed all dependencies: pip install -r requirements.txt")
        print("  - Activated your virtual environment")


if __name__ == "__main__":
    main()