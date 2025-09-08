#!/usr/bin/env python3
"""
Ecosystem Version Manager
Manages versions and history of the ecosystem ideas prioritized markdown file.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import hashlib

# Configuration
OUTPUT_FILE = "Research/ecosystem-ideas-prioritized.md"
VERSIONS_DIR = "Research/ecosystem-versions"
VERSION_INDEX_FILE = "Research/ecosystem-versions/version-index.json"

class EcosystemVersionManager:
    def __init__(self):
        self.output_path = Path(OUTPUT_FILE)
        self.versions_dir = Path(VERSIONS_DIR)
        self.version_index_path = Path(VERSION_INDEX_FILE)
        self.ensure_directories()
        self.version_index = self.load_version_index()
    
    def ensure_directories(self):
        """Create necessary directories"""
        self.versions_dir.mkdir(parents=True, exist_ok=True)
    
    def load_version_index(self):
        """Load the version index from disk"""
        if self.version_index_path.exists():
            try:
                with open(self.version_index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load version index: {e}")
        
        return {
            "versions": [],
            "latest_version": None,
            "created": datetime.now().isoformat()
        }
    
    def save_version_index(self):
        """Save the version index to disk"""
        try:
            with open(self.version_index_path, 'w', encoding='utf-8') as f:
                json.dump(self.version_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving version index: {e}")
    
    def get_file_hash(self, file_path):
        """Calculate SHA-256 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def extract_metadata_from_file(self, file_path):
        """Extract metadata from the markdown file"""
        metadata = {
            "ideas_count": 0,
            "easy_count": 0,
            "medium_count": 0,
            "hard_count": 0,
            "total_lines": 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                metadata["total_lines"] = len(lines)
                
                # Count difficulty categories
                metadata["easy_count"] = content.count('🟢 Easy Implementation')
                metadata["medium_count"] = content.count('🟡 Medium Implementation')
                metadata["hard_count"] = content.count('🔴 Hard Implementation')
                
                # Look for total ideas count in the file
                for line in lines:
                    if "*Total Ideas Analyzed:" in line:
                        try:
                            count_str = line.split(":")[-1].strip().rstrip("*")
                            metadata["ideas_count"] = int(count_str)
                        except:
                            pass
                
        except Exception as e:
            print(f"Error extracting metadata: {e}")
        
        return metadata
    
    def create_version(self, description="Automated update"):
        """Create a new version of the ecosystem file"""
        if not self.output_path.exists():
            print(f"Output file {self.output_path} does not exist")
            return None
        
        # Calculate file hash
        file_hash = self.get_file_hash(self.output_path)
        if not file_hash:
            return None
        
        # Check if this version already exists
        for version in self.version_index["versions"]:
            if version["hash"] == file_hash:
                print(f"Version with hash {file_hash[:8]}... already exists")
                return version["version_id"]
        
        # Create new version
        timestamp = datetime.now()
        version_id = timestamp.strftime("%Y%m%d_%H%M%S")
        version_filename = f"ecosystem-ideas-v{version_id}.md"
        version_path = self.versions_dir / version_filename
        
        try:
            # Copy file to versions directory
            shutil.copy2(self.output_path, version_path)
            
            # Extract metadata
            metadata = self.extract_metadata_from_file(self.output_path)
            
            # Create version record
            version_record = {
                "version_id": version_id,
                "timestamp": timestamp.isoformat(),
                "filename": version_filename,
                "hash": file_hash,
                "description": description,
                "file_size": self.output_path.stat().st_size,
                "metadata": metadata
            }
            
            # Add to index
            self.version_index["versions"].append(version_record)
            self.version_index["latest_version"] = version_id
            self.version_index["last_updated"] = timestamp.isoformat()
            
            # Save index
            self.save_version_index()
            
            print(f"✅ Created version {version_id}")
            print(f"📁 Saved as: {version_path}")
            print(f"📊 Ideas: {metadata['ideas_count']}, Easy: {metadata['easy_count']}, Medium: {metadata['medium_count']}, Hard: {metadata['hard_count']}")
            
            return version_id
            
        except Exception as e:
            print(f"Error creating version: {e}")
            return None
    
    def list_versions(self):
        """List all versions"""
        if not self.version_index["versions"]:
            print("No versions found")
            return
        
        print(f"\n📚 Ecosystem Ideas Version History")
        print("=" * 60)
        print(f"{'Version':<15} {'Date':<20} {'Ideas':<6} {'E/M/H':<8} {'Description'}")
        print("-" * 60)
        
        for version in reversed(self.version_index["versions"]):
            timestamp = datetime.fromisoformat(version["timestamp"])
            date_str = timestamp.strftime("%Y-%m-%d %H:%M")
            
            metadata = version.get("metadata", {})
            ideas_count = metadata.get("ideas_count", "?")
            easy = metadata.get("easy_count", 0)
            medium = metadata.get("medium_count", 0)
            hard = metadata.get("hard_count", 0)
            emh_str = f"{easy}/{medium}/{hard}"
            
            latest_marker = " (latest)" if version["version_id"] == self.version_index["latest_version"] else ""
            description = version["description"][:30] + "..." if len(version["description"]) > 30 else version["description"]
            
            print(f"{version['version_id']:<15} {date_str:<20} {ideas_count:<6} {emh_str:<8} {description}{latest_marker}")
    
    def restore_version(self, version_id):
        """Restore a specific version"""
        version_record = None
        for version in self.version_index["versions"]:
            if version["version_id"] == version_id:
                version_record = version
                break
        
        if not version_record:
            print(f"Version {version_id} not found")
            return False
        
        version_path = self.versions_dir / version_record["filename"]
        if not version_path.exists():
            print(f"Version file {version_path} not found")
            return False
        
        try:
            # Backup current file first
            if self.output_path.exists():
                backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.output_path.with_suffix(f'.restore_backup_{backup_id}.md')
                shutil.copy2(self.output_path, backup_path)
                print(f"📁 Current file backed up to: {backup_path}")
            
            # Restore the version
            shutil.copy2(version_path, self.output_path)
            print(f"✅ Restored version {version_id} to {self.output_path}")
            return True
            
        except Exception as e:
            print(f"Error restoring version: {e}")
            return False
    
    def cleanup_old_versions(self, keep_count=10):
        """Remove old versions, keeping only the most recent ones"""
        if len(self.version_index["versions"]) <= keep_count:
            print(f"Only {len(self.version_index['versions'])} versions exist, no cleanup needed")
            return
        
        # Sort by timestamp and keep the most recent
        sorted_versions = sorted(
            self.version_index["versions"], 
            key=lambda x: x["timestamp"], 
            reverse=True
        )
        
        versions_to_keep = sorted_versions[:keep_count]
        versions_to_remove = sorted_versions[keep_count:]
        
        removed_count = 0
        for version in versions_to_remove:
            version_path = self.versions_dir / version["filename"]
            try:
                if version_path.exists():
                    version_path.unlink()
                    removed_count += 1
                    print(f"🗑️  Removed old version: {version['version_id']}")
            except Exception as e:
                print(f"Error removing {version['version_id']}: {e}")
        
        # Update index
        self.version_index["versions"] = versions_to_keep
        self.save_version_index()
        
        print(f"✅ Cleanup complete: removed {removed_count} old versions")

def main():
    """Main CLI interface"""
    import sys
    
    manager = EcosystemVersionManager()
    
    if len(sys.argv) < 2:
        print("Ecosystem Version Manager")
        print("\nUsage:")
        print("  python ecosystem_version_manager.py create [description]")
        print("  python ecosystem_version_manager.py list")
        print("  python ecosystem_version_manager.py restore <version_id>")
        print("  python ecosystem_version_manager.py cleanup [keep_count]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        description = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Manual version creation"
        manager.create_version(description)
    
    elif command == "list":
        manager.list_versions()
    
    elif command == "restore":
        if len(sys.argv) < 3:
            print("Error: Please provide version_id to restore")
            sys.exit(1)
        version_id = sys.argv[2]
        manager.restore_version(version_id)
    
    elif command == "cleanup":
        keep_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        manager.cleanup_old_versions(keep_count)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()