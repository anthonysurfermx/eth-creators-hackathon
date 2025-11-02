from supabase import create_client
from config.settings import settings

supabase = create_client(settings.supabase_url, settings.supabase_key)

# Read migration SQL
with open('migrations/add_metrics_columns.sql', 'r') as f:
    sql = f.read()

print("Running migration...")
print(sql)

# Execute via raw SQL (Supabase Python client doesn't support raw SQL directly)
# We'll need to run this via Supabase dashboard or psql

print("\n⚠️  Please run this SQL in Supabase SQL Editor:")
print("https://supabase.com/dashboard/project/nqkmillmqrehjxqwifyq/sql/new")
print("\nOr I can add the columns programmatically using RPC...")

# Alternative: Add columns one by one via pgAdmin or Supabase dashboard
print("\nColumns to add to 'posts' table:")
print("- views (INTEGER, DEFAULT 0)")
print("- likes (INTEGER, DEFAULT 0)")
print("- comments_count (INTEGER, DEFAULT 0)")
print("- shares (INTEGER, DEFAULT 0)")
print("- last_metrics_sync (TIMESTAMPTZ)")
print("- metrics_fetch_error (TEXT)")
print("- platform_post_id (TEXT)")
