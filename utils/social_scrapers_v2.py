"""
Social Media Scrapers V2 - Improved with multiple fallback methods
"""
import re
import asyncio
import json
from typing import Optional, Dict
from loguru import logger
import httpx
from bs4 import BeautifulSoup


class TikTokScraperV2:
    """
    Scrape TikTok metrics using oembed API (no auth needed)
    """

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from TikTok URL"""
        # https://www.tiktok.com/@user/video/1234567890
        # https://vm.tiktok.com/ABC123/
        match = re.search(r'/video/(\d+)', url)
        return match.group(1) if match else None

    @staticmethod
    async def get_metrics(url: str) -> Dict:
        """
        Fetch TikTok video metrics using oEmbed API

        Returns dict with views, likes, comments, shares
        """
        try:
            # Method 1: Try oEmbed API (public, no auth)
            oembed_url = f"https://www.tiktok.com/oembed?url={url}"

            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(oembed_url, headers=headers)

                if response.status_code == 200:
                    data = response.json()

                    # oEmbed gives us basic info but not metrics
                    # We need to scrape the HTML page
                    return await TikTokScraperV2._scrape_from_html(url, client)
                else:
                    logger.warning(f"oEmbed failed: {response.status_code}")
                    return await TikTokScraperV2._scrape_from_html(url, client)

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

    @staticmethod
    async def _scrape_from_html(url: str, client: httpx.AsyncClient) -> Dict:
        """Scrape metrics from TikTok HTML page"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }

            response = await client.get(url, headers=headers, follow_redirects=True)

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0
                }

            html = response.text
            soup = BeautifulSoup(html, 'lxml')

            # Look for __UNIVERSAL_DATA script tag
            script_tags = soup.find_all('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})

            if not script_tags:
                script_tags = soup.find_all('script', string=re.compile('__UNIVERSAL_DATA'))

            if script_tags:
                script_content = script_tags[0].string
                data = json.loads(script_content)

                # Navigate through the nested structure
                try:
                    video_detail = data['__DEFAULT_SCOPE__']['webapp.video-detail']
                    item_info = video_detail['itemInfo']['itemStruct']

                    stats = item_info['stats']

                    return {
                        "success": True,
                        "error": None,
                        "views": stats.get('playCount', 0),
                        "likes": stats.get('diggCount', 0),
                        "comments": stats.get('commentCount', 0),
                        "shares": stats.get('shareCount', 0),
                        "video_id": item_info['id']
                    }
                except KeyError as e:
                    logger.warning(f"Could not parse TikTok data structure: {e}")

            # Fallback: Return zeros and mark as needing manual update
            return {
                "success": False,
                "error": "Could not extract metrics from HTML. Please update manually.",
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            }

        except Exception as e:
            logger.error(f"HTML scraping error: {e}")
            return {
                "success": False,
                "error": str(e),
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            }


class InstagramScraperV2:
    """Scrape Instagram Reels metrics"""

    @staticmethod
    def extract_shortcode(url: str) -> Optional[str]:
        """Extract shortcode from Instagram URL"""
        # https://www.instagram.com/p/ABC123def/
        # https://www.instagram.com/reel/ABC123def/
        match = re.search(r'/(p|reel)/([^/]+)', url)
        return match.group(2) if match else None

    @staticmethod
    async def get_metrics(url: str) -> Dict:
        """
        Fetch Instagram Reel metrics

        Instagram has strong anti-scraping, so this may not always work.
        Falls back to manual entry.
        """
        try:
            shortcode = InstagramScraperV2.extract_shortcode(url)
            if not shortcode:
                return {
                    "success": False,
                    "error": "Invalid Instagram URL",
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0
                }

            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "views": 0,
                        "likes": 0,
                        "comments": 0,
                        "shares": 0
                    }

                html = response.text

                # Try to find embedded JSON data
                # Instagram embeds data in script tags
                soup = BeautifulSoup(html, 'lxml')
                scripts = soup.find_all('script', type='application/ld+json')

                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if 'interactionStatistic' in data:
                            stats = {}
                            for stat in data['interactionStatistic']:
                                interaction_type = stat['interactionType'].split('/')[-1]
                                if interaction_type == 'LikeAction':
                                    stats['likes'] = stat['userInteractionCount']
                                elif interaction_type == 'CommentAction':
                                    stats['comments'] = stat['userInteractionCount']
                                elif interaction_type == 'WatchAction':
                                    stats['views'] = stat['userInteractionCount']

                            return {
                                "success": True,
                                "error": None,
                                "views": stats.get('views', 0),
                                "likes": stats.get('likes', 0),
                                "comments": stats.get('comments', 0),
                                "shares": 0,  # Instagram doesn't expose shares
                                "shortcode": shortcode
                            }
                    except:
                        continue

                # Fallback: Manual entry needed
                return {
                    "success": False,
                    "error": "Could not extract metrics. Please update manually with /update",
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0
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


async def scrape_social_metrics(url: str, platform: str) -> Dict:
    """
    Universal scraper with automatic fallback to manual entry

    Args:
        url: Social media post URL
        platform: 'tiktok', 'instagram', 'x', or 'twitter'

    Returns dict with success, views, likes, comments, shares, error
    """
    if platform == "tiktok":
        result = await TikTokScraperV2.get_metrics(url)
    elif platform in ["instagram", "reel"]:
        result = await InstagramScraperV2.get_metrics(url)
    elif platform in ["twitter", "x"]:
        # Twitter requires API access
        result = {
            "success": False,
            "error": "Twitter/X metrics require API access. Use /update to add manually.",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0
        }
    else:
        result = {
            "success": False,
            "error": f"Platform '{platform}' not supported",
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0
        }

    result["platform"] = platform
    return result


# Test with real URLs
async def test_real_urls():
    """Test with actual public videos"""

    print("=== Testing TikTok Scraper V2 ===")
    # Use a known public video (replace with a real one)
    tiktok_url = "https://www.tiktok.com/@tiktok/video/7106594312292453675"
    result = await TikTokScraperV2.get_metrics(tiktok_url)
    print(f"Success: {result['success']}")
    print(f"Views: {result['views']:,}")
    print(f"Likes: {result['likes']:,}")
    print(f"Comments: {result['comments']:,}")
    print(f"Shares: {result['shares']:,}")
    if not result['success']:
        print(f"Error: {result['error']}")

    print("\n=== Testing Instagram Scraper V2 ===")
    # Use a known public reel
    instagram_url = "https://www.instagram.com/reel/C8example/"  # Need real URL
    result = await InstagramScraperV2.get_metrics(instagram_url)
    print(f"Success: {result['success']}")
    print(f"Views: {result['views']:,}")
    print(f"Likes: {result['likes']:,}")
    print(f"Comments: {result['comments']:,}")
    if not result['success']:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    asyncio.run(test_real_urls())
