-- Add metrics columns to posts table
ALTER TABLE posts
ADD COLUMN IF NOT EXISTS views INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS likes INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS comments_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS shares INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_metrics_sync TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS metrics_fetch_error TEXT,
ADD COLUMN IF NOT EXISTS platform_post_id TEXT;

-- Update creators table to track total metrics
ALTER TABLE creators
ADD COLUMN IF NOT EXISTS total_shares INTEGER DEFAULT 0;

-- Create index for faster metrics lookups
CREATE INDEX IF NOT EXISTS idx_posts_metrics ON posts(views DESC, likes DESC);
CREATE INDEX IF NOT EXISTS idx_posts_last_sync ON posts(last_metrics_sync);
