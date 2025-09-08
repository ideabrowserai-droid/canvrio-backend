#!/usr/bin/env python3
"""
Production Deployment Script for CannTech Daily Sync
Automates the upload and execution of database sync files to production
"""
import os
import sys
import subprocess
import requests
import sqlite3
import time
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionDeployer:
    def __init__(self):
        self.production_api = 'https://canvrio-backend.onrender.com'
        # These would be configured based on your production setup
        self.production_server = os.getenv('PRODUCTION_SERVER', 'your-server.com')
        self.production_user = os.getenv('PRODUCTION_USER', 'deploy')
        self.production_path = os.getenv('PRODUCTION_PATH', '/app')
    
    def deploy_sql_file(self, sql_file):
        """Deploy SQL file to production server and execute"""
        logger.info(f"Starting deployment of {sql_file}")
        
        if not os.path.exists(sql_file):
            logger.error(f"SQL file {sql_file} not found")
            return False
        
        try:
            # Method 1: If using Render.com or similar platform
            if self.is_render_deployment():
                return self.deploy_via_render_api(sql_file)
            
            # Method 2: If using SSH access
            elif self.has_ssh_access():
                return self.deploy_via_ssh(sql_file)
            
            # Method 3: Manual deployment instructions
            else:
                return self.generate_manual_deployment(sql_file)
                
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False
    
    def is_render_deployment(self):
        """Check if this is a Render.com deployment"""
        return 'onrender.com' in self.production_api
    
    def has_ssh_access(self):
        """Check if SSH access is configured"""
        return (
            self.production_server != 'your-server.com' and
            os.getenv('SSH_KEY_PATH') is not None
        )
    
    def deploy_via_render_api(self, sql_file):
        """Deploy via Render.com API (if available)"""
        logger.info("Render.com deployment detected")
        logger.info("Note: Render.com typically requires git-based deployment")
        logger.info("Creating manual deployment package...")
        
        # For Render, we need to commit the SQL file and trigger a deployment
        # This is a simplified approach - actual implementation depends on your setup
        
        deployment_script = f"""
# Render.com Deployment Steps for {sql_file}

## Method 1: Git-based deployment (Recommended for Render)
1. Commit the SQL file to your git repository:
   ```bash
   git add {sql_file}
   git commit -m "Daily content sync - {datetime.now().strftime('%Y-%m-%d')}"
   git push origin main
   ```

2. Render will automatically redeploy your application

3. Add a startup command to execute the SQL:
   ```bash
   # In your Render service settings, add this to the start command:
   sqlite3 content.db < {sql_file} && python simple_main.py
   ```

## Method 2: Manual file upload (if Render supports it)
1. Use Render's file upload feature (if available)
2. Upload {sql_file} to your application directory
3. Execute via SSH or web shell (if available)

## Verification
After deployment, test:
curl {self.production_api}/api/content/latest?limit=3
"""
        
        # Save deployment instructions
        instructions_file = sql_file.replace('.sql', '_RENDER_DEPLOY.md')
        with open(instructions_file, 'w') as f:
            f.write(deployment_script)
        
        logger.info(f"Render deployment instructions saved: {instructions_file}")
        logger.info("Manual deployment required - see instructions file")
        return True
    
    def deploy_via_ssh(self, sql_file):
        """Deploy via SSH to production server"""
        logger.info(f"Deploying via SSH to {self.production_server}")
        
        try:
            # Upload SQL file
            scp_cmd = [
                'scp', 
                sql_file, 
                f"{self.production_user}@{self.production_server}:{self.production_path}/"
            ]
            
            logger.info(f"Uploading: {' '.join(scp_cmd)}")
            result = subprocess.run(scp_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Upload failed: {result.stderr}")
                return False
            
            # Execute SQL on production server
            sql_filename = os.path.basename(sql_file)
            ssh_cmd = [
                'ssh',
                f"{self.production_user}@{self.production_server}",
                f"cd {self.production_path} && sqlite3 content.db < {sql_filename}"
            ]
            
            logger.info(f"Executing: {' '.join(ssh_cmd)}")
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"SQL execution failed: {result.stderr}")
                return False
            
            logger.info("SQL executed successfully on production server")
            
            # Verify deployment
            return self.verify_deployment()
            
        except Exception as e:
            logger.error(f"SSH deployment failed: {e}")
            return False
    
    def generate_manual_deployment(self, sql_file):
        """Generate manual deployment instructions"""
        logger.info("Generating manual deployment instructions")
        
        manual_steps = f"""
# Manual Deployment Instructions for {sql_file}

## Step 1: Upload SQL File
Upload {sql_file} to your production server where content.db is located.

## Step 2: Execute SQL Import
```bash
# On your production server:
sqlite3 content.db < {os.path.basename(sql_file)}
```

## Step 3: Verify Import
```bash
# Check approved content count:
sqlite3 content.db "SELECT COUNT(*) FROM content_feeds WHERE compliance_status='approved';"

# Check sample content:
sqlite3 content.db "SELECT title, source FROM content_feeds WHERE compliance_status='approved' LIMIT 3;"
```

## Step 4: Test API Response
```bash
curl {self.production_api}/api/content/latest?limit=3
```

## Step 5: Verify Frontend
Visit your live website and check that the "Latest Cannabis Intelligence" banner shows updated content.

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        instructions_file = sql_file.replace('.sql', '_MANUAL_DEPLOY.md')
        with open(instructions_file, 'w') as f:
            f.write(manual_steps)
        
        logger.info(f"Manual deployment instructions: {instructions_file}")
        return True
    
    def verify_deployment(self):
        """Verify that deployment was successful"""
        logger.info("Verifying deployment...")
        
        try:
            # Test production API
            response = requests.get(
                f"{self.production_api}/api/content/latest?limit=1",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content_count = data.get('count', 0)
                
                if content_count > 0:
                    logger.info(f"Deployment verified! Production now has {content_count} approved items")
                    return True
                else:
                    logger.warning("Deployment may have failed - API still returns 0 items")
                    return False
            else:
                logger.error(f"API verification failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Deployment verification failed: {e}")
            return False

def main():
    """Main deployment function"""
    if len(sys.argv) < 2:
        print("Usage: python deploy_to_production.py <sql_file>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    
    if not os.path.exists(sql_file):
        print(f"Error: SQL file {sql_file} not found")
        sys.exit(1)
    
    deployer = ProductionDeployer()
    success = deployer.deploy_sql_file(sql_file)
    
    if success:
        logger.info("Deployment completed successfully!")
        sys.exit(0)
    else:
        logger.error("Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()