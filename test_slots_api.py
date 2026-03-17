import requests
from datetime import date, timedelta

API_URL = "http://localhost:8000/api/slots/"

# Test with doctor 001
doctor_code = "001"
test_date = date.today().strftime('%Y-%m-%d')

print(f"\n{'='*60}")
print(f"TESTING SLOTS API")
print(f"{'='*60}")
print(f"Doctor Code: {doctor_code}")
print(f"Date: {test_date}")
print(f"URL: {API_URL}?doctor_code={doctor_code}&date={test_date}")
print(f"{'='*60}\n")

try:
    response = requests.get(API_URL, params={
        'doctor_code': doctor_code,
        'date': test_date
    })
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        slots = response.json()
        print(f"\nTotal Slots: {len(slots)}")
        
        if slots:
            print(f"\nFirst 10 slots:")
            for slot in slots[:10]:
                print(f"  Slot {slot['slot_number']}: {slot['start_time']} - {slot['end_time']} [{slot['status']}]")
            
            # Count by status
            vacant = sum(1 for s in slots if s['status'] == 'Vacant')
            booked = sum(1 for s in slots if s['status'] == 'Booked')
            print(f"\nSummary:")
            print(f"  Vacant: {vacant}")
            print(f"  Booked: {booked}")
        else:
            print("\nNo slots returned!")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure Django server is running:")
    print("  cd DRS_BACKEND")
    print("  python manage.py runserver")
