import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from hms_sync.models import Doctor

# Connect directly to SQLite database
db_path = settings.DATABASES['default']['NAME']
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "="*70)
print("UPDATING PHOTO URLs USING RAW SQL")
print("="*70 + "\n")

# Check if photourl column exists
cursor.execute("PRAGMA table_info(hms_doctors)")
columns = cursor.fetchall()
has_photourl = any(col[1] == 'photourl' for col in columns)

if not has_photourl:
    print("❌ photourl column does not exist in hms_doctors table!")
    print("Run migration first: python manage.py migrate hms_sync")
    conn.close()
    exit(1)

# Get all doctors
doctors = Doctor.objects.all()
updated_count = 0

for doctor in doctors:
    if doctor.name and doctor.name != "External Dr":
        # Generate photo URL
        name_encoded = doctor.name.replace(' ', '+')
        
        if updated_count % 3 == 0:
            # Use pravatar for every 3rd doctor
            avatar_id = (updated_count % 70) + 1
            photo_url = f"https://i.pravatar.cc/200?img={avatar_id}"
        else:
            # Use ui-avatars
            photo_url = f"https://ui-avatars.com/api/?name={name_encoded}&size=200&background=667eea&color=fff&bold=true"
        
        # Update using raw SQL
        cursor.execute(
            "UPDATE hms_doctors SET photourl = ? WHERE code = ?",
            (photo_url, doctor.code)
        )
        updated_count += 1
        print(f"✓ Updated {doctor.code} - {doctor.name}")

# Commit changes
conn.commit()
conn.close()

print("\n" + "="*70)
print(f"SUMMARY: Updated {updated_count} doctors with photo URLs using raw SQL")
print("="*70)

# Verify a few doctors
print("\nVerifying updates:")
for code in ['004', '029', '030', '032', '033']:
    try:
        doctor = Doctor.objects.get(code=code)
        print(f"  {code} - {doctor.name}: {doctor.photourl[:60] if doctor.photourl else 'NULL'}...")
    except Doctor.DoesNotExist:
        pass
