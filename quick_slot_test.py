#!/usr/bin/env python
"""Quick test of slot generation"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from datetime import date
from appointments.slot_utils import generate_slots
from hms_sync.models import DoctorTiming

# Test with doctor 001 on Sunday (2026-04-19)
print("\n=== Testing Doctor 001 on Sunday (2026-04-19) ===")
slots = generate_slots('001', date(2026, 4, 19))
print(f"Generated {len(slots)} slots")
if slots:
    for i, slot in enumerate(slots[:5]):
        print(f"  Slot {i+1}: {slot['start_time']}-{slot['end_time']} ({slot['status']})")

# Check what timings exist for doctor 001
print("\n=== Checking timings for doctor 001 ===")
timings = DoctorTiming.objects.filter(code='001').exclude(time1__isnull=True).exclude(time2__isnull=True)
print(f"Found {timings.count()} timings")
if timings.exists():
    t = timings.first()
    print(f"First timing: sun={t.sun}, mon={t.mon}, tue={t.tue}, wed={t.wed}, thu={t.thu}, fri={t.fri}, sat={t.sat}")
    print(f"  Times: {t.time1} to {t.time2}")
