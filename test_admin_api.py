import requests
import json

print("Testing Admin Appointments API...")
try:
    response = requests.get('http://localhost:8000/api/admin/appointments')
    data = response.json()
    
    print(f'Status: {response.status_code}')
    print('='*60)
    
    if 'appointments' in data:
        appointments = data['appointments']
        print(f'Total appointments: {len(appointments)}')
        if appointments:
            print('\nFirst appointment:')
            print(json.dumps(appointments[0], indent=2))
    else:
        print(json.dumps(data, indent=2)[:500])
        
except Exception as e:
    print(f'Error: {e}')
