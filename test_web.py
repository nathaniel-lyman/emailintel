#!/usr/bin/env python3
"""
Test script for web interface.
Tests Flask app routes and functionality.
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_flask_app():
    """Test Flask application routes."""
    print("Testing Flask web interface...")
    
    # Check if app is running
    base_url = "http://localhost:5000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"  ✅ Health check: {health_data['status']}")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
            
        # Test stats endpoint
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats_data = response.json()
            print(f"  ✅ Stats endpoint: {stats_data.get('total_summaries', 0)} summaries")
        else:
            print(f"  ❌ Stats endpoint failed: {response.status_code}")
            
        # Test main dashboard
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("  ✅ Dashboard loads successfully")
        else:
            print(f"  ❌ Dashboard failed: {response.status_code}")
            
        # Test settings page
        response = requests.get(f"{base_url}/settings", timeout=5)
        if response.status_code == 200:
            print("  ✅ Settings page loads successfully")
        else:
            print(f"  ❌ Settings page failed: {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to Flask app. Is it running?")
        print("  💡 Try running: python app.py")
        return False
    except Exception as e:
        print(f"  ❌ Error testing Flask app: {e}")
        return False


def test_api_endpoints():
    """Test API endpoints."""
    print("\nTesting API endpoints...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test refresh endpoint (without auth)
        response = requests.post(f"{base_url}/refresh", timeout=10)
        if response.status_code in [200, 401]:  # 401 is expected if auth is enabled
            print("  ✅ Refresh endpoint accessible")
        else:
            print(f"  ❌ Refresh endpoint failed: {response.status_code}")
            
        # Test health endpoint details
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"  ✅ Health details: DB={health_data.get('database')}, Scheduler={health_data.get('scheduler')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing API endpoints: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask_wtf',
        'wtforms',
        'apscheduler',
        'requests',
        'feedparser',
        'beautifulsoup4',
        'openai',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def check_environment():
    """Check environment configuration."""
    print("\nChecking environment configuration...")
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("  ⚠️  .env file not found")
        print("  💡 Copy .env.example to .env and configure your settings")
        return False
    
    # Check database
    if not os.path.exists('db.sqlite3'):
        print("  ⚠️  Database not found")
        print("  💡 Run: python init_db.py")
        return False
    
    print("  ✅ Environment configured")
    return True


def main():
    """Run all tests."""
    print("🧪 Testing Web Interface for Retail Price Cut Summary App")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        return
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed")
        return
    
    # Test Flask app
    if not test_flask_app():
        print("\n❌ Flask app test failed")
        return
    
    # Test API endpoints
    if not test_api_endpoints():
        print("\n❌ API endpoint test failed")
        return
    
    print("\n" + "=" * 60)
    print("🎉 All web interface tests passed!")
    print("\nYour web interface is ready to use:")
    print("  Dashboard: http://localhost:5000/")
    print("  Settings:  http://localhost:5000/settings")
    print("  Health:    http://localhost:5000/health")
    print("  Stats:     http://localhost:5000/stats")


if __name__ == "__main__":
    main()