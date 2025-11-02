"""
Social Media Scrapers - Get metrics from TikTok and Instagram URLs
No API keys required, no login needed
"""
import re
import asyncio
from typing import Optional
from loguru import logger
import httpx
from tiktokapipy.async_api import AsyncTikTokAPI


class TikTokScraper:
    """Scrape TikTok video metrics without API"""

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from TikTok URL"""
        # https://www.tiktok.com/@user/video/1234567890
        # https://vm.tiktok.com/ABC123/
        match = re.search(r'/video/(\d+)', url)
        return match.group(1) if match else None

    @staticmethod
    async def get_metrics(url: str) -> dict:
        """
        Fetch TikTok video metrics from URL

        Returns:
            {
                "views": int,
                "likes": int,
                "comments": int,
                "shares": int,
                "success": bool,
                "error": str | None
            }
        """
        try:
            video_id = TikTokScraper.extract_video_id(url)
            if not video_id:
                return {
                    "success": False,
                    "error": "Invalid TikTok URL format",
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0
                }

            async with AsyncTikTokAPI() as api:
                video = await api.video(video_id)

                stats = video.stats

                return {
                    "success": True,
                    "error": None,
                    "views": stats.play_count or 0,
                    "likes": stats.digg_count or 0,
                    "comments": stats.comment_count or 0,
                    "shares": stats.share_count or 0,
                    "video_id": video_id
                }

        except Exception as e:
            logger.error(f"TikTok scraping error for {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            }


class InstagramScraper:
    """Scrape Instagram Reels metrics without API"""

    @staticmethod
    def extract_shortcode(url: str) -> Optional[str]:
        """Extract shortcode from Instagram URL"""
        # https://www.instagram.com/p/ABC123def/
        # https://www.instagram.com/reel/ABC123def/
        match = re.search(r'/(p|reel)/([^/]+)', url)
        return match.group(2) if match else None

    @staticmethod
    async def get_metrics(url: str) -> dict:
        """
        Fetch Instagram Reel metrics from URL using public GraphQL endpoint

        Returns:
            {
                "views": int,
                "likes": int,
                "comments": int,
                "success": bool,
                "error": str | None
            }
        """
        try:
            shortcode = InstagramScraper.extract_shortcode(url)
            if not shortcode:
                return {
                    "success": False,
                    "error": "Invalid Instagram URL format",
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0
                }

            # Instagram GraphQL public endpoint
            graphql_url = f"https://www.instagram.com/p/{shortcode}/"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }

            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(graphql_url, headers=headers)

                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "views": 0,
                        "likes": 0,
                        "comments": 0,
                        "shares": 0
                    }

                # Extract JSON data from HTML
                html = response.text

                # Look for window._sharedData or embedded JSON
                import json

                # Try to find embedded JSON with video data
                match = re.search(r'window\._sharedData = ({.*?});', html)
                if not match:
                    match = re.search(r'"shortcode_media":({.*?"edge_media_to_comment".*?})', html)

                if not match:
                    # Fallback: Try to parse visible text
                    logger.warning(f"Could not extract JSON from Instagram HTML for {url}")
                    return {
                        "success": False,
                        "error": "Could not parse Instagram data",
                        "views": 0,
                        "likes": 0,
                        "comments": 0,
                        "shares": 0
                    }

                data = json.loads(match.group(1))

                # Navigate to media data
                if "entry_data" in data:
                    media = data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]
                else:
                    media = data

                # Extract metrics
                views = media.get("video_view_count", 0)
                likes = media.get("edge_media_preview_like", {}).get("count", 0)
                comments = media.get("edge_media_to_comment", {}).get("count", 0)

                return {
                    "success": True,
                    "error": None,
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": 0,  # Instagram doesn't expose shares publicly
                    "shortcode": shortcode
                }

        except Exception as e:
            logger.error(f"Instagram scraping error for {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            }


async def scrape_social_metrics(url: str, platform: str) -> dict:
    """
    Universal scraper - detects platform and fetches metrics

    Args:
        url: Social media post URL
        platform: 'tiktok', 'instagram', 'x', or 'twitter'

    Returns:
        {
            "success": bool,
            "platform": str,
            "views": int,
            "likes": int,
            "comments": int,
            "shares": int,
            "error": str | None
        }
    """
    if platform == "tiktok":
        result = await TikTokScraper.get_metrics(url)
    elif platform in ["instagram", "reel"]:
        result = await InstagramScraper.get_metrics(url)
    elif platform in ["twitter", "x"]:
        # Twitter/X scraping is more complex due to auth requirements
        # For now, return zeros and suggest manual entry
        result = {
            "success": False,
            "error": "Twitter/X metrics require API access. Please track manually.",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0
        }
    else:
        result = {
            "success": False,
            "error": f"Platform '{platform}' not supported for scraping",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0
        }

    result["platform"] = platform
    return result


# Test function
async def test_scrapers():
    """Test both scrapers with real URLs"""

    # Test TikTok
    print("=== Testing TikTok Scraper ===")
    tiktok_url = "https://www.tiktok.com/@zachking/video/7351374569783799082"
    tiktok_result = await TikTokScraper.get_metrics(tiktok_url)
    print(f"TikTok Result: {tiktok_result}")

    # Test Instagram
    print("\n=== Testing Instagram Scraper ===")
    instagram_url = "https://www.instagram.com/p/C-example/"  # Need real URL
    instagram_result = await InstagramScraper.get_metrics(instagram_url)
    print(f"Instagram Result: {instagram_result}")


if __name__ == "__main__":
    asyncio.run(test_scrapers())
