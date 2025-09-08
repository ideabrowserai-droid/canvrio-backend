#!/usr/bin/env python3
"""
Database Sync Script for CannTech Production Deployment
Exports approved content from local database and prepares for production sync
"""
import sqlite3
import json
import requests
from datetime import datetime
import sys
import os

class DatabaseSyncManager:
    def __init__(self):
        self.local_db = 'content.db'
        self.export_file = 'approved_content_export.sql'
        self.production_api = 'https://canvrio-backend.onrender.com'
    
    def export_approved_content(self):
        """Export approved content from local database to SQL file"""
        print("[EXPORT] Exporting approved content from local database...")
        
        if not os.path.exists(self.local_db):
            raise FileNotFoundError(f"Local database {self.local_db} not found!")
            
        conn = sqlite3.connect(self.local_db)
        cursor = conn.cursor()
        
        # Get approved content
        cursor.execute('''
            SELECT id, title, content, source, category, url, published_date, 
                   created_at, compliance_status, engagement_metrics, content_hash, 
                   approval_timestamp, priority
            FROM content_feeds 
            WHERE compliance_status = 'approved' AND is_active = 1
            ORDER BY approval_timestamp DESC
        ''')
        
        approved_items = cursor.fetchall()
        conn.close()
        
        if not approved_items:
            print("[WARNING] No approved content found to export!")
            return False
            
        print(f"[SUCCESS] Found {len(approved_items)} approved content items")
        
        # Generate SQL export
        with open(self.export_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("-- CannTech Approved Content Export\n")
            f.write(f"-- Generated: {datetime.now().isoformat()}\n")
            f.write(f"-- Total items: {len(approved_items)}\n\n")
            
            # Create table if not exists
            f.write("""-- Ensure content_feeds table exists with proper schema
CREATE TABLE IF NOT EXISTS content_feeds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    source TEXT NOT NULL,
    category TEXT,
    url TEXT,
    published_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    compliance_status TEXT DEFAULT 'pending',
    social_platform TEXT,
    engagement_metrics JSON,
    content_hash VARCHAR(255) UNIQUE,
    approval_timestamp DATETIME,
    priority INTEGER DEFAULT 3
);

-- Clear existing approved content to avoid duplicates
DELETE FROM content_feeds WHERE compliance_status = 'approved';

""")
            
            # Write INSERT statements
            f.write("-- Insert approved content items\n")
            for item in approved_items:
                # Escape single quotes in text fields
                title = item[1].replace("'", "''") if item[1] else ''
                content = item[2].replace("'", "''") if item[2] else ''
                source = item[3].replace("'", "''") if item[3] else ''
                category = item[4] or 'General'
                url = item[5] or ''
                published_date = item[6]
                created_at = item[7] 
                engagement_metrics = item[9] or '{}'
                content_hash = item[10] or ''
                approval_timestamp = item[11]
                priority = item[12] or 3
                
                f.write(f"""INSERT INTO content_feeds (
    title, content, source, category, url, published_date, created_at,
    is_active, compliance_status, engagement_metrics, content_hash,
    approval_timestamp, priority
) VALUES (
    '{title}',
    '{content}',
    '{source}',
    '{category}',
    '{url}',
    '{published_date}',
    '{created_at}',
    1,
    'approved',
    '{engagement_metrics}',
    '{content_hash}',
    '{approval_timestamp}',
    {priority}
);
""")
            
            f.write("\n-- End of export\n")
        
        print(f"[SUCCESS] Export completed: {self.export_file}")
        return True
    
    def test_export_integrity(self):
        """Test the exported SQL file by importing to temporary database"""
        print("[TEST] Testing export integrity...")
        
        if not os.path.exists(self.export_file):
            raise FileNotFoundError(f"Export file {self.export_file} not found!")
        
        # Create temporary test database
        test_db = 'test_export.db'
        if os.path.exists(test_db):
            os.remove(test_db)
            
        try:
            conn = sqlite3.connect(test_db)
            cursor = conn.cursor()
            
            # Execute the export SQL
            with open(self.export_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                # Split by statements and execute
                statements = sql_content.split(';')
                for statement in statements:
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        cursor.execute(statement)
            
            conn.commit()
            
            # Verify imported content
            cursor.execute("SELECT COUNT(*) FROM content_feeds WHERE compliance_status = 'approved'")
            imported_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT title, source FROM content_feeds WHERE compliance_status = 'approved' LIMIT 3")
            sample_items = cursor.fetchall()
            
            conn.close()
            os.remove(test_db)
            
            print(f"[SUCCESS] Export integrity test passed!")
            print(f"   - Imported {imported_count} approved items")
            print("   - Sample items:")
            for title, source in sample_items:
                print(f"     - {title[:50]}... ({source})")
            
            return True
            
        except Exception as e:
            if os.path.exists(test_db):
                os.remove(test_db)
            raise Exception(f"Export integrity test failed: {e}")
    
    def verify_production_api(self):
        """Verify production API is accessible"""
        print("[API] Verifying production API access...")
        
        try:
            response = requests.get(f"{self.production_api}/health", timeout=10)
            response.raise_for_status()
            print("[SUCCESS] Production API accessible")
            return True
        except Exception as e:
            raise Exception(f"Cannot access production API: {e}")
    
    def get_sync_instructions(self):
        """Generate manual sync instructions for production"""
        instructions = f"""
**PRODUCTION DATABASE SYNC INSTRUCTIONS**

1. **Upload Export File:**
   - File: {self.export_file}
   - Upload to production server directory

2. **Execute SQL Import:**
   ```bash
   # Connect to production database
   sqlite3 content.db < {self.export_file}
   
   # Or if using database management tool:
   # Import the {self.export_file} file
   ```

3. **Verify Import:**
   ```bash
   # Check approved content count
   sqlite3 content.db "SELECT COUNT(*) FROM content_feeds WHERE compliance_status='approved';"
   
   # Should return: 19 (or current approved count)
   ```

4. **Test Frontend:**
   - Visit: https://canvrio.ca (or production frontend)
   - Check "Latest Cannabis Intelligence" banner
   - Approved content should now appear

5. **Verify API:**
   ```bash
   curl https://canvrio-backend.onrender.com/api/content/latest?limit=3
   # Should return approved content items
   ```

WARNING: This replaces all existing approved content on production.
SAFE: Only affects 'approved' status items, pending content untouched.
"""
        return instructions

def main():
    """Run the database sync process"""
    sync_manager = DatabaseSyncManager()
    
    try:
        print("[START] Starting CannTech Database Sync Process\n")
        
        # Step 1: Export approved content
        if not sync_manager.export_approved_content():
            print("[ERROR] Export failed - no content to sync")
            return False
            
        # Step 2: Test export integrity  
        sync_manager.test_export_integrity()
        
        # Step 3: Verify production access
        sync_manager.verify_production_api()
        
        # Step 4: Generate sync instructions
        print("\n" + sync_manager.get_sync_instructions())
        
        print("[SUCCESS] Database sync preparation completed successfully!")
        print(f"[NEXT] Next step: Upload {sync_manager.export_file} to production")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Database sync failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)