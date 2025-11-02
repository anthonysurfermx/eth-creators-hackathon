# Social Media Integration Plan
## TikTok & Instagram Auto-Posting + Metrics Tracking

---

## Overview

Integrate direct posting to TikTok and Instagram from Telegram bot, then track views/engagement automatically to power the leaderboard and drive virality.

---

## Phase 1: API Setup & Registration

### TikTok Requirements
- ✅ **Register app**: https://developers.tiktok.com
- ✅ **Add Content Posting API** product to app
- ✅ **OAuth 2.0 Setup**:
  - Client Key & Client Secret
  - Redirect URI (your Railway URL)
  - Scopes: `user.info.basic`, `video.upload`, `video.list`
- ⚠️ **Audit Process**: Unaudited apps = videos posted as PRIVATE only
  - Need to pass TikTok review for PUBLIC posting
  - Usually takes 1-2 weeks

### Instagram Requirements
- ✅ **Register app**: https://developers.facebook.com/apps
- ✅ **Instagram Graph API** product
- ✅ **Requirements**:
  - Users need Instagram Business/Creator account
  - Account must be linked to Facebook Page
  - OAuth 2.0 with long-lived tokens (90 days)
  - Scopes: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`
- ✅ **Video specs**:
  - Reels: up to 90 seconds
  - Format: MP4, H.264 codec
  - Our videos: 12 seconds ✅

---

## Phase 2: User Flow Design

### Current Flow
```
User → /create [prompt] → Video generated → Telegram
                                        ↓
                          Manual: Download + Post manually
```

### New Flow (Option A - Direct Auto-Post)
```
User → /create [prompt] → Video generated → Telegram
                                        ↓
                          /post tiktok (auto-posts to TikTok)
                          /post instagram (auto-posts to Instagram)
                                        ↓
                          Bot tracks post ID + starts metrics sync
```

### New Flow (Option B - One-Click Post)
```
User → /create [prompt] → Video generated → Telegram
                                        ↓
                          "📤 Post to TikTok" [Button]
                          "📸 Post to Instagram" [Button]
                                        ↓
                          OAuth → Connect account (one time)
                                        ↓
                          Auto-post + Track metrics
```

### New Flow (Option C - Current /posted [url] Enhanced)
```
User → /create [prompt] → Video generated → Telegram
                                        ↓
                User manually posts to TikTok/Instagram
                                        ↓
                /posted [url] → Bot fetches metrics via API
                                        ↓
                Periodic sync every 6 hours
```

**Recommendation**: Start with **Option C** (enhanced current flow) because:
- ✅ No OAuth friction initially
- ✅ Works immediately without TikTok audit approval
- ✅ Users already understand `/posted [url]` command
- ✅ Can add Options A/B later for power users

---

## Phase 3: Database Schema Updates

### New Table: `social_accounts`
```sql
CREATE TABLE social_accounts (
  id BIGSERIAL PRIMARY KEY,
  tg_user_id BIGINT REFERENCES creators(tg_user_id),
  platform TEXT NOT NULL, -- 'tiktok' or 'instagram'
  platform_user_id TEXT NOT NULL,
  username TEXT,
  access_token TEXT NOT NULL,
  refresh_token TEXT,
  token_expires_at TIMESTAMPTZ,
  connected_at TIMESTAMPTZ DEFAULT NOW(),
  last_synced_at TIMESTAMPTZ,
  is_active BOOLEAN DEFAULT TRUE,
  UNIQUE(tg_user_id, platform)
);
```

### Update `posts` table
```sql
-- Add columns for API-fetched metrics
ALTER TABLE posts ADD COLUMN platform_post_id TEXT;
ALTER TABLE posts ADD COLUMN last_metrics_sync TIMESTAMPTZ;
ALTER TABLE posts ADD COLUMN metrics_fetch_error TEXT;
```

---

## Phase 4: Implementation Steps

### 4.1 TikTok Integration

#### Setup OAuth
```python
# utils/tiktok_oauth.py
TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
TIKTOK_REDIRECT_URI = f"{os.getenv('APP_URL')}/oauth/tiktok/callback"

def get_tiktok_auth_url(user_id: int) -> str:
    """Generate TikTok OAuth URL"""
    state = generate_state_token(user_id)
    scopes = ["user.info.basic", "video.list"]

    return f"https://www.tiktok.com/v2/auth/authorize?" \
           f"client_key={TIKTOK_CLIENT_KEY}" \
           f"&scope={','.join(scopes)}" \
           f"&response_type=code" \
           f"&redirect_uri={TIKTOK_REDIRECT_URI}" \
           f"&state={state}"
```

#### Fetch Video Metrics
```python
# utils/tiktok_api.py
async def get_video_metrics(post_id: str, access_token: str) -> dict:
    """Fetch TikTok video metrics"""
    url = "https://open.tiktokapis.com/v2/video/query/"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=headers,
            json={"filters": {"video_ids": [post_id]}}
        )

        data = response.json()
        video = data["data"]["videos"][0]

        return {
            "views": video.get("view_count", 0),
            "likes": video.get("like_count", 0),
            "comments": video.get("comment_count", 0),
            "shares": video.get("share_count", 0)
        }
```

#### Extract Post ID from URL
```python
def extract_tiktok_post_id(url: str) -> str:
    """Extract TikTok video ID from URL"""
    # https://www.tiktok.com/@user/video/1234567890
    match = re.search(r'/video/(\d+)', url)
    return match.group(1) if match else None
```

### 4.2 Instagram Integration

#### Setup OAuth
```python
# utils/instagram_oauth.py
FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
REDIRECT_URI = f"{os.getenv('APP_URL')}/oauth/instagram/callback"

def get_instagram_auth_url(user_id: int) -> str:
    """Generate Instagram OAuth URL"""
    state = generate_state_token(user_id)
    scopes = ["instagram_basic", "pages_read_engagement"]

    return f"https://www.facebook.com/v18.0/dialog/oauth?" \
           f"client_id={FB_APP_ID}" \
           f"&redirect_uri={REDIRECT_URI}" \
           f"&scope={','.join(scopes)}" \
           f"&state={state}"
```

#### Fetch Reel Metrics
```python
# utils/instagram_api.py
async def get_reel_metrics(media_id: str, access_token: str) -> dict:
    """Fetch Instagram Reel metrics"""
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    params = {
        "fields": "like_count,comments_count,plays,shares,reach",
        "access_token": access_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

        return {
            "views": data.get("plays", 0),
            "likes": data.get("like_count", 0),
            "comments": data.get("comments_count", 0),
            "shares": data.get("shares", 0),
            "reach": data.get("reach", 0)
        }
```

#### Extract Media ID from URL
```python
def extract_instagram_media_id(url: str, access_token: str) -> str:
    """Extract Instagram media ID from URL"""
    # https://www.instagram.com/p/ABC123def/
    shortcode = re.search(r'/p/([^/]+)', url).group(1)

    # Need to convert shortcode to media ID via API
    # Or use Instagram Graph API to search by shortcode
    return media_id
```

### 4.3 Metrics Sync Background Job

```python
# jobs/sync_metrics.py
import asyncio
from datetime import datetime, timedelta

async def sync_all_metrics():
    """Sync metrics for all posts (run every 6 hours)"""
    # Get posts that need sync
    posts = await db.get_posts_needing_sync()

    for post in posts:
        try:
            # Get user's access token for platform
            account = await db.get_social_account(
                post["tg_user_id"],
                post["platform"]
            )

            if not account or not account["is_active"]:
                continue

            # Fetch metrics based on platform
            if post["platform"] == "tiktok":
                metrics = await get_video_metrics(
                    post["platform_post_id"],
                    account["access_token"]
                )
            elif post["platform"] == "instagram":
                metrics = await get_reel_metrics(
                    post["platform_post_id"],
                    account["access_token"]
                )

            # Update post metrics
            await db.update_post_metrics(post["id"], metrics)

            # Update creator aggregates
            await db.recalculate_creator_stats(post["tg_user_id"])

        except Exception as e:
            logger.error(f"Failed to sync metrics for post {post['id']}: {e}")
            await db.mark_sync_error(post["id"], str(e))

# Schedule with APScheduler or Celery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(sync_all_metrics, 'interval', hours=6)
```

---

## Phase 5: Bot Commands

### New/Updated Commands

#### `/connect tiktok`
```
🎵 Connect TikTok Account

To track your TikTok video metrics automatically:

1. Click the link below
2. Authorize the app
3. Return to Telegram

[Connect TikTok Account] → (OAuth URL)

Once connected, your TikTok videos will be tracked automatically!
```

#### `/connect instagram`
```
📸 Connect Instagram Account

Requirements:
• Instagram Business or Creator account
• Account linked to a Facebook Page

[Connect Instagram Account] → (OAuth URL)

Your Instagram Reels metrics will sync every 6 hours!
```

#### Enhanced `/posted [url]`
```python
async def posted_command(update, context):
    url = context.args[0]
    platform = detect_platform(url)

    # Check if user has connected account
    account = await db.get_social_account(user_id, platform)

    if account:
        # Extract post ID and fetch metrics via API
        post_id = extract_post_id(url, platform)
        metrics = await fetch_metrics(post_id, account["access_token"], platform)

        await update.message.reply_text(
            f"✅ Post tracked!\n\n"
            f"📊 Current metrics:\n"
            f"👀 Views: {metrics['views']:,}\n"
            f"❤️ Likes: {metrics['likes']:,}\n"
            f"💬 Comments: {metrics['comments']:,}\n"
            f"🔄 Shares: {metrics['shares']:,}\n\n"
            f"I'll sync metrics every 6 hours!"
        )
    else:
        # Fallback to manual tracking
        await update.message.reply_text(
            f"✅ Post registered!\n\n"
            f"💡 Connect your {platform} account to track metrics automatically:\n"
            f"/connect {platform}"
        )
```

---

## Phase 6: Leaderboard Updates

### Real-Time Metrics Display

```python
# Update leaderboard query to include real metrics
async def get_leaderboard(limit: int = 10):
    result = db.client.table("creators") \
        .select("username, total_videos, total_views, total_engagements, total_shares") \
        .order("total_views", desc=True) \
        .limit(limit) \
        .execute()

    return result.data
```

### Leaderboard Message
```
🏆 Top Creators

🥇 @user1 — 125K views
   📹 5 videos • ❤️ 12K likes • 🔄 850 shares

🥈 @user2 — 98K views
   📹 8 videos • ❤️ 9.5K likes • 🔄 620 shares

🥉 @user3 — 76K views
   📹 3 videos • ❤️ 7.8K likes • 🔄 490 shares

Last updated: 2 hours ago
Next sync: in 4 hours
```

---

## Phase 7: Testing & Rollout

### Testing Checklist
- [ ] OAuth flow works for TikTok
- [ ] OAuth flow works for Instagram
- [ ] Metrics fetching works correctly
- [ ] Background sync job runs every 6 hours
- [ ] Token refresh logic works
- [ ] Error handling for expired tokens
- [ ] Leaderboard updates correctly
- [ ] `/posted` command with and without connected accounts

### Rollout Plan
1. **Week 1**: Register apps, get API access
2. **Week 2**: Implement OAuth + metrics fetching
3. **Week 3**: Build background sync job
4. **Week 4**: Beta test with 3-5 users
5. **Week 5**: Public launch

---

## Environment Variables Needed

```bash
# TikTok
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret

# Instagram/Facebook
FB_APP_ID=your_app_id
FB_APP_SECRET=your_app_secret

# App URL (for OAuth redirects)
APP_URL=https://web-production-22a45.up.railway.app
```

---

## Cost Considerations

### API Costs
- ✅ **TikTok API**: FREE (no rate limits mentioned for Content Posting API)
- ✅ **Instagram Graph API**: FREE (standard rate limits apply)

### Rate Limits
- **TikTok**: Typically 100-500 requests/day per app
- **Instagram**: 200 calls/hour per user, 4800 calls/hour per app

For 100 users posting 1 video/day:
- Metrics sync every 6 hours = 4 syncs/day
- 100 users × 4 syncs = 400 API calls/day ✅ Within limits

---

## Next Steps

1. ✅ Research API requirements (DONE)
2. **Register TikTok app**: https://developers.tiktok.com
3. **Register Meta app**: https://developers.facebook.com
4. Implement OAuth flows
5. Build metrics fetching
6. Deploy background sync job
7. Test with real accounts
8. Launch! 🚀
