import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import Doctor

# Update doctors with sample photo URLs using UI Avatars service
# This generates avatar images based on the doctor's name

doctors = Doctor.objects.all()
updated_count = 0

print("\n" + "="*70)
print("ADDING SAMPLE PHOTO URLs TO DOCTORS")
print("="*70 + "\n")

for doctor in doctors:
    if doctor.name and doctor.name != "External Dr":
        # Generate a photo URL using UI Avatars (free service)
        # Format: https://ui-avatars.com/api/?name=FirstName+LastName&size=200&background=random
        name_encoded = doctor.name.replace(' ', '+')
        photo_url = f"https://ui-avatars.com/api/?name={name_encoded}&size=200&background=667eea&color=fff&bold=true"
        
        # For some doctors, use pravatar (random avatar images)
        # Alternate between ui-avatars and pravatar for variety
        if updated_count % 3 == 0:
            # Use pravatar for every 3rd doctor
            avatar_id = (updated_count % 70) + 1  # pravatar has 70 images
            photo_url = f"https://i.pravatar.cc/200?img={avatar_id}"
        
        doctor.photourl = photo_url
        doctor.save()
        updated_count += 1
        print(f"✓ Updated {doctor.code} - {doctor.name}")
        print(f"  Photo URL: {photo_url}\n")

print("="*70)
print(f"SUMMARY: Updated {updated_count} doctors with photo URLs")
print("="*70)

# Show some examples
print("\nSample doctors with photos:")
for doctor in Doctor.objects.filter(photourl__isnull=False)[:5]:
    print(f"  • {doctor.code} - {doctor.name}")
    print(f"    {doctor.photourl}\n")
