#!/usr/bin/env python3
"""
Script to delete all videos from Supabase database.
Use with caution - this will permanently delete all video records!
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def main():
    """Delete all videos from the database"""

    # Create Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    print("=" * 60)
    print("DELETE ALL VIDEOS - WARNING")
    print("=" * 60)
    print("\nThis script will DELETE ALL videos from the database.")
    print("This action CANNOT be undone!")
    print("\nDatabase:", SUPABASE_URL)

    # Count current videos
    try:
        count_result = supabase.table("videos").select("id", count="exact").execute()
        video_count = count_result.count if count_result.count else 0
        print(f"\nCurrent videos in database: {video_count}")
    except Exception as e:
        print(f"\nError counting videos: {e}")
        return

    if video_count == 0:
        print("\nNo videos to delete. Exiting.")
        return

    # Confirm deletion
    print("\n" + "=" * 60)
    confirmation = input("Type 'DELETE ALL' to confirm deletion: ")

    if confirmation != "DELETE ALL":
        print("\nDeletion cancelled. No changes made.")
        return

    print("\nDeleting all videos...")

    try:
        # Delete all videos
        result = supabase.table("videos").delete().neq("id", 0).execute()

        print(f"✓ Successfully deleted all videos!")

        # Verify deletion
        verify_result = supabase.table("videos").select("id", count="exact").execute()
        remaining = verify_result.count if verify_result.count else 0
        print(f"✓ Remaining videos: {remaining}")

    except Exception as e:
        print(f"\n✗ Error deleting videos: {e}")
        return

    print("\n" + "=" * 60)
    print("Deletion complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
