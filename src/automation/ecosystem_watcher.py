#!/usr/bin/env python3
"""
Ecosystem Ideas Watcher
Monitors the Research/Ecosystem Ideas folder for changes and automatically
updates the prioritized markdown file using Claude Code's research-agent.
"""

import os
import sys
import time
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
import json

# Configuration
ECOSYSTEM_FOLDER = "Research/Ecosystem Ideas"
OUTPUT_FILE = "Research/ecosystem-ideas-prioritized.md"
WATCH_INTERVAL = 5  # seconds
STATE_FILE = ".ecosystem_watcher_state.json"

class EcosystemWatcher:
    def __init__(self):
        self.ecosystem_path = Path(ECOSYSTEM_FOLDER)
        self.output_path = Path(OUTPUT_FILE)
        self.state_file = Path(STATE_FILE)
        self.file_states = {}
        self.load_state()
        
    def load_state(self):
        """Load previous file states from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.file_states = json.load(f)
                print(f"Loaded previous state: {len(self.file_states)} files tracked")
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")
                self.file_states = {}
    
    def save_state(self):
        """Save current file states to disk"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.file_states, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save state file: {e}")
    
    def get_file_hash(self, file_path):
        """Calculate MD5 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def scan_ecosystem_folder(self):
        """Scan ecosystem folder and return file states"""
        current_states = {}
        
        if not self.ecosystem_path.exists():
            print(f"Warning: Ecosystem folder {self.ecosystem_path} does not exist")
            return current_states
        
        for file_path in self.ecosystem_path.rglob('*'):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(Path.cwd()))
                file_hash = self.get_file_hash(file_path)
                if file_hash:
                    current_states[relative_path] = {
                        'hash': file_hash,
                        'modified': file_path.stat().st_mtime,
                        'size': file_path.stat().st_size
                    }
        
        return current_states
    
    def detect_changes(self, current_states):
        """Detect if files have been added, modified, or deleted"""
        changes = {
            'added': [],
            'modified': [],
            'deleted': []
        }
        
        # Check for new and modified files
        for file_path, current_state in current_states.items():
            if file_path not in self.file_states:
                changes['added'].append(file_path)
            elif self.file_states[file_path]['hash'] != current_state['hash']:
                changes['modified'].append(file_path)
        
        # Check for deleted files
        for file_path in self.file_states:
            if file_path not in current_states:
                changes['deleted'].append(file_path)
        
        return changes
    
    def run_claude_analysis(self):
        """Run Claude Code research-agent to analyze ecosystem ideas"""
        print("🤖 Running Claude Code research-agent analysis...")
        
        try:
            # Create the Claude Code command
            claude_prompt = f"""Please review the {ECOSYSTEM_FOLDER} folder and analyze all the ideas provided. I need you to:

1. Thoroughly examine all files and ideas in the ecosystem folder
2. Understand each idea and its potential integration into our project
3. Evaluate the implementation difficulty of each idea (easy, medium, hard)
4. Consider factors like:
   - Technical complexity
   - Dependencies required
   - Development time needed
   - Integration with existing codebase
   - Resource requirements

5. Create a comprehensive markdown file that prioritizes these ideas from easiest to hardest to implement
6. For each idea, include:
   - Brief description
   - Implementation difficulty rating
   - Key requirements/dependencies
   - Estimated effort level
   - Any potential blockers or considerations

7. Update or create the file "{OUTPUT_FILE}" with this prioritized analysis
8. Include a timestamp and version info at the top of the document

Please provide a detailed analysis and create this prioritized list as a well-structured markdown document."""

            # Run Claude Code with the research-agent
            cmd = [
                "claude", "code", 
                "@agent-research-agent", 
                claude_prompt
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Analysis completed successfully")
                return True
            else:
                print(f"❌ Analysis failed with return code: {result.returncode}")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Analysis timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"❌ Error running analysis: {e}")
            return False
    
    def backup_existing_output(self):
        """Create a backup of existing output file"""
        if self.output_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.output_path.with_suffix(f'.backup_{timestamp}.md')
            try:
                import shutil
                shutil.copy2(self.output_path, backup_path)
                print(f"📁 Backed up existing file to: {backup_path}")
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")
    
    def watch(self):
        """Main watch loop"""
        print(f"🔍 Starting ecosystem watcher...")
        print(f"📁 Monitoring: {self.ecosystem_path.absolute()}")
        print(f"📄 Output file: {self.output_path.absolute()}")
        print(f"⏱️  Check interval: {WATCH_INTERVAL} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                current_states = self.scan_ecosystem_folder()
                changes = self.detect_changes(current_states)
                
                if any(changes.values()):
                    print(f"\n📢 Changes detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:")
                    
                    if changes['added']:
                        print(f"  ➕ Added: {', '.join(changes['added'])}")
                    if changes['modified']:
                        print(f"  ✏️  Modified: {', '.join(changes['modified'])}")
                    if changes['deleted']:
                        print(f"  ❌ Deleted: {', '.join(changes['deleted'])}")
                    
                    # Backup existing output
                    self.backup_existing_output()
                    
                    # Run analysis
                    if self.run_claude_analysis():
                        print("🎉 Ecosystem ideas analysis updated successfully!")
                    else:
                        print("⚠️  Analysis failed - will retry on next change")
                    
                    # Update our tracked states
                    self.file_states = current_states
                    self.save_state()
                    print()
                
                time.sleep(WATCH_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n👋 Stopping ecosystem watcher...")
            self.save_state()
            print("State saved. Goodbye!")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--run-once':
            # Run analysis once and exit
            watcher = EcosystemWatcher()
            watcher.backup_existing_output()
            success = watcher.run_claude_analysis()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--help':
            print("Ecosystem Ideas Watcher")
            print("Usage:")
            print("  python ecosystem_watcher.py         # Start watching for changes")
            print("  python ecosystem_watcher.py --run-once  # Run analysis once and exit")
            print("  python ecosystem_watcher.py --help      # Show this help")
            sys.exit(0)
    
    # Start watching
    watcher = EcosystemWatcher()
    watcher.watch()

if __name__ == "__main__":
    main()