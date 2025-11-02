from supabase import create_client
import os
from config.settings import settings

supabase = create_client(settings.supabase_url, settings.supabase_key)

# Get all creators
creators = supabase.table("creators").select("*").execute()
print("=== CREATORS ===")
for c in creators.data:
    print(f"ID: {c['tg_user_id']}, Username: {c['username']}, Videos: {c['total_videos']}")

print("\n=== VIDEOS ===")
# Get all videos
videos = supabase.table("videos").select("id, tg_user_id, prompt, status, video_url, creators(username)").order("created_at", desc=True).execute()
for v in videos.data:
    username = v.get('creators', {}).get('username') if v.get('creators') else 'None'
    url_preview = v['video_url'][:70] + "..." if v['video_url'] and len(v['video_url']) > 70 else v['video_url']
    print(f"ID: {v['id']}, User: {username}, Status: {v['status']}, URL: {url_preview}")
