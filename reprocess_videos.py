#!/usr/bin/env python3
"""
Re-process videos from October 14, 2025
Downloads from OpenAI and uploads to Supabase Storage
"""
import asyncio
import httpx
from supabase import create_client
from config.settings import settings
from utils.storage import get_storage
from loguru import logger

async def reprocess_videos():
    """Download videos from OpenAI and upload to Supabase"""

    supabase = create_client(settings.supabase_url, settings.supabase_service_key or settings.supabase_key)
    storage = get_storage()

    print("=" * 80)
    print("🔄 RE-PROCESSING VIDEOS FROM OCTOBER 14, 2025")
    print("=" * 80)
    print()

    # Get videos from Oct 14
    result = supabase.table('videos') \
        .select('*') \
        .gte('created_at', '2025-10-14') \
        .execute()

    videos = result.data
    print(f"📊 Found {len(videos)} videos to process\n")

    if not videos:
        print("✅ No videos to process!")
        return

    success_count = 0
    error_count = 0
    skip_count = 0

    for i, video in enumerate(videos, 1):
        video_id = video['id']
        video_url = video.get('video_url', '')
        job_id = video.get('sora_job_id', f'video_{video_id}')

        print(f"\n{'='*80}")
        print(f"📹 Video {i}/{len(videos)} - ID: {video_id}")
        print(f"{'='*80}")
        print(f"   URL: {video_url[:60]}...")

        # Check if already has public URL
        if video.get('watermarked_url') or (video_url and not video_url.startswith('https://api.openai.com/')):
            print(f"   ⏭️  SKIP: Already has public URL")
            skip_count += 1
            continue

        # Check if it's an OpenAI URL
        if not video_url or not video_url.startswith('https://api.openai.com/v1/videos/'):
            print(f"   ❌ SKIP: Not an OpenAI URL")
            skip_count += 1
            continue

        try:
            print(f"   ⬇️  Downloading from OpenAI...")

            # Download video
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.get(
                    video_url,
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    follow_redirects=True
                )

                if response.status_code != 200:
                    print(f"   ❌ ERROR: Download failed - {response.status_code}")
                    print(f"      Response: {response.text[:200]}")
                    error_count += 1
                    continue

                video_bytes = response.content
                size_mb = len(video_bytes) / (1024 * 1024)
                print(f"   ✅ Downloaded {size_mb:.2f} MB")

            # Upload to Supabase Storage
            print(f"   ⬆️  Uploading to Supabase Storage...")

            filename = f"{job_id}.mp4"
            public_video_url, public_thumbnail_url = await storage.upload_video(
                video_bytes,
                filename=filename
            )

            print(f"   ✅ Uploaded successfully!")
            print(f"      Video: {public_video_url[:60]}...")
            print(f"      Thumb: {public_thumbnail_url[:60]}...")

            # Update database
            print(f"   💾 Updating database...")
            update_data = {
                "video_url": public_video_url,
                "thumbnail_url": public_thumbnail_url
            }

            supabase.table('videos').update(update_data).eq('id', video_id).execute()

            print(f"   ✅ Database updated!")
            success_count += 1

        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            error_count += 1
            continue

    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   ⏭️  Skipped: {skip_count}")
    print(f"   📹 Total: {len(videos)}")
    print()

    if success_count > 0:
        print("🎉 Videos are now publicly accessible!")
        print("🌐 Check them at: www.unicreators.app")

    if error_count > 0:
        print("\n⚠️  Some videos failed to process.")
        print("   Check the errors above and try again.")

if __name__ == "__main__":
    asyncio.run(reprocess_videos())
