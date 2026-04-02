"""
WhatsApp Integration - Diagnostic Tool
Troubleshoot WhatsApp messaging issues
"""

import os
import sys
import django
import requests
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from whatsapp.services import WhatsAppService, WHATSAPP_API_URL, WHATSAPP_ACCOUNT, WHATSAPP_SECRET
from appointments.models import Appointment

print("\n" + "="*70)
print("WhatsApp Integration - Diagnostic Tool")
print("="*70)

def check_credentials():
    """Check if API credentials are configured"""
    print("\n[1] Checking API Credentials...")
    print(f"    API URL: {WHATSAPP_API_URL}")
    print(f"    Account: {WHATSAPP_ACCOUNT[:20]}..." if len(WHATSAPP_ACCOUNT) > 20 else f"    Account: {WHATSAPP_ACCOUNT}")
    print(f"    Secret: {WHATSAPP_SECRET[:20]}..." if len(WHATSAPP_SECRET) > 20 else f"    Secret: {WHATSAPP_SECRET}")
    
    if not WHATSAPP_API_URL or not WHATSAPP_ACCOUNT or not WHATSAPP_SECRET:
        print("    ❌ PROBLEM: Missing API credentials!")
        return False
    print("    ✅ Credentials are configured")
    return True

def check_api_connectivity():
    """Check if DXing API is reachable"""
    print("\n[2] Checking API Connectivity...")
    try:
        response = requests.head(WHATSAPP_API_URL, timeout=5)
        print(f"    API URL is reachable (Status: {response.status_code})")
        print("    ✅ API is accessible")
        return True
    except requests.exceptions.ConnectionError:
        print("    ❌ PROBLEM: Cannot connect to API endpoint")
        print(f"    Check if {WHATSAPP_API_URL} is accessible")
        return False
    except requests.exceptions.Timeout:
        print("    ⚠️  API endpoint is slow to respond")
        return True
    except Exception as e:
        print(f"    ⚠️  Warning: {str(e)}")
        return True

def check_phone_format(phone_number):
    """Validate phone number format"""
    print(f"\n[3] Checking Phone Number Format: {phone_number}")
    
    # Check for common formatting issues
    issues = []
    
    if not phone_number:
        print("    ❌ PROBLEM: Phone number is empty!")
        return False
    
    if phone_number.startswith('+'):
        issues.append("Contains '+' symbol (should be removed)")
    
    if ' ' in phone_number:
        issues.append("Contains spaces (should be removed)")
    
    if '-' in phone_number:
        issues.append("Contains dashes (should be removed)")
    
    if not phone_number.isdigit():
        issues.append("Contains non-digit characters")
    
    if len(phone_number) < 10:
        issues.append("Too short (should be 10+ digits with country code)")
    
    if len(phone_number) > 15:
        issues.append("Too long (usually max 15 digits)")
    
    if issues:
        print("    ❌ PROBLEMS FOUND:")
        for issue in issues:
            print(f"        - {issue}")
        print(f"\n    Suggested format: Remove +, spaces, dashes")
        print(f"    Example for India: 918765432109 (country code 91 + number)")
        return False
    
    print(f"    ✅ Phone number format looks correct")
    return True

def test_api_directly(phone_number):
    """Test API directly with a test message"""
    print(f"\n[4] Testing API with Direct Call...")
    
    test_message = "This is a test message from Dr Health Hub WhatsApp integration at " + datetime.now().strftime('%H:%M:%S')
    
    payload = {
        "secret": WHATSAPP_SECRET,
        "account": WHATSAPP_ACCOUNT,
        "recipient": phone_number,
        "type": "text",
        "message": test_message
    }
    
    print(f"    Sending test message to: {phone_number}")
    print(f"    Message: '{test_message[:50]}...'")
    
    try:
        response = requests.post(WHATSAPP_API_URL, json=payload, timeout=15)
        print(f"    HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            print("    ✅ API returned success (200)")
            try:
                resp_json = response.json()
                print(f"    Response: {resp_json}")
                return True
            except:
                print(f"    Response Text: {response.text}")
                return True
        elif response.status_code == 401:
            print("    ❌ PROBLEM: Unauthorized (401)")
            print("    Check WHATSAPP_SECRET and WHATSAPP_ACCOUNT")
            print(f"    Response: {response.text}")
            return False
        else:
            print(f"    ⚠️  Unexpected status code: {response.status_code}")
            print(f"    Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("    ❌ PROBLEM: Request timeout (API too slow)")
        print("    Try increasing timeout or check API status")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"    ❌ PROBLEM: Connection error")
        print(f"    Error: {str(e)}")
        return False
    except Exception as e:
        print(f"    ❌ PROBLEM: {str(e)}")
        return False

def check_recent_appointments():
    """Check recent appointments in database"""
    print(f"\n[5] Checking Recent Appointments...")
    
    recent = Appointment.objects.all().order_by('-created_at')[:5]
    
    if not recent.exists():
        print("    No appointments found in database")
        return
    
    print(f"    Found {recent.count()} recent appointments:")
    for apt in recent:
        print(f"\n    ID: {apt.id}")
        print(f"    Patient: {apt.patient_name}")
        print(f"    Phone: {apt.phone_number}")
        print(f"    Status: {apt.status}")
        print(f"    Created: {apt.created_at}")
        
        if not apt.phone_number:
            print("    ⚠️  WARNING: No phone number!")

def check_logs():
    """Check for WhatsApp-related logs"""
    print(f"\n[6] Checking Django Logs for Errors...")
    
    # Check if logs file exists
    log_files = [
        'debug.log',
        'django.log',
        'whatsapp.log',
    ]
    
    print("    Looking for log files...")
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"    Found: {log_file}")
            with open(log_file, 'r') as f:
                lines = f.readlines()
                whatsapp_lines = [l for l in lines if 'whatsapp' in l.lower() or 'error' in l.lower()]
                if whatsapp_lines:
                    print(f"    Recent WhatsApp-related lines:")
                    for line in whatsapp_lines[-5:]:
                        print(f"        {line.strip()}")
    
    print("    Tip: Enable Django logging to see debug messages")

def main():
    """Run all diagnostic checks"""
    
    print("\n⚠️  DIAGNOSTIC CHECKLIST:")
    print("="*70)
    
    # Check 1: Credentials
    if not check_credentials():
        print("\n❌ CANNOT PROCEED: Missing API credentials")
        return
    
    # Check 2: API Connectivity
    if not check_api_connectivity():
        print("\n❌ CANNOT PROCEED: API not accessible")
        print("Possible solutions:")
        print("  - Check internet connection")
        print("  - Verify API URL is correct")
        print("  - Check if DXing API is down")
        return
    
    # Get phone number from user
    print("\n" + "="*70)
    phone = input("\nEnter phone number to test (format: country_code + number, e.g., 918765432109): ").strip()
    
    if not phone:
        print("No phone number provided")
        return
    
    # Check 3: Phone format
    if not check_phone_format(phone):
        print("\n❌ Phone number format issue detected")
        corrected = phone.replace('+', '').replace(' ', '').replace('-', '')
        test = input(f"\nTry corrected format? {corrected} (y/n): ")
        if test.lower() == 'y':
            phone = corrected
        else:
            return
    
    # Check 4: API Direct test
    if not test_api_directly(phone):
        print("\n❌ API test failed")
        print("\nPossible issues:")
        print("  1. Invalid API credentials")
        print("  2. Invalid phone number")
        print("  3. API account insufficient balance")
        print("  4. Phone number not WhatsApp-enabled")
        print("  5. API service down")
        return
    
    # Check 5: Recent appointments
    check_recent_appointments()
    
    # Check 6: Logs
    check_logs()
    
    print("\n" + "="*70)
    print("✅ ALL CHECKS PASSED!")
    print("="*70)
    print("\nIf you still don't receive messages:")
    print("  1. Wait 30 seconds (messages can be delayed)")
    print("  2. Check WhatsApp is saved as contact")
    print("  3. Check phone is WhatsApp-enabled")
    print("  4. Try with a different phone number")
    print("  5. Contact DXing support")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
