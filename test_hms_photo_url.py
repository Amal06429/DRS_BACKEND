"""
Test Script: Add Real HMS Photo URL and Verify Display

This script demonstrates how to add actual doctor photos from HMS
and verify they appear correctly in the DRS system.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from hms_sync.models import Doctor
from doctors.serializers import DoctorSerializer
import json

print("\n" + "="*80)
print("HMS PHOTO URL TEST")
print("="*80 + "\n")

# Test with a real HMS photo URL format
test_doctors = [
    {
        'code': '029',
        'name': 'STEPHEENA K CYRIAC',
        'photo_url': 'https://your-hms-server.com/photos/doctors/029.jpg'
    },
    {
        'code': '030',
        'name': 'SUBIN DILEEP MBBS',
        'photo_url': 'https://your-hms-server.com/photos/doctors/030.jpg'
    },
]

print("STEP 1: Adding HMS Photo URLs")
print("-" * 80)

with connection.cursor() as cursor:
    for doc in test_doctors:
        # Update with HMS photo URL
        cursor.execute(
            "UPDATE hms_doctors SET photourl = %s WHERE code = %s",
            [doc['photo_url'], doc['code']]
        )
        print(f"✓ Updated {doc['code']} - {doc['name']}")
        print(f"  Photo URL: {doc['photo_url']}\n")

print("\nSTEP 2: Verify Database")
print("-" * 80)

for doc_info in test_doctors:
    doctor = Doctor.objects.get(code=doc_info['code'])
    print(f"Doctor: {doctor.name} ({doctor.code})")
    print(f"PhotoURL in DB: {doctor.photourl}\n")

print("\nSTEP 3: Check API Response")
print("-" * 80)

for doc_info in test_doctors:
    doctor = Doctor.objects.get(code=doc_info['code'])
    serializer = DoctorSerializer(doctor)
    print(f"Doctor: {doctor.name}")
    print(json.dumps(serializer.data, indent=2))
    print("\n" + "-" * 80 + "\n")

print("\nSTEP 4: Frontend Display")
print("-" * 80)
print("The frontend will:")
print("✓ Receive photo_url from API")
print("✓ Display <img src='https://your-hms-server.com/photos/doctors/029.jpg' />")
print("✓ Show doctor photo (if URL is accessible)")
print("✓ Show initials placeholder (if URL returns 404)")

print("\n" + "="*80)  
print("HOW HMS SHOULD SYNC PHOTOS")
print("="*80)
print("""
When HMS syncs doctor data to DRS, include the photourl field:

Example HMS Sync Code:
---------------------
INSERT INTO hms_doctors (code, name, rate, department, qualification, photourl, synced_at)
VALUES ('029', 'STEPHEENA K CYRIAC', 150.0, 'RMO', 'M.B.B.S', 
        'https://your-hms-server.com/photos/doctors/029.jpg',
        '2026-03-12 10:30:00')
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    photourl = EXCLUDED.photourl,
    synced_at = EXCLUDED.synced_at;

Photo URL Options:
-----------------
1. HTTP URL:    'https://hms-server.com/photos/029.jpg'
2. HTTPS URL:   'https://secure-hms.com/api/photos/029'
3. Local Path:  '/media/hms_photos/029.jpg' (if photos copied to DRS server)
4. Cloud CDN:   'https://cdn.hospital.com/doctors/029.jpg'

All these formats work! The DRS will display whatever URL HMS provides.
""")

print("\n" + "="*80)
print("TO CLEAR TEST DATA")
print("="*80)
print("Run: python manage.py shell -c \"")
print("from django.db import connection;")
print("cursor = connection.cursor();")
print("cursor.execute('UPDATE hms_doctors SET photourl = NULL');")
print("print('Cleared test photo URLs')\"")
print("\n")
