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
print("ADDING PHOTOURL COLUMN TO HMS_DOCTORS TABLE")
print("="*70 + "\n")

# Check if photourl column exists
cursor.execute("PRAGMA table_info(hms_doctors)")
columns = cursor.fetchall()
print("Current columns in hms_doctors:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

has_photourl = any(col[1] == 'photourl' for col in columns)

if not has_photourl:
    print("\nAdding photourl column...")
    try:
        cursor.execute("ALTER TABLE hms_doctors ADD COLUMN photourl TEXT")
        conn.commit()
        print("✓ Successfully added photourl column!")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.close()
        exit(1)
else:
    print("\n✓ photourl column already exists!")

conn.close()

print("\n" + "="*70)
print("DONE")
print("="*70)
