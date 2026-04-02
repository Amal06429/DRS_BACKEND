"""
Phone Number Cleaning Verification
Test the phone number cleaning functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from whatsapp.services import clean_phone_number

print("\n" + "="*70)
print("Phone Number Cleaning Verification")
print("="*70)

test_cases = [
    # (input, expected_output, description)
    ("+919876543210", "919876543210", "Phone with + prefix"),
    ("+91 98765 43210", "919876543210", "Phone with + prefix and spaces"),
    ("+91-98765-43210", "919876543210", "Phone with + prefix and dashes"),
    ("919876543210", "919876543210", "Clean phone number"),
    ("91 9876 543210", "919876543210", "Phone with spaces"),
    ("91-98765-43210", "919876543210", "Phone with dashes"),
    ("+1-310-555-1234", "13105551234", "US phone with + and dashes"),
    ("+44 1632 960000", "441632960000", "UK phone with + and spaces"),
    ("", None, "Empty phone number"),
    (None, None, "None phone number"),
]

print("\nTesting phone number cleaning:\n")

passed = 0
failed = 0

for input_phone, expected, description in test_cases:
    result = clean_phone_number(input_phone)
    
    if result == expected:
        status = "✅ PASS"
        passed += 1
    else:
        status = "❌ FAIL"
        failed += 1
    
    print(f"{status}: {description}")
    print(f"   Input:    {repr(input_phone)}")
    print(f"   Expected: {repr(expected)}")
    print(f"   Got:      {repr(result)}")
    print()

print("="*70)
print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("="*70)

if failed == 0:
    print("✅ All phone number cleaning tests PASSED!")
    print("\nThe WhatsApp integration will now automatically:")
    print("  - Remove '+' prefix")
    print("  - Remove spaces and dashes")
    print("  - Clean phone numbers before sending")
    print("\nYou can now submit bookings with phone numbers like:")
    print("  - +919876543210")
    print("  - +91 98765 43210")
    print("  - +91-98765-43210")
    print("  - 919876543210")
    print("\nAll formats will work correctly! 🎉")
else:
    print(f"\n❌ {failed} tests FAILED - please review the implementation")

print("\n")
