"""
Test Telegram notification system
"""
import asyncio
from utils.telegram_notifier import notifier
from loguru import logger

async def test_notification():
    """Test sending a video ready notification"""
    # Test video URL (use one from Supabase)
    test_video_url = "https://mzvjkebkxcevgpjhvnno.supabase.co/storage/v1/object/public/videos/test_video.mp4"

    # Replace with your actual Telegram user ID
    # You can get this from the database or by sending a message to the bot
    test_user_id = 123456789  # REPLACE WITH REAL USER ID

    logger.info(f"Testing notification to user {test_user_id}")
    logger.info(f"Video URL: {test_video_url}")

    success = await notifier.send_video_ready_notification(test_user_id, test_video_url)

    if success:
        logger.info("✅ Notification sent successfully!")
    else:
        logger.error("❌ Notification failed to send")

if __name__ == "__main__":
    print("🧪 Testing Telegram Notification System\n")
    print("⚠️  NOTE: Update test_user_id in the script with a real Telegram user ID\n")

    # Uncomment to run the test:
    # asyncio.run(test_notification())

    print("Test script ready. Edit the file to add a real user ID and uncomment the test.")
