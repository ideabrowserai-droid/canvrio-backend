#!/usr/bin/env python3
"""
Database Migration Script for Canvrio System Consolidation
Adds missing columns and sets proper defaults for existing data
"""

import sqlite3
import json
import hashlib
from datetime import datetime

def migrate_database():
    """Migrate content.db to enhanced schema"""
    db_path = 'content.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    # Enable WAL mode
    cursor.execute('PRAGMA journal_mode=WAL;')
    
    # Add missing columns
    try:
        cursor.execute('ALTER TABLE content_feeds ADD COLUMN engagement_metrics JSON')
        print("Added engagement_metrics column")
    except sqlite3.OperationalError:
        print("engagement_metrics column already exists")
    
    try:
        cursor.execute('ALTER TABLE content_feeds ADD COLUMN content_hash VARCHAR(255)')
        print("Added content_hash column")
    except sqlite3.OperationalError:
        print("content_hash column already exists")
    
    # Create index for content_hash (can't add UNIQUE constraint to existing table in SQLite)
    try:
        cursor.execute('CREATE UNIQUE INDEX idx_content_hash ON content_feeds(content_hash)')
        print("Added unique index on content_hash")
    except sqlite3.OperationalError:
        print("Index on content_hash already exists")
    
    # Update existing records to add missing data
    cursor.execute("""
        SELECT id, title, content, source, category 
        FROM content_feeds 
        WHERE engagement_metrics IS NULL OR content_hash IS NULL
    """)
    
    rows = cursor.fetchall()
    updated_count = 0
    
    for row in rows:
        item_id, title, content, source, category = row
        
        # Generate content hash
        text = f"{title}{content or ''}"
        content_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        # Calculate business relevance score (simplified version)
        business_keywords = [
            'pricing', 'wholesale', 'retail', 'dispensary', 'license', 'compliance',
            'earnings', 'strategy', 'operations', 'regulations', 'health canada'
        ]
        
        text_lower = f"{title} {content or ''}".lower()
        relevance_score = 2.0 + sum(0.5 for keyword in business_keywords if keyword in text_lower)
        
        # Determine category if missing
        if not category:
            if any(k in text_lower for k in ['regulation', 'compliance', 'license']):
                category = 'Regulatory'
            elif any(k in text_lower for k in ['earnings', 'profit', 'revenue']):
                category = 'Business'
            else:
                category = 'Industry Commentary'
        
        # Create engagement metrics
        engagement_metrics = json.dumps({
            'business_relevance_score': min(relevance_score, 10.0),
            'migration_timestamp': datetime.now().isoformat()
        })
        
        # Update the record
        try:
            cursor.execute("""
                UPDATE content_feeds 
                SET engagement_metrics = ?, content_hash = ?, category = ?
                WHERE id = ?
            """, (engagement_metrics, content_hash, category, item_id))
            updated_count += 1
        except sqlite3.IntegrityError:
            # Handle duplicate hash by appending ID
            content_hash = f"{content_hash}_{item_id}"
            cursor.execute("""
                UPDATE content_feeds 
                SET engagement_metrics = ?, content_hash = ?, category = ?
                WHERE id = ?
            """, (engagement_metrics, content_hash, category, item_id))
            updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"Migration completed. Updated {updated_count} records.")
    print("Database is now ready for the unified system.")

if __name__ == "__main__":
    migrate_database()