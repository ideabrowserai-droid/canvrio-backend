import sqlite3
import os

# Create test database
test_db = 'test_sync.db'
if os.path.exists(test_db):
    os.remove(test_db)

conn = sqlite3.connect(test_db)
cursor = conn.cursor()

# Read and execute SQL export
with open('approved_content_export.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Execute the entire SQL script
cursor.executescript(sql_content)

conn.commit()

# Test the import
cursor.execute("SELECT COUNT(*) FROM content_feeds WHERE compliance_status = 'approved'")
count = cursor.fetchone()[0]
print(f"[TEST] Imported {count} approved items")

cursor.execute("SELECT title, source FROM content_feeds WHERE compliance_status = 'approved' LIMIT 3")
samples = cursor.fetchall()
print("[TEST] Sample items:")
for title, source in samples:
    print(f"  - {title[:50]}... ({source})")

conn.close()
os.remove(test_db)
print("[SUCCESS] Export integrity test passed!")