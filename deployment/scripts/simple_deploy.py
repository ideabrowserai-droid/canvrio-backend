#!/usr/bin/env python3
"""
Simple Windows-Compatible Deployment Script for CannTech Daily Sync
Works without external dependencies like sqlite3 command line
"""
import sqlite3
import os
import sys
import json
from datetime import datetime

def deploy_sql_file(sql_file):
    """Deploy SQL file to local database for testing/preparation"""
    print("=" * 50)
    print("CannTech Simple Deployment Script")
    print("=" * 50)
    print(f"SQL File: {sql_file}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if not os.path.exists(sql_file):
        print(f"ERROR: SQL file {sql_file} not found!")
        return False
    
    # Step 1: Backup current database
    print("[1/5] Backing up current database...")
    backup_name = f"content_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    if os.path.exists('content.db'):
        import shutil
        shutil.copy2('content.db', backup_name)
        print(f"     Backup created: {backup_name}")
    else:
        print("     No existing database found")
    
    # Step 2: Execute SQL import
    print("\n[2/5] Executing SQL import...")
    try:
        conn = sqlite3.connect('content.db')
        cursor = conn.cursor()
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Execute the SQL script
        cursor.executescript(sql_content)
        conn.commit()
        
        print("     SQL import successful!")
        
        # Step 3: Verify import
        print("\n[3/5] Verifying import...")
        cursor.execute("SELECT COUNT(*) FROM content_feeds WHERE compliance_status = 'approved'")
        approved_count = cursor.fetchone()[0]
        print(f"     Approved content count: {approved_count}")
        
        # Get sample content
        cursor.execute("SELECT title, source FROM content_feeds WHERE compliance_status = 'approved' LIMIT 3")
        samples = cursor.fetchall()
        print("     Sample approved items:")
        for title, source in samples:
            print(f"       - {title[:50]}... ({source})")
        
        conn.close()
        
    except Exception as e:
        print(f"     ERROR: SQL import failed - {e}")
        return False
    
    # Step 4: Test production API
    print("\n[4/5] Testing production API...")
    try:
        import requests
        response = requests.get('https://canvrio-backend.onrender.com/api/content/latest?limit=1', timeout=10)
        if response.status_code == 200:
            data = response.json()
            prod_count = data.get('count', 0)
            print(f"     Production currently has: {prod_count} approved items")
        else:
            print(f"     Production API returned status: {response.status_code}")
    except ImportError:
        print("     Skipping API test (requests not available)")
    except Exception as e:
        print(f"     Warning: Could not test production API - {e}")
    
    # Step 5: Generate next steps
    print("\n[5/5] Generating next steps...")
    
    next_steps = f"""
DEPLOYMENT TO PRODUCTION NEEDED:

This script updated your LOCAL database successfully.
To sync to production, you need to upload the database:

METHOD 1 - Upload Database File:
1. Upload your updated content.db to production server
2. Replace the production content.db with your updated file

METHOD 2 - Upload SQL File:  
1. Upload {sql_file} to production server
2. Execute: sqlite3 content.db < {os.path.basename(sql_file)}

METHOD 3 - Manual SQL (Render/Vercel):
1. Access production database admin panel
2. Execute the SQL from {sql_file} manually

VERIFICATION:
- Test: https://canvrio-backend.onrender.com/api/content/latest?limit=3
- Visit: https://canvrio.ca to see updated content

Local database now has {approved_count} approved items ready for production.
"""
    
    with open('deployment_next_steps.txt', 'w') as f:
        f.write(next_steps)
    
    print("     Next steps saved to: deployment_next_steps.txt")
    
    print("\n" + "=" * 50)
    print("LOCAL DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print(f"\nLocal database updated with {approved_count} approved items")
    print("Check deployment_next_steps.txt for production upload instructions")
    
    return True

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python simple_deploy.py <sql_file>")
        print("Example: python simple_deploy.py daily_exports\\daily_sync_20250905_145005.sql")
        return False
    
    sql_file = sys.argv[1]
    return deploy_sql_file(sql_file)

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    print("\nPress Enter to continue...")
    input()