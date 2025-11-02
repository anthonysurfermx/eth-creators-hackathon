"""
Telegram Notification Utility
Send messages to users from background processes
"""
import asyncio
import httpx
from loguru import logger
from config.settings import settings


class TelegramNotifier:
    """Send notifications to Telegram users"""

    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message to a Telegram user

        Args:
            chat_id: Telegram user ID
            text: Message text
            parse_mode: "Markdown" or "HTML"

        Returns:
            bool: True if message sent successfully
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": parse_mode
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    logger.info(f"✅ Telegram notification sent to user {chat_id}")
                    return True
                else:
                    logger.error(f"❌ Failed to send Telegram message: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Error sending Telegram notification: {e}")
            return False

    async def send_video_ready_notification(self, chat_id: int, video_url: str) -> bool:
        """
        Send notification that video is ready with download link

        Args:
            chat_id: Telegram user ID
            video_url: Public URL of the video on Supabase
        """
        message = f"""🎬 **Your video is ready!**

✅ Your video has been generated successfully and is now live on the web.

📥 **Download your video here:**
{video_url}

📱 **Next steps:**
1. Download the video from the link above
2. Upload it to TikTok with your creative hashtags
3. Come back to Telegram and use `/posted [your_url]` to register your video

🎯 **Remember:** People can bet on you as a creator on the leaderboard!

🌐 **See all videos:** www.unicreators.app

Good luck! 🚀"""

        return await self.send_message(chat_id, message)


# Singleton instance
notifier = TelegramNotifier()
