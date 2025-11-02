# 🗂️ Supabase Storage Setup Guide

## Problem
The `videos` bucket does not exist in your Supabase project, causing video uploads to fail.

## Solution: Create the bucket manually

### Step 1: Go to Supabase Dashboard
1. Visit: https://app.supabase.com
2. Select your project: `oqdwjrhcdlflfebujnkq`

### Step 2: Create Storage Bucket
1. Click on **Storage** in the left sidebar
2. Click **New bucket**
3. Configure:
   - **Name:** `videos`
   - **Public bucket:** ✅ YES (check this box)
   - **File size limit:** 100 MB (or higher)
   - **Allowed MIME types:** `video/*` (or leave empty for all)

4. Click **Create bucket**

### Step 3: Verify
Run this command to verify the bucket was created:

```bash
source venv/bin/activate
python3 -c "
from supabase import create_client
from config.settings import settings
supabase = create_client(settings.supabase_url, settings.supabase_key)
buckets = supabase.storage.list_buckets()
print('Buckets:', [b.name for b in buckets])
"
```

You should see: `Buckets: ['videos']`

### Step 4: Set Bucket Policies (Important!)

Make sure the bucket has these policies enabled:

#### Policy 1: Public Read Access
- **Name:** `Public video access`
- **Policy:** SELECT
- **Target roles:** `anon`, `authenticated`
- **SQL:**
```sql
((bucket_id = 'videos'::text))
```

#### Policy 2: Authenticated Upload
- **Name:** `Authenticated users can upload`
- **Policy:** INSERT
- **Target roles:** `authenticated`, `service_role`
- **SQL:**
```sql
((bucket_id = 'videos'::text))
```

#### Policy 3: Service Role Full Access
- **Name:** `Service role full access`
- **Policy:** ALL
- **Target roles:** `service_role`
- **SQL:**
```sql
((bucket_id = 'videos'::text))
```

### Alternative: Use SQL

If you have access to the SQL editor, run:

```sql
-- Create the bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('videos', 'videos', true);

-- Set policies
CREATE POLICY "Public read access"
ON storage.objects FOR SELECT
USING (bucket_id = 'videos');

CREATE POLICY "Authenticated upload"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'videos' AND auth.role() = 'authenticated');

CREATE POLICY "Service role full access"
ON storage.objects FOR ALL
USING (bucket_id = 'videos' AND auth.role() = 'service_role');
```

## After Setup

Once the bucket is created, the video upload system will work automatically.
Re-run the video processing script to upload the 9 pending videos.
