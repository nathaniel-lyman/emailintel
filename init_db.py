#!/usr/bin/env python3
"""
Database initialization script for Retail Price Cut Summary App.
Creates the SQLite database and applies the schema.
"""

import sqlite3
import os
from datetime import datetime

def init_database(db_path='db.sqlite3'):
    """Initialize the database with the schema."""
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        # Execute the schema
        cursor.executescript(schema)
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Database initialized successfully!")
        print("Created tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if default settings were inserted
        cursor.execute("SELECT keywords, domains FROM settings WHERE id = 1;")
        settings = cursor.fetchone()
        if settings:
            print("\nDefault settings loaded:")
            print(f"  Keywords: {settings[0]}")
            print(f"  Domains: {settings[1]}")
        
        # Log the initialization
        cursor.execute("""
            INSERT INTO processing_log (operation_type, status, message)
            VALUES (?, ?, ?);
        """, ('database_init', 'success', 'Database initialized successfully'))
        
        conn.commit()
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def reset_database(db_path='db.sqlite3'):
    """Reset the database by dropping all tables and reinitializing."""
    
    if os.path.exists(db_path):
        print(f"Removing existing database at {db_path}")
        os.remove(db_path)
    
    init_database(db_path)


def check_database_health(db_path='db.sqlite3'):
    """Check database health and integrity."""
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check PRAGMA integrity
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        if result[0] != 'ok':
            print(f"Database integrity check failed: {result[0]}")
            return False
        
        # Check required tables exist
        required_tables = ['headlines', 'summaries', 'settings', 'processing_log']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = set(required_tables) - set(existing_tables)
        if missing_tables:
            print(f"Missing required tables: {missing_tables}")
            return False
        
        print("Database health check passed!")
        return True
        
    except Exception as e:
        print(f"Error checking database health: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'reset':
            reset_database()
        elif sys.argv[1] == 'check':
            check_database_health()
        else:
            print("Usage: python init_db.py [reset|check]")
    else:
        # Default action: initialize database
        if os.path.exists('db.sqlite3'):
            print("Database already exists. Use 'python init_db.py reset' to reset it.")
            check_database_health()
        else:
            init_database()