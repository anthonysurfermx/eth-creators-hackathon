#!/usr/bin/env python3
"""
Clean up placeholder videos from database
These are videos with URLs like https://storage.uniswap.com/videos/*.mp4
that were never actually uploaded (fake URLs from placeholder mode)
"""

from supabase import create_client
from config.settings import settings
from loguru import logger

supabase = create_client(settings.supabase_url, settings.supabase_key)

print("=" * 80)
print("🧹 CLEANUP: Removing Placeholder Videos")
print("=" * 80)
print()

# Step 1: Find all placeholder videos
print("1️⃣  Finding placeholder videos...\n")

videos = supabase.table("videos").select("*").execute()

placeholder_videos = []
for video in videos.data:
    video_url = video.get('video_url', '')

    # Placeholder URLs start with https://storage.uniswap.com/
    if video_url.startswith('https://storage.uniswap.com/'):
        # Check if it has any posts (real videos should have posts)
        posts = supabase.table("posts").select("id").eq("video_id", video['id']).execute()

        if len(posts.data) == 0:
            placeholder_videos.append(video)
            print(f"   ❌ Found placeholder video:")
            print(f"      ID: {video['id']}")
            print(f"      Prompt: {video.get('prompt', 'N/A')[:60]}...")
            print(f"      URL: {video_url}")
            print(f"      Creator: {video.get('tg_user_id', 'N/A')}")
            print()

if not placeholder_videos:
    print("   ✅ No placeholder videos found! Database is clean.\n")
    exit(0)

print(f"   Found {len(placeholder_videos)} placeholder video(s)\n")

# Step 2: Show what will be deleted
print("=" * 80)
print("2️⃣  Deletion Plan")
print("=" * 80)
print()

print("The following videos will be DELETED:")
for v in placeholder_videos:
    print(f"   - Video ID {v['id']}: '{v.get('prompt', 'N/A')[:40]}...'")

print()
print("⚠️  This action will:")
print("   - Delete video records from 'videos' table")
print("   - Affected creators' stats will be recalculated")
print("   - No real video files will be deleted (they don't exist)")
print()

# Step 3: Confirm deletion
response = input("❓ Proceed with deletion? (yes/no): ")

if response.lower() != 'yes':
    print("\n❌ Cancelled. No videos were deleted.")
    exit(0)

# Step 4: Delete videos
print("\n3️⃣  Deleting placeholder videos...\n")

deleted_count = 0
affected_creators = set()

for video in placeholder_videos:
    try:
        # Delete the video
        result = supabase.table("videos").delete().eq("id", video['id']).execute()

        if result.data:
            deleted_count += 1
            affected_creators.add(video['tg_user_id'])
            print(f"   ✅ Deleted video ID {video['id']}")
        else:
            print(f"   ⚠️  Failed to delete video ID {video['id']}")

    except Exception as e:
        print(f"   ❌ Error deleting video ID {video['id']}: {e}")

print(f"\n   Deleted {deleted_count} video(s)")

# Step 5: Recalculate creator stats
print("\n4️⃣  Recalculating creator stats...\n")

for creator_id in affected_creators:
    try:
        # Get all videos for this creator
        videos = supabase.table("videos").select("id").eq("tg_user_id", creator_id).execute()
        video_ids = [v["id"] for v in videos.data]

        if not video_ids:
            # No videos left, set everything to 0
            update_data = {
                "total_videos": 0,
                "total_views": 0,
                "total_engagements": 0
            }
        else:
            # Recalculate from posts
            posts = supabase.table("posts") \
                .select("views, likes, comments, shares") \
                .in_("video_id", video_ids) \
                .execute()

            total_views = sum(p.get("views", 0) for p in posts.data)
            total_engagements = sum(
                p.get("likes", 0) + p.get("comments", 0) + p.get("shares", 0)
                for p in posts.data
            )

            update_data = {
                "total_videos": len(video_ids),
                "total_views": total_views,
                "total_engagements": total_engagements
            }

        # Update creator
        supabase.table("creators").update(update_data).eq("tg_user_id", creator_id).execute()

        print(f"   ✅ Updated creator {creator_id}: {update_data['total_videos']} videos, {update_data['total_views']} views")

    except Exception as e:
        print(f"   ❌ Error updating creator {creator_id}: {e}")

print("\n" + "=" * 80)
print("✅ CLEANUP COMPLETE")
print("=" * 80)
print()
print(f"Summary:")
print(f"   - Deleted: {deleted_count} placeholder videos")
print(f"   - Updated: {len(affected_creators)} creator profiles")
print(f"   - Database is now clean!")
print()
