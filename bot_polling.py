#!/usr/bin/env python3
"""
ETH Creators Bot - Polling Mode (for local development)
Run this instead of app.py to test the bot locally without webhook
"""
import asyncio
from telegram.ext import Application, CommandHandler
from loguru import logger
from config.settings import settings
from agent.agent import agent
from db.client import db

# Import all command handlers from app.py
import sys
sys.path.insert(0, '.')
from app import (
    start_command,
    create_command,
    posted_command,
    leaderboard_command,
    stats_command,
    categories_command,
    examples_command,
    rules_command,
    update_metrics_command,
    myvideos_command,
    help_command
)

async def main():
    """Main function to run the bot in polling mode"""
    logger.info("🚀 Starting ETH Creators Bot v2 (Polling Mode)")

    # Initialize agent
    await agent.initialize()
    logger.info("✅ AgentKit initialized")

    # Build application
    application = Application.builder().token(settings.telegram_bot_token).build()

    # Register all command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("create", create_command))
    application.add_handler(CommandHandler("posted", posted_command))
    application.add_handler(CommandHandler("update", update_metrics_command))
    application.add_handler(CommandHandler("myvideos", myvideos_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("categories", categories_command))
    application.add_handler(CommandHandler("examples", examples_command))
    application.add_handler(CommandHandler("rules", rules_command))

    logger.info("✅ Telegram bot initialized")
    logger.info("🔄 Starting polling... (Press Ctrl+C to stop)")

    # Initialize and start polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Keep the bot running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
