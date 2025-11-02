#!/usr/bin/env python3
"""
Script to check videos in Supabase database
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def main():
    """Check videos in the database"""

    # Create Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("=" * 80)
    print("VIDEOS IN SUPABASE DATABASE")
    print("=" * 80)
    print(f"\nDatabase: {SUPABASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Get all videos
        result = supabase.table("videos").select("*").order("created_at", desc=True).execute()

        videos = result.data

        print(f"Total videos found: {len(videos)}\n")

        if len(videos) == 0:
            print("No videos in database.")
            return

        print("=" * 80)

        for idx, video in enumerate(videos, 1):
            print(f"\n[Video {idx}]")
            print(f"ID: {video.get('id')}")
            print(f"Creator (tg_user_id): {video.get('tg_user_id')}")
            print(f"Prompt: {video.get('prompt', 'N/A')[:80]}...")
            print(f"Category: {video.get('category', 'N/A')}")
            print(f"Status: {video.get('status', 'N/A')}")
            print(f"Duration: {video.get('duration_seconds', 'N/A')} seconds")
            print(f"Video URL: {video.get('video_url', 'N/A')[:60]}...")
            print(f"Thumbnail URL: {video.get('thumbnail_url', 'N/A')[:60]}...")
            print(f"Caption: {video.get('caption', 'N/A')[:60]}...")
            print(f"Hashtags: {video.get('hashtags', 'N/A')}")
            print(f"Created: {video.get('created_at', 'N/A')}")
            print("-" * 80)

        # Summary by status
        print("\n" + "=" * 80)
        print("SUMMARY BY STATUS")
        print("=" * 80)

        status_counts = {}
        for video in videos:
            status = video.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        for status, count in sorted(status_counts.items()):
            print(f"{status:20} {count:>5} videos")

        # Summary by category
        print("\n" + "=" * 80)
        print("SUMMARY BY CATEGORY")
        print("=" * 80)

        category_counts = {}
        for video in videos:
            category = video.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1

        for category, count in sorted(category_counts.items()):
            print(f"{category:20} {count:>5} videos")

    except Exception as e:
        print(f"Error fetching videos: {e}")
        return

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
