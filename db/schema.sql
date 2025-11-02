-- Uniswap Sora Bot Database Schema
-- PostgreSQL / Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users/Creators table
CREATE TABLE IF NOT EXISTS creators (
    id BIGSERIAL PRIMARY KEY,
    tg_user_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    display_name TEXT,
    strikes INT DEFAULT 0 CHECK (strikes >= 0 AND strikes <= 3),
    is_banned BOOLEAN DEFAULT FALSE,
    cooldown_until TIMESTAMPTZ,
    total_videos INT DEFAULT 0,
    total_views BIGINT DEFAULT 0,
    total_engagements BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Videos generated with Sora 2
CREATE TABLE IF NOT EXISTS videos (
    id BIGSERIAL PRIMARY KEY,
    video_uuid UUID DEFAULT uuid_generate_v4() UNIQUE,
    tg_user_id BIGINT NOT NULL REFERENCES creators(tg_user_id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    enhanced_prompt TEXT, -- Prompt with branding added
    category TEXT CHECK (category IN (
        'product_features',
        'defi_education', 
        'unichain_tech',
        'multi_chain',
        'user_success',
        'cultural_fusion'
    )),
    status TEXT CHECK (status IN (
        'queued',
        'validating',
        'generating',
        'processing',
        'ready',
        'rejected',
        'failed'
    )) DEFAULT 'queued',
    rejection_reason TEXT,
    video_url TEXT,
    watermarked_url TEXT,
    thumbnail_url TEXT,
    duration_seconds INT CHECK (duration_seconds >= 10 AND duration_seconds <= 60),
    caption TEXT,
    hashtags TEXT,
    sora_job_id TEXT,
    generation_time_seconds NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT valid_duration CHECK (duration_seconds IS NULL OR (duration_seconds >= 10 AND duration_seconds <= 60))
);

-- Social media posts
CREATE TABLE IF NOT EXISTS posts (
    id BIGSERIAL PRIMARY KEY,
    video_id BIGINT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    tg_user_id BIGINT NOT NULL REFERENCES creators(tg_user_id) ON DELETE CASCADE,
    platform TEXT CHECK (platform IN ('tiktok', 'twitter', 'x', 'instagram')) NOT NULL,
    post_url TEXT NOT NULL UNIQUE,
    post_id TEXT, -- Platform-specific ID
    approved BOOLEAN DEFAULT FALSE,
    has_required_hashtags BOOLEAN DEFAULT FALSE,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    last_tracked_at TIMESTAMPTZ
);

-- Metrics snapshots (updated every 6 hours)
CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    views BIGINT DEFAULT 0,
    likes BIGINT DEFAULT 0,
    comments BIGINT DEFAULT 0,
    shares BIGINT DEFAULT 0,
    saves BIGINT DEFAULT 0,
    engagement_rate NUMERIC(5,2),
    follower_count BIGINT,
    snapshot_at TIMESTAMPTZ DEFAULT NOW()
);

-- Leaderboard (denormalized for performance)
CREATE TABLE IF NOT EXISTS leaderboard (
    id BIGSERIAL PRIMARY KEY,
    tg_user_id BIGINT NOT NULL UNIQUE REFERENCES creators(tg_user_id) ON DELETE CASCADE,
    username TEXT,
    total_videos INT DEFAULT 0,
    total_views BIGINT DEFAULT 0,
    total_likes BIGINT DEFAULT 0,
    total_shares BIGINT DEFAULT 0,
    total_engagements BIGINT DEFAULT 0,
    avg_engagement_rate NUMERIC(5,2),
    rank INT,
    rank_change INT DEFAULT 0, -- +/- from last update
    category_breakdown JSONB, -- {"cultural_fusion": 5, "product_features": 3}
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notifications sent to users
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    tg_user_id BIGINT NOT NULL REFERENCES creators(tg_user_id) ON DELETE CASCADE,
    type TEXT CHECK (type IN (
        'rank_up',
        'rank_down',
        'milestone',
        'strike_warning',
        'cooldown',
        'prize_won',
        'metrics_update'
    )),
    title TEXT,
    message TEXT,
    data JSONB, -- Additional context
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Strikes/Violations log
CREATE TABLE IF NOT EXISTS violations (
    id BIGSERIAL PRIMARY KEY,
    tg_user_id BIGINT NOT NULL REFERENCES creators(tg_user_id) ON DELETE CASCADE,
    video_id BIGINT REFERENCES videos(id) ON DELETE SET NULL,
    violation_type TEXT NOT NULL,
    description TEXT,
    strike_number INT,
    action_taken TEXT, -- 'warning', 'cooldown', 'ban'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Community votes (for "Best Creativity" prize)
CREATE TABLE IF NOT EXISTS votes (
    id BIGSERIAL PRIMARY KEY,
    video_id BIGINT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    voter_tg_user_id BIGINT NOT NULL REFERENCES creators(tg_user_id) ON DELETE CASCADE,
    vote_type TEXT CHECK (vote_type IN ('upvote', 'creative', 'funny', 'educational')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(video_id, voter_tg_user_id, vote_type)
);

-- Campaign prizes
CREATE TABLE IF NOT EXISTS prizes (
    id BIGSERIAL PRIMARY KEY,
    prize_type TEXT CHECK (prize_type IN (
        'top_10',
        'most_creative',
        'most_viral',
        'early_adopter',
        'consistency'
    )),
    rank INT,
    tg_user_id BIGINT REFERENCES creators(tg_user_id) ON DELETE SET NULL,
    prize_description TEXT,
    status TEXT CHECK (status IN ('pending', 'awarded', 'claimed')),
    awarded_at TIMESTAMPTZ
);

-- Agent conversation history (for context)
CREATE TABLE IF NOT EXISTS agent_conversations (
    id BIGSERIAL PRIMARY KEY,
    tg_user_id BIGINT NOT NULL REFERENCES creators(tg_user_id) ON DELETE CASCADE,
    thread_id TEXT NOT NULL,
    run_id TEXT,
    user_message TEXT,
    assistant_message TEXT,
    tool_calls JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_videos_user ON videos(tg_user_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_created ON videos(created_at DESC);
CREATE INDEX idx_posts_url ON posts(post_url);
CREATE INDEX idx_posts_video ON posts(video_id);
CREATE INDEX idx_posts_platform ON posts(platform);
CREATE INDEX idx_metrics_post ON metrics(post_id);
CREATE INDEX idx_metrics_snapshot ON metrics(snapshot_at DESC);
CREATE INDEX idx_leaderboard_rank ON leaderboard(rank);
CREATE INDEX idx_notifications_user ON notifications(tg_user_id);
CREATE INDEX idx_notifications_sent ON notifications(sent, created_at);
CREATE INDEX idx_violations_user ON violations(tg_user_id);

-- Functions

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_creators_updated_at
    BEFORE UPDATE ON creators
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Increment creator video count
CREATE OR REPLACE FUNCTION increment_creator_videos()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'ready' THEN
        UPDATE creators 
        SET total_videos = total_videos + 1
        WHERE tg_user_id = NEW.tg_user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_increment_videos
    AFTER UPDATE OF status ON videos
    FOR EACH ROW
    WHEN (NEW.status = 'ready' AND OLD.status != 'ready')
    EXECUTE FUNCTION increment_creator_videos();

-- Views for analytics

-- Top videos by engagement
CREATE OR REPLACE VIEW top_videos AS
SELECT 
    v.id,
    v.tg_user_id,
    c.username,
    v.prompt,
    v.category,
    v.video_url,
    v.created_at,
    COALESCE(SUM(m.views), 0) as total_views,
    COALESCE(SUM(m.likes), 0) as total_likes,
    COALESCE(SUM(m.shares), 0) as total_shares,
    COALESCE(SUM(m.likes + m.comments + m.shares), 0) as total_engagements,
    COALESCE(AVG(m.engagement_rate), 0) as avg_engagement_rate
FROM videos v
LEFT JOIN posts p ON p.video_id = v.id
LEFT JOIN metrics m ON m.post_id = p.id
LEFT JOIN creators c ON c.tg_user_id = v.tg_user_id
WHERE v.status = 'ready'
GROUP BY v.id, c.username
ORDER BY total_views DESC;

-- Campaign stats summary
CREATE OR REPLACE VIEW campaign_stats AS
SELECT 
    COUNT(DISTINCT c.tg_user_id) as total_creators,
    COUNT(DISTINCT v.id) as total_videos,
    COUNT(DISTINCT p.id) as total_posts,
    SUM(m.views) as total_views,
    SUM(m.likes) as total_likes,
    SUM(m.shares) as total_shares,
    AVG(m.engagement_rate) as avg_engagement_rate
FROM creators c
LEFT JOIN videos v ON v.tg_user_id = c.tg_user_id AND v.status = 'ready'
LEFT JOIN posts p ON p.video_id = v.id
LEFT JOIN metrics m ON m.post_id = p.id;
