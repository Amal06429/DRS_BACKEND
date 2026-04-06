# HMS Doctor Photo Sync Guide

## Overview
The Doctor Registration System (DRS) displays doctor photos from the HMS (Hospital Management System) database. This guide explains how to sync actual doctor photos from HMS.

## Current Status
✅ Database schema ready - `hms_doctors.photourl` field exists
✅ Backend API configured - Returns `photo_url` in API responses
✅ Frontend configured - Displays photos on all pages
❌ **HMS sync needs to provide actual photo URLs**

---

## How HMS Should Provide Doctor Photos

### Option 1: Photo URLs (Recommended)
The HMS system should store photo URLs in the `photourl` field during sync.

**Example HMS Sync Data:**
```json
{
  "code": "029",
  "name": "STEPHEENA K CYRIAC",
  "rate": 150.0,
  "department": "RMO",
  "qualification": "M.B.B.S",
  "photourl": "https://your-hospital-server.com/photos/doctors/029.jpg",
  "synced_at": "2026-03-12 10:30:00"
}
```

**Photo URL Formats Supported:**
- ✅ Direct URLs: `https://example.com/photos/029.jpg`
- ✅ Hospital server: `https://hospital-server.com/api/photos/029`
- ✅ Cloud storage: `https://s3.amazonaws.com/hospital/doctors/029.jpg`
- ✅ Base64 data URLs: `data:image/jpeg;base64,/9j/4AAQ...`

---

### Option 2: Photo File Server
Host doctor photos on your HMS server and provide the URL pattern.

**Setup:**
1. Store photos on HMS server: `/var/www/hms/photos/doctors/`
2. Name files by doctor code: `029.jpg`, `030.jpg`, etc.
3. Configure web server to serve photos
4. Provide URL pattern: `https://hms-server.com/photos/doctors/{code}.jpg`

**In HMS Sync:**
```python
# When syncing doctor data
doctor_photo_url = f"https://hms-server.com/photos/doctors/{doctor_code}.jpg"
```

---

### Option 3: Copy Photos to DRS Server
Copy physical photo files to DRS server during sync.

**Setup:**
1. Create media directory: `DRS_BACKEND/media/hms_photos/`
2. During sync, copy photos: `029.jpg`, `030.jpg`
3. Update photourl: `/media/hms_photos/{code}.jpg`

**Example:**
```python
import shutil
import os

# Copy photo during HMS sync
hms_photo_path = f"/path/to/hms/photos/{doctor_code}.jpg"
drs_photo_path = f"/path/to/drs/media/hms_photos/{doctor_code}.jpg"

if os.path.exists(hms_photo_path):
    shutil.copy2(hms_photo_path, drs_photo_path)
    photourl = f"/media/hms_photos/{doctor_code}.jpg"
else:
    photourl = None
```

---

## HMS Sync Script Example

### Complete Example with Photos:
```python
import psycopg2
import requests
from datetime import datetime

def sync_doctors_with_photos():
    """Sync doctors from HMS to DRS including photos"""
    
    # Connect to HMS database
    hms_conn = psycopg2.connect(
        host="hms-server",
        database="hms_db",
        user="hms_user",
        password="hms_pass"
    )
    
    # Connect to DRS database
    drs_conn = psycopg2.connect(
        host="localhost",
        database="drs_db",
        user="drs_user",
        password="drs_pass"
    )
    
    hms_cursor = hms_conn.cursor()
    drs_cursor = drs_conn.cursor()
    
    # Get doctors from HMS
    hms_cursor.execute("""
        SELECT 
            doctor_code,
            doctor_name,
            consultation_rate,
            department_code,
            avg_consultation_time,
            qualification,
            photo_path  -- Photo path or URL in HMS
        FROM hms_doctors
        WHERE active = true
    """)
    
    sync_time = datetime.now().isoformat()
    
    for row in hms_cursor.fetchall():
        code, name, rate, dept, avgtime, qual, photo_path = row
        
        # Generate photo URL
        if photo_path:
            # Option 1: Direct URL
            if photo_path.startswith('http'):
                photo_url = photo_path
            # Option 2: Construct URL from path
            else:
                photo_url = f"https://hms-server.com/photos/{photo_path}"
        else:
            photo_url = None
        
        # Insert/Update in DRS
        drs_cursor.execute("""
            INSERT INTO hms_doctors 
                (code, name, rate, department, avgcontime, qualification, photourl, synced_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (code) DO UPDATE SET
                name = EXCLUDED.name,
                rate = EXCLUDED.rate,
                department = EXCLUDED.department,
                avgcontime = EXCLUDED.avgcontime,
                qualification = EXCLUDED.qualification,
                photourl = EXCLUDED.photourl,
                synced_at = EXCLUDED.synced_at
        """, (code, name, rate, dept, avgtime, qual, photo_url, sync_time))
    
    drs_conn.commit()
    print(f"✓ Synced {hms_cursor.rowcount} doctors with photos")
    
    hms_conn.close()
    drs_conn.close()

if __name__ == "__main__":
    sync_doctors_with_photos()
```

---

## Verification Steps

### 1. Check Photo URLs in Database
```bash
cd DRS_BACKEND
python manage.py shell
```

```python
from hms_sync.models import Doctor

# Check doctors with photos
doctors_with_photos = Doctor.objects.filter(photourl__isnull=False)
print(f"Doctors with photos: {doctors_with_photos.count()}")

# Show sample
for doctor in doctors_with_photos[:5]:
    print(f"{doctor.code} - {doctor.name}: {doctor.photourl}")
```

### 2. Test API Response
```bash
curl http://bookingdrs.com/api/doctors/RMO
```

Should return:
```json
{
  "doctors": [
    {
      "code": "029",
      "name": "STEPHEENA K CYRIAC",
      "photo_url": "https://hms-server.com/photos/029.jpg",
      ...
    }
  ]
}
```

### 3. Check Frontend Display
1. Open `http://localhost:5173`
2. Select a department
3. Doctor photos should display (or show initials if photo_url is null)

---

## Troubleshooting

### Photos Not Displaying

**Check 1: Database has URLs**
```sql
SELECT code, name, photourl 
FROM hms_doctors 
WHERE photourl IS NOT NULL 
LIMIT 5;
```

**Check 2: URLs are accessible**
```bash
curl -I "https://hms-server.com/photos/029.jpg"
# Should return 200 OK
```

**Check 3: CORS Headers (if different domain)**
```python
# In settings.py
CORS_ALLOWED_ORIGINS = [
    "https://hms-server.com",
]
```

**Check 4: Frontend receives data**
Open browser DevTools → Network → Check API response

---

## Photo Requirements

**Recommended Specifications:**
- Format: JPEG or PNG
- Size: 200x200 pixels (square)
- Max file size: 500KB
- Aspect ratio: 1:1 (square)

**Accepted Formats:**
- ✅ `.jpg`, `.jpeg`
- ✅ `.png`
- ✅ `.webp`
- ❌ `.gif` (not recommended)
- ❌ `.bmp` (too large)

---

## Security Considerations

### Photo Access Control
If photos contain sensitive information:

1. **Use authenticated URLs:**
```python
photourl = f"https://hms-server.com/api/photos/{code}?token={secure_token}"
```

2. **Serve through DRS backend:**
```python
# In DRS views.py
@api_view(['GET'])
def get_doctor_photo(request, code):
    # Fetch from HMS with authentication
    response = requests.get(
        f"https://hms-server.com/photos/{code}.jpg",
        headers={"Authorization": f"Bearer {HMS_TOKEN}"}
    )
    return HttpResponse(response.content, content_type='image/jpeg')
```

---

## Summary Checklist

- [ ] HMS system has doctor photos available
- [ ] Photos accessible via URL or file path
- [ ] HMS sync script updated to include `photourl`
- [ ] Test sync with sample doctors
- [ ] Verify photos display in DRS frontend
- [ ] Configure CORS if needed
- [ ] Set up photo server/CDN if needed
- [ ] Document HMS photo update procedure

---

## Need Help?

**Contact DRS Development Team:**
- Check database: `python manage.py dbshell`
- View logs: `tail -f logs/django.log`
- Test API: `python manage.py shell`

**HMS Integration Questions:**
- HMS photo storage location?
- HMS photo access method?
- HMS sync schedule?
