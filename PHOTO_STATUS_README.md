# Doctor Photo Display - Current Setup and Requirements

## 🎯 Current Status

### ✅ What's Ready in DRS:
1. **Database Field**: `hms_doctors.photourl` column exists
2. **API**: Returns `photo_url` in all doctor endpoints
3. **Frontend**: Displays photos on all pages (with fallback to initials)
4. **Migration**: Completed - all tables updated

### ❌ What's Missing:
**HMS (Hospital Management System) needs to provide actual doctor photo URLs**

Currently, all `photourl` values are `NULL` in the database because:
- The HMS sync is not sending photo URLs
- OR the HMS database doesn't have doctor photos yet

---

## 📸 How It Works

### Current Data Flow:
```
HMS Database (External)
    ↓
    photourl: NULL (No photos provided yet)
    ↓
DRS Database (hms_doctors table)
    ↓
    photourl: NULL
    ↓
API Response
    ↓
    "photo_url": null
    ↓
Frontend Display
    ↓
    Shows doctor's initial in colored circle (S, A, M, etc.)
```

### Expected Data Flow (Once HMS Provides Photos):
```
HMS Database
    ↓
    photourl: "https://hms-server.com/photos/029.jpg"
    ↓
DRS Database
    ↓
    photourl: "https://hms-server.com/photos/029.jpg"
    ↓
API Response
    ↓
    "photo_url": "https://hms-server.com/photos/029.jpg"
    ↓
Frontend Display
    ↓
    Shows actual doctor photo <img src="..." />
```

---

## 🔧 What HMS Team Needs to Do

### Option 1: Provide Photo URLs (Easiest)
Update HMS sync script to include photo URLs:

```sql
-- When syncing doctors to DRS
INSERT INTO hms_doctors (
    code, name, rate, department, qualification, 
    photourl,  -- ADD THIS FIELD
    synced_at
) VALUES (
    '029', 'STEPHEENA K CYRIAC', 150.0, 'RMO', 'M.B.B.S',
    'https://your-hms-server.com/photos/doctors/029.jpg',  -- PHOTO URL
    '2026-03-12 10:00:00'
);
```

**Where can photos be hosted:**
- HMS server: `https://hms.hospital.com/photos/029.jpg`
- Cloud storage: `https://s3.amazonaws.com/hospital/doctors/029.jpg`
- CDN: `https://cdn.hospital.com/doctors/029.jpg`
- Local server: `http://192.168.1.100/hms/photos/029.jpg`

### Option 2: Copy Photo Files to DRS Server
Copy actual photo files during HMS sync:

```python
# In HMS sync script
import shutil

# Copy doctor photo
hms_photo = f"/hms/photos/{doctor_code}.jpg"
drs_photo = f"/var/www/drs/media/hms_photos/{doctor_code}.jpg"

if os.path.exists(hms_photo):
    shutil.copy2(hms_photo, drs_photo)
    photourl = f"/media/hms_photos/{doctor_code}.jpg"
else:
    photourl = None
```

---

## 📋 Checklist for HMS Team

- [ ] **Step 1**: Locate where doctor photos are stored in HMS
  - File path? (e.g., `/var/www/hms/photos/`)
  - Database field? (e.g., `hms_doctors.photo_path`)
  - Cloud storage? (e.g., S3 bucket)

- [ ] **Step 2**: Make photos accessible via URL
  - Set up web server to serve photos
  - OR upload to cloud storage
  - OR copy files to DRS server

- [ ] **Step 3**: Update HMS sync script
  - Add `photourl` field to sync
  - Include full URL or path to photos
  - Test with 2-3 doctors first

- [ ] **Step 4**: Verify in DRS
  - Check database: `SELECT code, name, photourl FROM hms_doctors LIMIT 5;`
  - Check API: Visit `http://localhost:8000/api/doctors/RMO`
  - Check frontend: Open DRS and select department

---

## 🧪 Testing

### Test with Sample Photo URL:
```bash
cd DRS_BACKEND
python manage.py shell
```

```python
from django.db import connection

# Add test photo URL
cursor = connection.cursor()
cursor.execute("""
    UPDATE hms_doctors 
    SET photourl = 'https://your-hms-server.com/photos/doctors/029.jpg'
    WHERE code = '029'
""")

# Verify
cursor.execute("SELECT code, name, photourl FROM hms_doctors WHERE code = '029'")
print(cursor.fetchone())
```

### Check API Response:
```bash
curl http://localhost:8000/api/doctors/RMO | json_pp
```

Should show:
```json
{
  "doctors": [
    {
      "code": "029",
      "name": "STEPHEENA K CYRIAC",
      "photo_url": "https://your-hms-server.com/photos/doctors/029.jpg",
      ...
    }
  ]
}
```

### Check Frontend:
1. Open `http://localhost:5173`
2. Select RMO department
3. Should see doctor photo (if URL accessible) or initial (if URL not accessible)

---

## 📁 Files Created for Reference

1. **[HMS_PHOTO_SYNC_GUIDE.md](HMS_PHOTO_SYNC_GUIDE.md)** - Complete guide with code examples
2. **[test_hms_photo_url.py](test_hms_photo_url.py)** - Test script to verify photo URLs work

---

## 🆘 Common Issues

### Q: Photos show initials instead of actual photos
**A:** HMS is not providing photo URLs. Check:
- Database: `SELECT photourl FROM hms_doctors WHERE photourl IS NOT NULL;`
- If count is 0, HMS sync needs to be updated

### Q: Photos show broken image icon
**A:** Photo URLs are provided but not accessible. Check:
- URL is correct: `curl -I "https://hms-server.com/photos/029.jpg"`
- Should return `200 OK`, not `404 Not Found`
- CORS headers if photos on different domain

### Q: Some photos work, others don't
**A:** Mixed data quality. Check:
- Which doctors have valid photourl: `SELECT code, photourl FROM hms_doctors WHERE photourl IS NOT NULL;`
- Test each URL individually

---

## 📞 Next Steps

1. **Contact HMS Team**: Ask where doctor photos are stored
2. **Get Photo Access**: Get URL pattern or file path
3. **Update Sync Script**: Include photourl in sync
4. **Test**: Sync 2-3 doctors and verify display
5. **Full Sync**: Sync all doctors with photos

---

## Summary

**DRS is ready to display doctor photos!** 

The system is fully configured. We just need the HMS (Hospital Management System) to provide the actual photo URLs during the sync process. Once HMS includes photo URLs, they will automatically display throughout the DRS system.

**Current Display**: Doctor initials in colored circles (placeholder)
**Expected Display**: Actual doctor photos (once HMS provides URLs)
