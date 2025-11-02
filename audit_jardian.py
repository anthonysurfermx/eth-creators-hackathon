#!/usr/bin/env python3
"""
Audit script to investigate Jardian's video issue
"""

from db import SupabaseClient
import json
from datetime import datetime

db = SupabaseClient()

print("=" * 80)
print("🔍 AUDIT: Jardian's Video Investigation")
print("=" * 80)
print()

# 1. Search for creators with 'jardian' in username
print("1️⃣  Searching for creators with 'jardian' in username...\n")
creators = db.client.table("creators").select("*").ilike("username", "%jardian%").execute()

if not creators.data:
    print("❌ No creator found with 'jardian' in username\n")

    # Try searching all recent creators
    print("Searching recent creators (last 24 hours)...")
    all_creators = db.client.table("creators").select("*").order("created_at", desc=True).limit(10).execute()

    if all_creators.data:
        print(f"\n📋 Recent creators:")
        for c in all_creators.data:
            print(f"   - {c['username']} (ID: {c['tg_user_id']})")
else:
    for creator in creators.data:
        print(f"✅ Creator Found:")
        print(f"   User ID: {creator['tg_user_id']}")
        print(f"   Username: @{creator['username']}")
        print(f"   Total Videos: {creator.get('total_videos', 0)}")
        print(f"   Total Views: {creator.get('total_views', 0)}")
        print(f"   Total Engagements: {creator.get('total_engagements', 0)}")
        print(f"   Created: {creator.get('created_at', 'N/A')}")
        print()

        # 2. Get their videos
        print("2️⃣  Fetching videos...\n")
        videos = db.client.table("videos").select("*").eq("tg_user_id", creator['tg_user_id']).order("created_at", desc=True).execute()

        if not videos.data:
            print("   ⚠️  No videos found for this creator")
            print("   This is ISSUE #1: Creator exists but no videos recorded")
        else:
            print(f"   Found {len(videos.data)} video(s)\n")

            for idx, video in enumerate(videos.data, 1):
                print(f"   📹 Video #{idx}:")
                print(f"      ID: {video['id']}")
                print(f"      Prompt: {video.get('prompt', 'N/A')}")
                print(f"      Status: {video.get('status', 'N/A')}")
                print(f"      Platform: {video.get('platform', 'N/A')}")
                print(f"      Platform Video ID: {video.get('platform_video_id', 'N/A')}")
                print(f"      Video URL: {video.get('video_url', 'N/A')}")
                print(f"      Thumbnail URL: {video.get('thumbnail_url', 'N/A')}")
                print(f"      Created: {video.get('created_at', 'N/A')}")
                print()

                # Check issues
                issues = []

                # ISSUE #1: Check if prompt contains Uniswap-related keywords
                prompt = video.get('prompt', '').lower()
                uniswap_keywords = ['uniswap', 'uni', 'defi', 'swap', 'dex', 'liquidity', 'pool', 'amm']
                has_uniswap = any(keyword in prompt for keyword in uniswap_keywords)

                if not has_uniswap:
                    issues.append("❌ ISSUE #1: Prompt doesn't contain Uniswap-related keywords")
                else:
                    print(f"      ✅ Prompt contains Uniswap keywords")

                # ISSUE #2: Check if video URL is missing
                if not video.get('video_url'):
                    issues.append("❌ ISSUE #2: Video URL is missing")
                else:
                    print(f"      ✅ Video URL exists")

                # ISSUE #3: Check if platform posts exist
                platform_posts = db.client.table("platform_posts").select("*").eq("video_id", video['id']).execute()

                if not platform_posts.data:
                    issues.append("❌ ISSUE #3: No platform_posts entry (not shared to social)")
                else:
                    print(f"      ✅ Platform posts exist: {len(platform_posts.data)}")
                    for post in platform_posts.data:
                        print(f"         - {post['platform']}: {post.get('post_url', 'N/A')}")
                        print(f"           Views: {post.get('views', 0)}, Likes: {post.get('likes', 0)}")

                if issues:
                    print()
                    print("      🚨 ISSUES FOUND:")
                    for issue in issues:
                        print(f"         {issue}")

                print()

print("\n" + "=" * 80)
print("3️⃣  CHECKING MODERATION FILTERS")
print("=" * 80)
print()

# Check what the current filters are looking for
print("Current filter implementation:")
print("   Looking in: utils/content_moderator.py")
print()

# Read the moderator file
try:
    with open('utils/content_moderator.py', 'r') as f:
        content = f.read()
        if 'uniswap' in content.lower():
            print("   ✅ Uniswap filter exists in code")
        else:
            print("   ⚠️  Uniswap filter might not be implemented")
except FileNotFoundError:
    print("   ❌ content_moderator.py not found")

print()
print("=" * 80)
print("📊 AUDIT COMPLETE")
print("=" * 80)
