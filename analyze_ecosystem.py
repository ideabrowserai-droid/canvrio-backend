#!/usr/bin/env python3
"""
Ecosystem Ideas Analyzer
Standalone script to analyze ecosystem ideas using Claude Code research-agent.
This script can be run manually or called by the watcher.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Configuration
ECOSYSTEM_FOLDER = "Research/Ecosystem Ideas"
OUTPUT_FILE = "Research/ecosystem-ideas-prioritized.md"

def count_ideas():
    """Count the number of idea files in the ecosystem folder"""
    ecosystem_path = Path(ECOSYSTEM_FOLDER)
    if not ecosystem_path.exists():
        return 0
    
    idea_files = list(ecosystem_path.rglob('*'))
    idea_files = [f for f in idea_files if f.is_file()]
    return len(idea_files)

def create_backup():
    """Create a timestamped backup of the existing output file"""
    output_path = Path(OUTPUT_FILE)
    if output_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = output_path.with_suffix(f'.backup_{timestamp}.md')
        try:
            import shutil
            shutil.copy2(output_path, backup_path)
            print(f"Created backup: {backup_path}")
            return str(backup_path)
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
            return None
    return None

def run_analysis():
    """Run Claude Code research-agent to analyze ecosystem ideas"""
    print("Starting ecosystem ideas analysis...")
    
    # Count ideas
    idea_count = count_ideas()
    print(f"Found {idea_count} idea files to analyze")
    
    if idea_count == 0:
        print("No idea files found in ecosystem folder")
        return False
    
    # Create backup
    create_backup()
    
    # Prepare the analysis prompt
    claude_prompt = f"""Review the {ECOSYSTEM_FOLDER} folder and analyze all the ideas provided. Create a comprehensive prioritization analysis:

## Analysis Requirements:

1. **Examine all files** in the ecosystem folder thoroughly
2. **Understand each idea** and its potential integration into our CannTech project
3. **Evaluate implementation difficulty** using this scale:
   - 🟢 **Easy** (1-2 weeks, minimal dependencies)
   - 🟡 **Medium** (1-2 months, moderate complexity)
   - 🔴 **Hard** (3+ months, high complexity/dependencies)

4. **Consider these factors**:
   - Technical complexity and architecture changes needed
   - Dependencies and external integrations required
   - Development time and resource requirements
   - Integration complexity with existing FastAPI/SQLAlchemy codebase
   - Potential revenue impact and business value
   - Risk factors and potential blockers

5. **Create the file** `{OUTPUT_FILE}` with this structure:

```markdown
# Ecosystem Ideas - Implementation Priority Analysis

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Total Ideas Analyzed: {idea_count}*

## Executive Summary
[Brief overview of the analysis and top recommendations]

## 🟢 Easy Implementation (1-2 weeks)
### [Idea Name]
- **Description**: [Brief description]
- **Effort**: [Specific time estimate]
- **Dependencies**: [List key requirements]
- **Integration**: [How it fits with existing code]
- **Business Value**: [Revenue/user benefit potential]
- **Implementation Notes**: [Key technical considerations]

## 🟡 Medium Implementation (1-2 months)
[Same structure as above]

## 🔴 Hard Implementation (3+ months)
[Same structure as above]

## Implementation Roadmap
[Suggested order of implementation with reasoning]

## Technical Considerations
[Overall technical notes, architecture implications, etc.]
```

6. **Prioritize within each difficulty level** by business value and strategic fit
7. **Include specific technical details** about integration with our existing FastAPI/SQLAlchemy/SQLite stack
8. **Add implementation roadmap** suggesting the optimal order

Please analyze thoroughly and create this comprehensive prioritization document."""

    try:
        # Prepare command for subprocess (using direct prompt)
        print("Running Claude Code analysis...")
        
        # For now, we'll create a temporary prompt file and call claude code
        temp_prompt_file = ".temp_ecosystem_prompt.txt"
        with open(temp_prompt_file, 'w', encoding='utf-8') as f:
            f.write(claude_prompt)
        
        # Run Claude Code
        cmd = ["claude", "code", "@agent-research-agent", f"@{temp_prompt_file}"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        # Clean up temp file
        try:
            os.remove(temp_prompt_file)
        except:
            pass
        
        if result.returncode == 0:
            print("Analysis completed successfully!")
            print(f"Output saved to: {OUTPUT_FILE}")
            return True
        else:
            print(f"Analysis failed with return code: {result.returncode}")
            if result.stderr:
                print(f"Error details: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Analysis timed out after 10 minutes")
        return False
    except FileNotFoundError:
        print("Claude Code CLI not found. Please ensure 'claude' is in your PATH")
        print("   Install instructions: https://docs.anthropic.com/en/docs/claude-code")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def show_help():
    """Show help information"""
    print("""
Ecosystem Ideas Analyzer

This script analyzes all idea files in the Research/Ecosystem Ideas folder
and creates a prioritized implementation plan using Claude Code's research-agent.

Usage:
  python analyze_ecosystem.py              # Run analysis
  python analyze_ecosystem.py --help       # Show this help
  python analyze_ecosystem.py --count      # Count idea files only

Features:
- Automatic backup of existing analysis
- Comprehensive difficulty rating (Easy/Medium/Hard)
- Business value assessment
- Technical integration analysis
- Implementation roadmap suggestions

Output: Research/ecosystem-ideas-prioritized.md
""")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            show_help()
            sys.exit(0)
        elif sys.argv[1] == '--count':
            count = count_ideas()
            print(f"Found {count} idea files in {ECOSYSTEM_FOLDER}")
            sys.exit(0)
    
    print("Ecosystem Ideas Analyzer")
    print("=" * 50)
    
    success = run_analysis()
    
    if success:
        print("\nAnalysis complete! Check the output file for your prioritized roadmap.")
        output_path = Path(OUTPUT_FILE)
        if output_path.exists():
            print(f"File location: {output_path.absolute()}")
            print(f"File size: {output_path.stat().st_size} bytes")
    else:
        print("\nAnalysis failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()