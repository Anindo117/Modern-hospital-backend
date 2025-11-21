# Database Migration Guide

## Overview
This guide explains how to migrate your database to include all the new tables and columns for the ambulance services and eye products features.

## Prerequisites
- Backend virtual environment activated
- PostgreSQL database running and accessible
- All environment variables configured in `.env`

## Migration Steps

### Step 1: Activate Virtual Environment
```bash
cd backend
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

### Step 2: Run Migration
To create/update all tables:
```bash
python scripts/migrate_db.py
```

This will:
- Create all new tables (AmbulanceService, EyeProduct, etc.)
- Update existing tables with new columns
- Preserve existing data

### Step 3: Verify Migration
Check that all tables were created:
```bash
# Connect to your PostgreSQL database
psql -U your_user -d your_database

# List all tables
\dt

# Check users table structure
\d users

# Check new tables
\d ambulance_services
\d eye_products
```

## Reset Database (Optional)
If you need to completely reset the database and start fresh:
```bash
python scripts/migrate_db.py reset
```

**WARNING**: This will delete all existing data!

## Troubleshooting

### Issue: "column users.nid does not exist"
**Solution**: Run the migration script to create all columns:
```bash
python scripts/migrate_db.py
```

### Issue: "relation does not exist"
**Solution**: Ensure all tables are created by running migration again:
```bash
python scripts/migrate_db.py
```

### Issue: Connection refused
**Solution**: Verify PostgreSQL is running and DATABASE_URL is correct in `.env`

## New Tables Created

### 1. ambulance_services
- id (Primary Key)
- name (Unique)
- description
- phone
- location
- latitude
- longitude
- available_24_7
- ambulance_count
- is_active
- created_at
- updated_at

### 2. eye_products
- id (Primary Key)
- name
- description
- category
- brand
- price
- image_url
- stock_quantity
- is_available
- is_active
- created_at
- updated_at

## Updated Tables

### users
New optional columns added:
- nid (National ID)
- date_of_birth
- gender
- blood_group
- division
- district
- upazila
- village
- address
- emergency_contact_name
- emergency_contact_phone

All these fields are optional and won't break existing registrations.

## Patient Registration
Patients can now register with just:
- **phone** (required)
- **password** (required)
- **full_name** (optional)
- **email** (optional)

All Bangladeshi profile fields are optional and can be filled later.

## Next Steps
1. Run the migration
2. Restart the backend server
3. Test patient registration with minimal fields
4. Test ambulance services and eye products endpoints
