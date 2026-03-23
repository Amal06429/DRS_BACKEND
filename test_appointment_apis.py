#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify appointment API endpoints are working correctly
"""
import requests
import json
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000/api"

def test_admin_appointments():
    """Test admin appointments endpoint"""
    print("\n" + "="*60)
    print("Testing Admin Appointments Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/admin/appointments")
        if response.status_code == 200:
            data = response.json()
            appointments = data.get('appointments', [])
            print(f"✅ SUCCESS: Retrieved {len(appointments)} appointments")
            
            if appointments:
                print("\nFirst appointment details:")
                apt = appointments[0]
                print(f"  ID: {apt['id']}")
                print(f"  Patient: {apt['patient_name']}")
                print(f"  Doctor: {apt['doctor_name']} ({apt['doctor_code']})")
                print(f"  Department: {apt['department_name']} ({apt['department_code']})")
                print(f"  Date: {apt['appointment_date']}")
                print(f"  Time Range: {apt['appointment_time_range']}")
                print(f"  Status: {apt['status']}")
                
                # Count by status
                pending = sum(1 for a in appointments if a['status'] == 'pending')
                accepted = sum(1 for a in appointments if a['status'] == 'accepted')
                rejected = sum(1 for a in appointments if a['status'] == 'rejected')
                
                print(f"\nStatus breakdown:")
                print(f"  Pending: {pending}")
                print(f"  Accepted: {accepted}")
                print(f"  Rejected: {rejected}")
        else:
            print(f"❌ FAILED: Status code {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def test_doctor_appointments():
    """Test doctor appointments endpoint"""
    print("\n" + "="*60)
    print("Testing Doctor Appointments Endpoint")
    print("="*60)
    
    doctor_codes = ["004", "005", "001"]
    
    for doctor_code in doctor_codes:
        try:
            response = requests.get(f"{BASE_URL}/doctor/appointments/{doctor_code}")
            if response.status_code == 200:
                appointments = response.json()
                print(f"\n✅ Doctor {doctor_code}: {len(appointments)} accepted appointments")
                
                if appointments:
                    for apt in appointments[:3]:  # Show first 3
                        print(f"  - {apt['patient_name']} on {apt['appointment_time_range']}")
            else:
                print(f"❌ Doctor {doctor_code}: Status code {response.status_code}")
        except Exception as e:
            print(f"❌ Doctor {doctor_code}: ERROR - {str(e)}")

def test_update_status():
    """Test updating appointment status"""
    print("\n" + "="*60)
    print("Testing Update Appointment Status Endpoint")
    print("="*60)
    
    # First get an appointment
    try:
        response = requests.get(f"{BASE_URL}/admin/appointments")
        if response.status_code == 200:
            appointments = response.json()['appointments']
            if appointments:
                apt_id = appointments[0]['id']
                current_status = appointments[0]['status']
                
                # Try to update to a different status
                new_status = 'accepted' if current_status != 'accepted' else 'pending'
                
                print(f"\nAttempting to update appointment {apt_id}")
                print(f"  Current status: {current_status}")
                print(f"  New status: {new_status}")
                
                update_response = requests.patch(
                    f"{BASE_URL}/admin/appointments/{apt_id}/status",
                    json={'status': new_status},
                    headers={'Content-Type': 'application/json'}
                )
                
                if update_response.status_code == 200:
                    result = update_response.json()
                    print(f"✅ SUCCESS: {result['message']}")
                    print(f"  Updated status: {result['appointment']['status']}")
                    
                    # Revert back
                    revert_response = requests.patch(
                        f"{BASE_URL}/admin/appointments/{apt_id}/status",
                        json={'status': current_status},
                        headers={'Content-Type': 'application/json'}
                    )
                    if revert_response.status_code == 200:
                        print(f"✅ Reverted back to: {current_status}")
                else:
                    print(f"❌ FAILED: Status code {update_response.status_code}")
                    print(f"Response: {update_response.text}")
            else:
                print("⚠️  No appointments found to test update")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def main():
    print("\n" + "="*60)
    print("APPOINTMENT API ENDPOINT TESTS")
    print("="*60)
    print("\nMake sure the Django server is running on http://localhost:8000")
    
    test_admin_appointments()
    test_doctor_appointments()
    test_update_status()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
