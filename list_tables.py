import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings

# Connect directly to SQLite database
db_path = settings.DATABASES['default']['NAME']
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "="*70)
print("DATABASE TABLES")
print("="*70 + "\n")

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("All tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Check for HMS tables specifically
print("\nHMS-related tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'hms%'")
hms_tables = cursor.fetchall()
for table in hms_tables:
    print(f"  - {table[0]}")
    # Show columns
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"      • {col[1]} ({col[2]})")

conn.close()
