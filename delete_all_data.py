#!/usr/bin/env python3
"""
Script to delete ALL data from Supabase database.
This includes: videos, posts, metrics, votes, violations, notifications, and agent conversations.
Use with extreme caution - this will permanently delete all records!
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def count_records(supabase: Client, table_name: str) -> int:
    """Count records in a table"""
    try:
        result = supabase.table(table_name).select("id", count="exact").execute()
        return result.count if result.count else 0
    except Exception as e:
        print(f"Error counting {table_name}: {e}")
        return 0

def delete_all_from_table(supabase: Client, table_name: str) -> bool:
    """Delete all records from a table"""
    try:
        supabase.table(table_name).delete().neq("id", 0).execute()
        return True
    except Exception as e:
        print(f"✗ Error deleting from {table_name}: {e}")
        return False

def main():
    """Delete all data from the database"""

    # Create Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    print("=" * 60)
    print("DELETE ALL DATA - CRITICAL WARNING")
    print("=" * 60)
    print("\nThis script will DELETE ALL DATA from the database:")
    print("  - Videos")
    print("  - Posts")
    print("  - Metrics")
    print("  - Votes")
    print("  - Violations")
    print("  - Notifications")
    print("  - Agent Conversations")
    print("\nCreators and leaderboard will NOT be deleted.")
    print("\nThis action CANNOT be undone!")
    print("\nDatabase:", SUPABASE_URL)

    # Tables to delete (in order to respect foreign key constraints)
    tables_to_delete = [
        "agent_conversations",
        "notifications",
        "violations",
        "votes",
        "metrics",
        "posts",
        "videos"
    ]

    # Count current records
    print("\n" + "=" * 60)
    print("Current record counts:")
    print("=" * 60)
    total_records = 0
    for table in tables_to_delete:
        count = count_records(supabase, table)
        total_records += count
        print(f"{table:25} {count:>10} records")
    print("=" * 60)
    print(f"{'TOTAL':25} {total_records:>10} records")

    if total_records == 0:
        print("\nNo records to delete. Exiting.")
        return

    # Confirm deletion
    print("\n" + "=" * 60)
    print("⚠️  WARNING: You are about to delete ALL content data!")
    confirmation = input("\nType 'DELETE EVERYTHING' to confirm deletion: ")

    if confirmation != "DELETE EVERYTHING":
        print("\nDeletion cancelled. No changes made.")
        return

    print("\n" + "=" * 60)
    print("Deleting all data...")
    print("=" * 60)

    # Delete from each table
    deleted_count = 0
    for table in tables_to_delete:
        count = count_records(supabase, table)
        if count > 0:
            print(f"\nDeleting {count} records from {table}...", end=" ")
            if delete_all_from_table(supabase, table):
                print("✓")
                deleted_count += 1
        else:
            print(f"\nSkipping {table} (empty)")

    # Verify deletion
    print("\n" + "=" * 60)
    print("Verifying deletion...")
    print("=" * 60)
    remaining_total = 0
    for table in tables_to_delete:
        count = count_records(supabase, table)
        remaining_total += count
        print(f"{table:25} {count:>10} records")

    print("\n" + "=" * 60)
    if remaining_total == 0:
        print("✓ SUCCESS: All data deleted successfully!")
    else:
        print(f"⚠️  WARNING: {remaining_total} records still remain")
    print("=" * 60)

if __name__ == "__main__":
    main()
