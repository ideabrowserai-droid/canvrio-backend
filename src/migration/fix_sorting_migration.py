#!/usr/bin/env python3
"""
Database migration to fix the sorting problem
Adds approval_timestamp column and updates approval logic
"""

import sqlite3
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Add approval_timestamp column to content_feeds table"""
    db_path = 'content.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable WAL mode
        cursor.execute('PRAGMA journal_mode=WAL;')
        
        # Add approval_timestamp column if it doesn't exist
        try:
            cursor.execute('ALTER TABLE content_feeds ADD COLUMN approval_timestamp DATETIME')
            logger.info("✅ Added approval_timestamp column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                logger.info("✅ approval_timestamp column already exists")
            else:
                raise e
        
        # Update existing approved content to have approval timestamps
        # Set approval_timestamp to created_at for existing approved content
        cursor.execute('''
            UPDATE content_feeds 
            SET approval_timestamp = created_at 
            WHERE compliance_status = 'approved' 
            AND approval_timestamp IS NULL
        ''')
        updated_count = cursor.rowcount
        logger.info(f"✅ Updated {updated_count} existing approved items with approval timestamps")
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    migrate_database()