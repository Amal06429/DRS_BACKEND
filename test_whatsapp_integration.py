"""
WhatsApp Integration Test Script
Tests all WhatsApp messaging functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from whatsapp.services import WhatsAppService
from datetime import datetime, timedelta
import json

print("=" * 60)
print("WhatsApp Integration Test Suite")
print("=" * 60)

# Test phone number (CHANGE THIS TO YOUR TEST NUMBER)
TEST_PHONE = "918765432109"

def print_result(test_name, result):
    """Pretty print test results"""
    print(f"\n{'─' * 60}")
    print(f"Test: {test_name}")
    print(f"{'─' * 60}")
    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    if result.get('response'):
        print(f"API Response: {json.dumps(result.get('response'), indent=2)}")
    print()

def test_booking_confirmation():
    """Test 1: Booking Confirmation Message"""
    print("\n[1/4] Testing Booking Confirmation Message...")
    
    result = WhatsAppService.send_booking_confirmation(
        phone_number=TEST_PHONE,
        patient_name="John Doe",
        appointment_date=datetime.now() + timedelta(days=7),
        doctor_code="DOC001",
        slot_number=1
    )
    print_result("Booking Confirmation", result)
    return result.get('success', False)

def test_booking_approved():
    """Test 2: Booking Approved Message"""
    print("\n[2/4] Testing Booking Approved Message...")
    
    result = WhatsAppService.send_booking_approved(
        phone_number=TEST_PHONE,
        patient_name="John Doe",
        appointment_date=datetime.now() + timedelta(days=7),
        doctor_code="DOC001"
    )
    print_result("Booking Approved", result)
    return result.get('success', False)

def test_booking_rejected():
    """Test 3: Booking Rejected Message"""
    print("\n[3/4] Testing Booking Rejected Message...")
    
    result = WhatsAppService.send_booking_rejected(
        phone_number=TEST_PHONE,
        patient_name="John Doe",
        appointment_date=datetime.now() + timedelta(days=7),
        doctor_code="DOC001"
    )
    print_result("Booking Rejected", result)
    return result.get('success', False)

def test_custom_message():
    """Test 4: Custom Message"""
    print("\n[4/4] Testing Custom Message...")
    
    result = WhatsAppService.send_custom_message(
        phone_number=TEST_PHONE,
        message="Hello! This is a test message from Dr Health Hub. If you received this, the WhatsApp integration is working correctly!"
    )
    print_result("Custom Message", result)
    return result.get('success', False)

def main():
    """Run all tests"""
    print(f"\nTest Configuration:")
    print(f"  Phone Number: {TEST_PHONE}")
    print(f"  Timestamp: {datetime.now()}")
    print(f"\n⚠️  IMPORTANT: Make sure to update TEST_PHONE with your actual number!")
    print(f"   Current phone is for demonstration only.\n")
    
    # Run tests
    results = []
    try:
        results.append(("Booking Confirmation", test_booking_confirmation()))
        results.append(("Booking Approved", test_booking_approved()))
        results.append(("Booking Rejected", test_booking_rejected()))
        results.append(("Custom Message", test_custom_message()))
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    print("\n⚠️  Before running this test:")
    print("   1. Update TEST_PHONE variable with your actual phone number")
    print("   2. Ensure WhatsApp API credentials are correct in whatsapp/services.py")
    print("   3. Make sure your phone number is WhatsApp enabled\n")
    
    input("Press Enter to continue with testing...")
    sys.exit(main())
