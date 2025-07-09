#!/usr/bin/env python3
"""
Database migration script to add topic classification to existing summaries.
Adds the topic column and classifies existing summaries.
"""

import sqlite3
import os
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_add_topic_column(db_path=None):
    """Add topic column to summaries table if it doesn't exist."""
    
    if db_path is None:
        db_path = Config.DATABASE_PATH
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if topic column already exists
        cursor.execute("PRAGMA table_info(summaries)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'topic' not in columns:
            logger.info("Adding topic column to summaries table...")
            cursor.execute("""
                ALTER TABLE summaries 
                ADD COLUMN topic TEXT DEFAULT 'General'
            """)
            
            # Create index for topic column
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_summaries_topic ON summaries(topic)
            """)
            
            conn.commit()
            logger.info("Topic column added successfully!")
        else:
            logger.info("Topic column already exists")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def classify_existing_summaries(db_path=None):
    """Classify existing summaries that don't have topics."""
    
    if db_path is None:
        db_path = Config.DATABASE_PATH
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get summaries without topics or with 'General' topic
        cursor.execute("""
            SELECT s.id, s.summary_text, h.title
            FROM summaries s
            JOIN headlines h ON s.headline_id = h.id
            WHERE s.topic IS NULL OR s.topic = 'General'
        """)
        
        summaries = cursor.fetchall()
        
        if not summaries:
            logger.info("No summaries need topic classification")
            return True
        
        logger.info(f"Classifying topics for {len(summaries)} summaries...")
        
        # Import after checking if we have work to do
        from summarizer import TopicClassifier
        classifier = TopicClassifier()
        
        classified_count = 0
        for summary in summaries:
            try:
                # Classify the summary
                topic = classifier.classify_topic(summary['summary_text'], summary['title'])
                
                # Update the database
                cursor.execute("""
                    UPDATE summaries 
                    SET topic = ? 
                    WHERE id = ?
                """, (topic, summary['id']))
                
                classified_count += 1
                
                if classified_count % 10 == 0:
                    logger.info(f"Classified {classified_count}/{len(summaries)} summaries...")
                    
            except Exception as e:
                logger.error(f"Error classifying summary {summary['id']}: {e}")
        
        conn.commit()
        logger.info(f"Successfully classified {classified_count} summaries!")
        return True
        
    except Exception as e:
        logger.error(f"Error during topic classification: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    
    # Migrate database schema
    if not migrate_add_topic_column():
        print("Failed to migrate database schema")
        sys.exit(1)
    
    # Classify existing summaries
    if not classify_existing_summaries():
        print("Failed to classify existing summaries")
        sys.exit(1)
    
    print("Migration completed successfully!")