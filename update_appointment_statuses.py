#!/usr/bin/env python
"""Script to update old appointment statuses to new status schema"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from appointments.models import Appointment

def update_statuses():
    """Update old statuses to new schema"""
    
    print("=" * 70)
    print("UPDATING APPOINTMENT STATUSES")
    print("=" * 70)
    print()
    
    # Mapping old statuses to new ones
    status_mapping = {
        'confirmed': 'accepted',
        'completed': 'accepted',
        'cancelled': 'rejected',
    }
    
    total_updated = 0
    
    for old_status, new_status in status_mapping.items():
        appointments = Appointment.objects.filter(status=old_status)
        count = appointments.count()
        
        if count > 0:
            print(f"Updating {count} appointment(s) from '{old_status}' to '{new_status}'...")
            appointments.update(status=new_status)
            total_updated += count
    
    # Display summary
    print()
    print("=" * 70)
    print("CURRENT STATUS DISTRIBUTION")
    print("=" * 70)
    
    all_appointments = Appointment.objects.all()
    total = all_appointments.count()
    
    pending_count = all_appointments.filter(status='pending').count()
    accepted_count = all_appointments.filter(status='accepted').count()
    rejected_count = all_appointments.filter(status='rejected').count()
    
    print(f"Total appointments: {total}")
    print(f"  • Pending: {pending_count}")
    print(f"  • Accepted: {accepted_count}")
    print(f"  • Rejected: {rejected_count}")
    print()
    
    if total_updated > 0:
        print(f"✓ Successfully updated {total_updated} appointment(s)")
    else:
        print("✓ No updates needed - all statuses are already using the new schema")
    
    print("=" * 70)

if __name__ == '__main__':
    update_statuses()
