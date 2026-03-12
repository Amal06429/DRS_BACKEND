import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import Doctor
from doctors.serializers import DoctorSerializer
import json

print("\n" + "="*70)
print("API RESPONSE TEST - RMO DEPARTMENT DOCTORS")
print("="*70 + "\n")

# Get doctors from RMO department (the ones in the screenshot)
doctors = Doctor.objects.filter(department='RMO')[:4]

for doctor in doctors:
    serializer = DoctorSerializer(doctor)
    print(f"Doctor: {doctor.name} ({doctor.code})")
    print(json.dumps(serializer.data, indent=2))
    print("\n" + "-"*70 + "\n")
