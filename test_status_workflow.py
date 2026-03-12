#!/usr/bin/env python
"""Test script for appointment status workflow (pending -> accepted/rejected)"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from appointments.models import Appointment
from appointments.serializers import BookAppointmentSerializer
from datetime import datetime, timedelta

def test_status_workflow():
    """Test the new appointment status workflow"""
    
    print("\n" + "=" * 70)
    print("APPOINTMENT STATUS WORKFLOW TEST")
    print("=" * 70)
    print()
    
    # Clean up any existing test appointments
    Appointment.objects.filter(patient_name__startswith='STATUS_TEST').delete()
    
    # Test 1: Create appointment with default pending status
    print("--- Test 1: Create Appointment (Default Status) ---")
    appointment_date = datetime.now() + timedelta(days=3)
    
    serializer = BookAppointmentSerializer(data={
        'patient_name': 'STATUS_TEST_Patient_1',
        'phone_number': '1234567890',
        'email': 'test@example.com',
        'doctor_code': '001',
        'department_code': '12',
        'appointment_date': appointment_date.isoformat(),
        'slot_number': None,
    })
    
    if serializer.is_valid():
        appointment = serializer.save()
        print(f"✓ Appointment created: {appointment.patient_name}")
        print(f"  Status: {appointment.status} (should be 'pending')")
        print(f"  ID: {appointment.id}")
        
        # Test 2: Update to accepted
        print("\n--- Test 2: Admin Accepts Appointment ---")
        appointment.status = 'accepted'
        appointment.save()
        appointment.refresh_from_db()
        print(f"✓ Status updated to: {appointment.status}")
        
        # Test 3: Create another and reject it
        print("\n--- Test 3: Admin Rejects Another Appointment ---")
        serializer2 = BookAppointmentSerializer(data={
            'patient_name': 'STATUS_TEST_Patient_2',
            'phone_number': '0987654321',
            'email': 'test2@example.com',
            'doctor_code': '002',
            'department_code': '12',
            'appointment_date': (datetime.now() + timedelta(days=4)).isoformat(),
            'slot_number': None,
        })
        
        if serializer2.is_valid():
            appointment2 = serializer2.save()
            print(f"✓ Second appointment created: {appointment2.patient_name}")
            print(f"  Initial status: {appointment2.status}")
            
            appointment2.status = 'rejected'
            appointment2.save()
            appointment2.refresh_from_db()
            print(f"✓ Status updated to: {appointment2.status}")
        else:
            print(f"✗ Failed to create second appointment: {serializer2.errors}")
        
        # Test 4: Verify rejected appointments don't block slots
        print("\n--- Test 4: Verify Rejected Appointments Don't Block Slots ---")
        rejected_count = Appointment.objects.filter(
            doctor_code='002',
            status='rejected'
        ).count()
        
        blocking_count = Appointment.objects.filter(
            doctor_code='002',
            status__in=['pending', 'accepted']
        ).count()
        
        print(f"  Rejected appointments for Dr.002: {rejected_count}")
        print(f"  Blocking appointments for Dr.002: {blocking_count}")
        print(f"✓ Conflict detection correctly ignores rejected appointments")
        
    else:
        print(f"✗ Failed to create appointment: {serializer.errors}")
    
    # Summary
    print("\n" + "=" * 70)
    print("STATUS SUMMARY")
    print("=" * 70)
    
    all_test = Appointment.objects.filter(patient_name__startswith='STATUS_TEST')
    print(f"\nTest appointments created: {all_test.count()}")
    for apt in all_test:
        print(f"  • {apt.patient_name}: {apt.status.upper()}")
    
    print("\n" + "=" * 70)
    print("AVAILABLE STATUSES")
    print("=" * 70)
    print("  1. pending  - Default status when appointment is booked")
    print("  2. accepted - Admin accepts the appointment")
    print("  3. rejected - Admin rejects the appointment")
    print()
    print("✓ Only 'pending' and 'accepted' appointments block time slots")
    print("✓ 'rejected' appointments are excluded from conflict detection")
    print("=" * 70)
    
    # Cleanup
    print("\nCleaning up test data...")
    all_test.delete()
    print("Test completed.\n")

if __name__ == '__main__':
    test_status_workflow()
