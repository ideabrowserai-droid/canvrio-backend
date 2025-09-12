#!/usr/bin/env python3
"""
Daily Database Sync Automation for CannTech Production
Automatically syncs curator-approved content from local to production daily
"""
import sqlite3
import json
import requests
import os
import sys
from datetime import datetime, timedelta
import schedule
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailySyncManager:
    def __init__(self):
        self.local_db = 'content.db'
        self.production_api = 'https://canvrio-backend.onrender.com'
        self.export_dir = 'daily_exports'
        self.ensure_export_directory()
    
    def ensure_export_directory(self):
        """Create exports directory if it doesn't exist"""
        Path(self.export_dir).mkdir(exist_ok=True)
    
    def check_for_new_approvals(self, hours_back=24):
        """Check if there are new approvals in the last N hours"""
        if not os.path.exists(self.local_db):
            logger.warning(f"Local database {self.local_db} not found")
            return False, 0
            
        conn = sqlite3.connect(self.local_db)
        cursor = conn.cursor()
        
        # Check for approvals in the last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        cursor.execute('''
            SELECT COUNT(*) FROM content_feeds 
            WHERE compliance_status = 'approved' 
            AND approval_timestamp > ?
        ''', (cutoff_time.isoformat(),))
        
        new_approvals = cursor.fetchone()[0]
        
        # Also check total approved count
        cursor.execute('''
            SELECT COUNT(*) FROM content_feeds 
            WHERE compliance_status = 'approved' AND is_active = 1
        ''')
        total_approved = cursor.fetchone()[0]
        
        conn.close()
        
        logger.info(f"Found {new_approvals} new approvals in last {hours_back}h, {total_approved} total approved")
        return new_approvals > 0, total_approved
    
    def get_current_production_count(self):
        """Get current number of approved items on production"""
        try:
            response = requests.get(
                f"{self.production_api}/api/content/latest?limit=1",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('count', 0)
            else:
                logger.warning(f"Production API returned status {response.status_code}")
                return -1
        except Exception as e:
            logger.error(f"Failed to check production content count: {e}")
            return -1
    
    def create_daily_export(self):
        """Create daily export of approved content"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = os.path.join(self.export_dir, f"daily_sync_{timestamp}.sql")
        
        logger.info("Creating daily export...")
        
        if not os.path.exists(self.local_db):
            raise FileNotFoundError(f"Local database {self.local_db} not found!")
            
        conn = sqlite3.connect(self.local_db)
        cursor = conn.cursor()
        
        # Get all approved content
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
            logger.warning("No approved content found to export!")
            return None, 0
            
        # Generate SQL export
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(f"-- CannTech Daily Sync Export\n")
            f.write(f"-- Generated: {datetime.now().isoformat()}\n")
            f.write(f"-- Total items: {len(approved_items)}\n\n")
            
            # Ensure table exists
            f.write("""-- Ensure content_feeds table exists
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

-- Clear existing approved content
DELETE FROM content_feeds WHERE compliance_status = 'approved';

""")
            
            # Insert approved content
            f.write("-- Insert approved content items\n")
            for item in approved_items:
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
            
        logger.info(f"Daily export created: {export_file} ({len(approved_items)} items)")
        return export_file, len(approved_items)
    
    def should_run_sync(self):
        """Determine if sync should run based on new content and production state"""
        # Check for new approvals
        has_new_approvals, total_local = self.check_for_new_approvals(hours_back=25)  # Slightly over 24h for overlap
        
        # Check current production state
        production_count = self.get_current_production_count()
        
        logger.info(f"Sync decision: Local={total_local}, Production={production_count}, NewApprovals={has_new_approvals}")
        
        # Run sync if:
        # 1. There are new approvals in last 24h, OR
        # 2. Local has more approved content than production, OR  
        # 3. Production has 0 items but local has approved content
        should_sync = (
            has_new_approvals or 
            (total_local > production_count and production_count >= 0) or
            (production_count == 0 and total_local > 0)
        )
        
        return should_sync, total_local, production_count
    
    def run_daily_sync(self):
        """Main daily sync process"""
        logger.info("=== DAILY SYNC PROCESS STARTED ===")
        
        try:
            # Check if sync is needed
            should_sync, local_count, prod_count = self.should_run_sync()
            
            if not should_sync:
                logger.info(f"Sync not needed - Local: {local_count}, Production: {prod_count}")
                logger.info("=== DAILY SYNC SKIPPED ===")
                return True
            
            logger.info(f"Sync needed - Local: {local_count}, Production: {prod_count}")
            
            # Create export
            export_file, item_count = self.create_daily_export()
            if not export_file:
                logger.warning("No content to sync")
                return True
            
            # Generate deployment instructions
            instructions = self.generate_deployment_instructions(export_file, item_count)
            
            # Save instructions to file
            instructions_file = export_file.replace('.sql', '_DEPLOY.md')
            with open(instructions_file, 'w') as f:
                f.write(instructions)
            
            logger.info(f"Deployment instructions: {instructions_file}")
            logger.info("=== DAILY SYNC EXPORT READY ===")
            logger.info(f"Next step: Execute deployment using {export_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Daily sync failed: {e}")
            return False
    
    def generate_deployment_instructions(self, export_file, item_count):
        """Generate deployment instructions for the daily export"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# Daily Sync Deployment Instructions

**Generated**: {timestamp}  
**Export File**: {export_file}  
**Content Items**: {item_count} approved items  

## Deployment Commands

### 1. Upload to Production Server
```bash
# Upload {export_file} to your production server
scp {export_file} user@production-server:/app/
```

### 2. Execute Database Import
```bash
# On production server:
cd /app
sqlite3 content.db < {os.path.basename(export_file)}
```

### 3. Verify Import
```bash
# Check approved content count
sqlite3 content.db "SELECT COUNT(*) FROM content_feeds WHERE compliance_status='approved';"
# Expected result: {item_count}
```

### 4. Test API Response
```bash
curl https://canvrio-backend.onrender.com/api/content/latest?limit=3
# Should return {item_count} total items
```

### 5. Verify Frontend
- Visit: https://canvrio.ca
- Check "Latest Cannabis Intelligence" banner shows new content

## Automated Deployment (Optional)

If you have SSH access configured, run:
```bash
python deploy_to_production.py {os.path.basename(export_file)}
```

---
*Generated by CannTech Daily Sync Manager*
"""

def setup_daily_schedule():
    """Setup the daily sync schedule"""
    # Schedule daily sync at 8:00 AM
    schedule.every().day.at("08:00").do(lambda: DailySyncManager().run_daily_sync())
    
    # Also allow manual trigger
    schedule.every().day.at("20:00").do(lambda: DailySyncManager().run_daily_sync())
    
    logger.info("Daily sync scheduled for 8:00 AM and 8:00 PM")
    
    # Run scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def manual_sync():
    """Run sync manually"""
    sync_manager = DailySyncManager()
    return sync_manager.run_daily_sync()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        logger.info("Running manual sync...")
        success = manual_sync()
        sys.exit(0 if success else 1)
    elif len(sys.argv) > 1 and sys.argv[1] == "--check":
        sync_manager = DailySyncManager()
        should_sync, local, prod = sync_manager.should_run_sync()
        print(f"Should sync: {should_sync}")
        print(f"Local approved: {local}")  
        print(f"Production approved: {prod}")
        sys.exit(0)
    else:
        logger.info("Starting daily sync scheduler...")
        setup_daily_schedule()