"""
Telegram Bot Runner for Railway
Runs only the Telegram bot with webhook support
APIs are served separately on Vercel
"""
import asyncio
from loguru import logger
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
)

from config.settings import settings
from agent.agent import agent
from db.client import db

# Import all command handlers from app.py
from app import (
    start_command,
    create_command,
    posted_command,
    leaderboard_command,
    stats_command,
    categories_command,
    examples_command,
    rules_command,
    help_command
)


async def main():
    """Run Telegram bot with webhook on Railway"""
    logger.info("🚀 Starting Uniswap Creator Bot (Railway)")

    # Initialize AgentKit
    await agent.initialize()
    logger.info("✅ AgentKit initialized")

    # Build Telegram application
    tg_app: Application = ApplicationBuilder().token(settings.telegram_bot_token).build()

    # Register all command handlers
    tg_app.add_handler(CommandHandler("start", start_command))
    tg_app.add_handler(CommandHandler("help", help_command))
    tg_app.add_handler(CommandHandler("create", create_command))
    tg_app.add_handler(CommandHandler("posted", posted_command))
    tg_app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    tg_app.add_handler(CommandHandler("stats", stats_command))
    tg_app.add_handler(CommandHandler("categories", categories_command))
    tg_app.add_handler(CommandHandler("examples", examples_command))
    tg_app.add_handler(CommandHandler("rules", rules_command))

    logger.info("✅ Command handlers registered")

    # Initialize bot
    await tg_app.initialize()
    logger.info("✅ Telegram bot initialized")

    # Start webhook
    webhook_url = settings.telegram_webhook_url
    logger.info(f"🌐 Setting webhook: {webhook_url}")

    await tg_app.bot.set_webhook(
        url=webhook_url,
        secret_token=settings.telegram_webhook_secret
    )

    # Start the bot
    await tg_app.start()
    logger.info("✅ Bot started with webhook mode")
    logger.info(f"📡 Listening on: {webhook_url}")

    # Run polling as fallback (Railway will handle webhook via app.py)
    logger.info("🔄 Starting polling mode...")
    await tg_app.updater.start_polling()

    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down bot...")
        await tg_app.updater.stop()
        await tg_app.stop()
        await tg_app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
