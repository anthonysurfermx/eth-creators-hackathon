"""
Supabase Database Client
"""
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime
from config.settings import settings
from loguru import logger


class Database:
    """Wrapper around Supabase client with helper methods"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    # ==================== CREATORS ====================
    
    async def get_or_create_creator(self, tg_user_id: int, username: str, display_name: str = None) -> Dict:
        """Get existing creator or create new one"""
        try:
            # Try to get existing
            result = self.client.table("creators").select("*").eq("tg_user_id", tg_user_id).execute()
            
            if result.data:
                return result.data[0]
            
            # Create new
            new_creator = {
                "tg_user_id": tg_user_id,
                "username": username,
                "display_name": display_name or username
            }
            result = self.client.table("creators").insert(new_creator).execute()
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error getting/creating creator: {e}")
            raise
    
    async def get_creator(self, tg_user_id: int) -> Optional[Dict]:
        """Get creator by Telegram user ID"""
        result = self.client.table("creators").select("*").eq("tg_user_id", tg_user_id).execute()
        return result.data[0] if result.data else None
    
    async def update_creator_strikes(self, tg_user_id: int, strikes: int) -> None:
        """Update creator strike count"""
        self.client.table("creators").update({"strikes": strikes}).eq("tg_user_id", tg_user_id).execute()
    
    async def ban_creator(self, tg_user_id: int) -> None:
        """Ban a creator"""
        self.client.table("creators").update({"is_banned": True}).eq("tg_user_id", tg_user_id).execute()
    
    async def set_cooldown(self, tg_user_id: int, cooldown_until: datetime) -> None:
        """Set cooldown period for creator"""
        self.client.table("creators").update({
            "cooldown_until": cooldown_until.isoformat()
        }).eq("tg_user_id", tg_user_id).execute()
    
    # ==================== VIDEOS ====================
    
    async def create_video(self, video_data: Dict) -> Dict:
        """Create new video record"""
        result = self.client.table("videos").insert(video_data).execute()
        return result.data[0]
    
    async def update_video_status(self, video_id: int, status: str, **kwargs) -> None:
        """Update video status and optional fields"""
        update_data = {"status": status, **kwargs}
        self.client.table("videos").update(update_data).eq("id", video_id).execute()

    async def update_video_by_id(self, video_id: int, update_data: Dict) -> None:
        """Update video fields by ID"""
        self.client.table("videos").update(update_data).eq("id", video_id).execute()
    
    async def get_video(self, video_id: int) -> Optional[Dict]:
        """Get video by ID"""
        result = self.client.table("videos").select("*").eq("id", video_id).execute()
        return result.data[0] if result.data else None
    
    async def get_user_videos(self, tg_user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's videos"""
        result = self.client.table("videos").select("*").eq("tg_user_id", tg_user_id).order("created_at", desc=True).limit(limit).execute()
        return result.data
    
    async def get_last_video(self, tg_user_id: int) -> Optional[Dict]:
        """Get user's most recent video"""
        result = self.client.table("videos").select("*").eq("tg_user_id", tg_user_id).order("created_at", desc=True).limit(1).execute()
        return result.data[0] if result.data else None
    
    async def count_videos_today(self, tg_user_id: int) -> int:
        """Count videos created today by user"""
        result = self.client.table("videos").select("id", count="exact").eq("tg_user_id", tg_user_id).gte("created_at", datetime.now().date().isoformat()).execute()
        return result.count or 0
    
    # ==================== POSTS ====================
    
    async def create_post(self, post_data: Dict) -> Dict:
        """Register a social media post"""
        result = self.client.table("posts").insert(post_data).execute()
        return result.data[0]
    
    async def get_post_by_url(self, post_url: str) -> Optional[Dict]:
        """Get post by URL"""
        result = self.client.table("posts").select("*").eq("post_url", post_url).execute()
        return result.data[0] if result.data else None
    
    async def approve_post(self, post_id: int) -> None:
        """Approve a post"""
        self.client.table("posts").update({
            "approved": True,
            "approved_at": datetime.now().isoformat()
        }).eq("id", post_id).execute()
    
    async def get_posts_for_tracking(self, limit: int = 100) -> List[Dict]:
        """Get approved posts that need metrics update"""
        result = self.client.table("posts").select("*, videos(*)").eq("approved", True).order("last_tracked_at").limit(limit).execute()
        return result.data
    
    async def update_post_tracking(self, post_id: int) -> None:
        """Update last tracked timestamp"""
        self.client.table("posts").update({
            "last_tracked_at": datetime.now().isoformat()
        }).eq("id", post_id).execute()
    
    # ==================== METRICS ====================
    
    async def save_metrics(self, metrics_data: Dict) -> Dict:
        """Save metrics snapshot"""
        result = self.client.table("metrics").insert(metrics_data).execute()
        return result.data[0]
    
    async def get_latest_metrics(self, post_id: int) -> Optional[Dict]:
        """Get most recent metrics for a post"""
        result = self.client.table("metrics").select("*").eq("post_id", post_id).order("snapshot_at", desc=True).limit(1).execute()
        return result.data[0] if result.data else None

    async def update_post_metrics(self, post_id: int, metrics: Dict) -> None:
        """Update post with latest metrics"""
        from utils.timezone import now_local

        update_data = {
            "views": metrics.get("views", 0),
            "likes": metrics.get("likes", 0),
            "comments_count": metrics.get("comments", 0),
            "shares": metrics.get("shares", 0),
            "last_metrics_sync": now_local().isoformat(),
            "metrics_fetch_error": metrics.get("error")
        }

        if metrics.get("video_id") or metrics.get("shortcode"):
            update_data["platform_post_id"] = metrics.get("video_id") or metrics.get("shortcode")

        self.client.table("posts").update(update_data).eq("id", post_id).execute()

        # Also save to metrics history
        await self.save_metrics({
            "post_id": post_id,
            "views": metrics.get("views", 0),
            "likes": metrics.get("likes", 0),
            "comments": metrics.get("comments", 0),
            "shares": metrics.get("shares", 0),
            "snapshot_at": now_local().isoformat()
        })

    async def recalculate_creator_stats(self, tg_user_id: int) -> None:
        """Recalculate aggregated stats for a creator from their posts and videos"""
        # Get all posts for this user
        posts_result = self.client.table("posts").select("views, likes, comments_count, shares").eq("tg_user_id", tg_user_id).execute()

        total_views = sum(p.get("views", 0) for p in posts_result.data)
        total_likes = sum(p.get("likes", 0) for p in posts_result.data)
        total_comments = sum(p.get("comments_count", 0) for p in posts_result.data)
        total_shares = sum(p.get("shares", 0) for p in posts_result.data)
        total_engagements = total_likes + total_comments + total_shares

        # Get total videos count
        videos_result = self.client.table("videos").select("id", count="exact").eq("tg_user_id", tg_user_id).execute()
        total_videos = videos_result.count if videos_result.count else 0

        # Update creator
        self.client.table("creators").update({
            "total_views": total_views,
            "total_videos": total_videos,
            "total_engagements": total_engagements,
            "total_shares": total_shares
        }).eq("tg_user_id", tg_user_id).execute()
    
    async def get_metrics_history(self, post_id: int) -> List[Dict]:
        """Get metrics history for a post"""
        result = self.client.table("metrics").select("*").eq("post_id", post_id).order("snapshot_at", desc=True).execute()
        return result.data
    
    # ==================== LEADERBOARD ====================
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top N creators"""
        result = self.client.table("leaderboard").select("*").order("rank").limit(limit).execute()
        return result.data
    
    async def get_user_rank(self, tg_user_id: int) -> Optional[Dict]:
        """Get user's leaderboard entry"""
        result = self.client.table("leaderboard").select("*").eq("tg_user_id", tg_user_id).execute()
        return result.data[0] if result.data else None
    
    async def update_leaderboard(self, tg_user_id: int, stats: Dict) -> None:
        """Update or insert leaderboard entry"""
        existing = await self.get_user_rank(tg_user_id)
        
        if existing:
            self.client.table("leaderboard").update(stats).eq("tg_user_id", tg_user_id).execute()
        else:
            stats["tg_user_id"] = tg_user_id
            self.client.table("leaderboard").insert(stats).execute()
    
    async def recalculate_leaderboard(self) -> None:
        """Recalculate entire leaderboard from raw data"""
        # This would be a complex aggregation query
        # For now, implemented as stored procedure or separate job
        pass
    
    # ==================== NOTIFICATIONS ====================
    
    async def create_notification(self, notification_data: Dict) -> Dict:
        """Create notification"""
        result = self.client.table("notifications").insert(notification_data).execute()
        return result.data[0]
    
    async def get_pending_notifications(self, limit: int = 50) -> List[Dict]:
        """Get unsent notifications"""
        result = self.client.table("notifications").select("*").eq("sent", False).order("created_at").limit(limit).execute()
        return result.data
    
    async def mark_notification_sent(self, notification_id: int) -> None:
        """Mark notification as sent"""
        self.client.table("notifications").update({
            "sent": True,
            "sent_at": datetime.now().isoformat()
        }).eq("id", notification_id).execute()
    
    # ==================== VIOLATIONS ====================
    
    async def log_violation(self, violation_data: Dict) -> Dict:
        """Log content violation"""
        result = self.client.table("violations").insert(violation_data).execute()
        return result.data[0]
    
    async def get_user_violations(self, tg_user_id: int) -> List[Dict]:
        """Get user's violation history"""
        result = self.client.table("violations").select("*").eq("tg_user_id", tg_user_id).order("created_at", desc=True).execute()
        return result.data
    
    # ==================== VOTES ====================
    
    async def cast_vote(self, video_id: int, voter_tg_user_id: int, vote_type: str) -> bool:
        """Cast a vote for a video"""
        try:
            self.client.table("votes").insert({
                "video_id": video_id,
                "voter_tg_user_id": voter_tg_user_id,
                "vote_type": vote_type
            }).execute()
            return True
        except:
            return False  # Already voted
    
    async def get_video_votes(self, video_id: int) -> Dict[str, int]:
        """Get vote counts for a video"""
        result = self.client.table("votes").select("vote_type").eq("video_id", video_id).execute()
        
        vote_counts = {}
        for vote in result.data:
            vote_type = vote["vote_type"]
            vote_counts[vote_type] = vote_counts.get(vote_type, 0) + 1
        
        return vote_counts
    
    # ==================== AGENT CONVERSATIONS ====================
    
    async def save_conversation(self, conversation_data: Dict) -> Dict:
        """Save agent conversation for context"""
        result = self.client.table("agent_conversations").insert(conversation_data).execute()
        return result.data[0]
    
    async def get_user_conversations(self, tg_user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent conversations"""
        result = self.client.table("agent_conversations").select("*").eq("tg_user_id", tg_user_id).order("created_at", desc=True).limit(limit).execute()
        return result.data


# Global database instance
db = Database()
