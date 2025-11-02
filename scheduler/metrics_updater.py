"""
Automatic metrics updater for social media posts
Runs periodically to refresh metrics from TikTok, Instagram, etc.
"""
import asyncio
from datetime import datetime
from typing import List, Dict
from loguru import logger
from db.client import Database
from utils.social_scrapers_v2 import scrape_social_metrics


class MetricsUpdater:
    """Periodically updates metrics for all social media posts"""

    def __init__(self):
        self.db = Database()

    async def update_all_metrics(self) -> Dict[str, int]:
        """
        Update metrics for all posts in the database
        Returns summary of updates
        """
        logger.info("🔄 Starting automatic metrics update...")

        # Get all posts that have URLs
        posts_result = self.db.client.table("posts") \
            .select("id, post_url, platform, tg_user_id, video_id") \
            .not_.is_("post_url", "null") \
            .execute()

        stats = {
            "total_posts": len(posts_result.data),
            "updated": 0,
            "failed": 0,
            "skipped": 0
        }

        for post in posts_result.data:
            try:
                post_id = post["id"]
                url = post["post_url"]
                platform = post["platform"]
                tg_user_id = post["tg_user_id"]

                logger.info(f"Updating metrics for post {post_id} ({platform})")

                # Scrape metrics
                metrics = await scrape_social_metrics(url, platform)

                if metrics.get("success"):
                    # Update post metrics
                    await self.db.update_post_metrics(post_id, metrics)

                    # Recalculate creator stats
                    await self.db.recalculate_creator_stats(tg_user_id)

                    stats["updated"] += 1
                    logger.success(f"✅ Updated post {post_id}: {metrics.get('views', 0)} views")
                else:
                    error_msg = metrics.get("error", "Unknown error")
                    logger.warning(f"⚠️ Failed to scrape post {post_id}: {error_msg}")

                    # Save error to database
                    self.db.client.table("posts").update({
                        "metrics_fetch_error": error_msg
                    }).eq("id", post_id).execute()

                    stats["failed"] += 1

                # Add delay to avoid rate limiting
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"❌ Error updating post {post.get('id')}: {e}")
                stats["failed"] += 1

        logger.info(f"""
        📊 Metrics update completed:
        - Total posts: {stats['total_posts']}
        - Updated: {stats['updated']}
        - Failed: {stats['failed']}
        - Skipped: {stats['skipped']}
        """)

        return stats

    async def update_single_post(self, post_id: int) -> bool:
        """Update metrics for a single post"""
        try:
            post_result = self.db.client.table("posts") \
                .select("id, post_url, platform, tg_user_id") \
                .eq("id", post_id) \
                .execute()

            if not post_result.data:
                logger.error(f"Post {post_id} not found")
                return False

            post = post_result.data[0]
            url = post["post_url"]
            platform = post["platform"]
            tg_user_id = post["tg_user_id"]

            # Scrape metrics
            metrics = await scrape_social_metrics(url, platform)

            if metrics.get("success"):
                # Update post metrics
                await self.db.update_post_metrics(post_id, metrics)

                # Recalculate creator stats
                await self.db.recalculate_creator_stats(tg_user_id)

                logger.success(f"✅ Updated post {post_id}: {metrics.get('views', 0)} views")
                return True
            else:
                logger.error(f"Failed to scrape post {post_id}: {metrics.get('error')}")
                return False

        except Exception as e:
            logger.error(f"Error updating post {post_id}: {e}")
            return False


# Singleton instance
_metrics_updater = None

def get_metrics_updater() -> MetricsUpdater:
    """Get or create metrics updater singleton"""
    global _metrics_updater
    if _metrics_updater is None:
        _metrics_updater = MetricsUpdater()
    return _metrics_updater
