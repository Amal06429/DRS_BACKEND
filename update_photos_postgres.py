import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from hms_sync.models import Doctor

print("\n" + "="*70)
print("UPDATING PHOTO URLs FOR ALL DOCTORS (PostgreSQL)")
print("="*70 + "\n")

# Get all doctors
doctors = Doctor.objects.all()
updated_count = 0

with connection.cursor() as cursor:
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
                "UPDATE hms_doctors SET photourl = %s WHERE code = %s",
                [photo_url, doctor.code]
            )
            updated_count += 1
            
            if updated_count <= 10 or doctor.code in ['029', '030', '032', '033']:
                print(f"✓ Updated {doctor.code} - {doctor.name}")

print(f"\n... (updated {updated_count} doctors total)")

print("\n" + "="*70)
print(f"SUMMARY: Updated {updated_count} doctors with photo URLs")
print("="*70)

# Verify the specific doctors from the screenshot
print("\nVerifying doctors from screenshot:")
for code in ['029', '030', '032', '033']:
    try:
        doctor = Doctor.objects.get(code=code)
        print(f"  {code} - {doctor.name}")
        print(f"       Photo: {doctor.photourl[:60] if doctor.photourl else 'NULL'}...")
    except Doctor.DoesNotExist:
        print(f"  {code} - NOT FOUND")
