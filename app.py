"""
ETH Creators Bot v2 - Main Application
FastAPI + Telegram + AgentKit
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from loguru import logger

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from config.settings import settings
from agent.agent import agent
from db.client import db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler.metrics_updater import get_metrics_updater

# Initialize APScheduler
scheduler = AsyncIOScheduler()

# Initialize FastAPI with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""
    # Startup
    logger.info("🚀 Starting ETH Creators Bot v2")
    await agent.initialize()
    logger.info("✅ AgentKit initialized")

    # Initialize Telegram bot
    await tg_app.initialize()
    logger.info("✅ Telegram bot initialized")

    # Start metrics auto-updater (every 6 hours)
    metrics_updater = get_metrics_updater()
    scheduler.add_job(
        metrics_updater.update_all_metrics,
        'interval',
        hours=6,
        id='metrics_updater',
        name='Update social media metrics',
        replace_existing=True
    )
    scheduler.start()
    logger.info("✅ Metrics auto-updater scheduled (every 6 hours)")

    yield
    # Shutdown
    logger.info("👋 Shutting down")
    scheduler.shutdown()
    await tg_app.shutdown()


app = FastAPI(title="ETH Creators Bot", lifespan=lifespan)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Telegram application
tg_app: Application = ApplicationBuilder().token(settings.telegram_bot_token).build()


# ==================== BOT COMMANDS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    welcome = """💎 **¡Bienvenido a ETH Creators!**

¡Crea videos con IA sobre Ethereum usando Sora 2!

**Inicio Rápido:**
1. Escribe `/create [tu idea]` para generar un video
2. Publícalo en TikTok/X/Instagram
3. Regístralo con `/posted [url]` para entrar a la tabla de clasificación

**Comandos:**
• `/create` - Generar video con Sora 2
• `/categories` - Ver temas aprobados
• `/examples` - Inspiración para prompts
• `/leaderboard` - Ver clasificación
• `/stats` - Tu rendimiento
• `/rules` - Guías de contenido

**Gana Recompensas:**
🎯 ¡La gente puede apostar por ti como creador!
📈 Más vistas = Más recompensas
🏆 Compite por el primer lugar

🌐 **Ver todos los videos:** www.ethcreators.app

¡Creemos algo increíble! 🚀"""

    # Create user in database
    await db.get_or_create_creator(
        tg_user_id=update.effective_user.id,
        username=update.effective_user.username,
        display_name=update.effective_user.full_name
    )
    
    await update.message.reply_text(welcome, parse_mode="Markdown")


async def create_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate video with Sora 2"""
    if not context.args:
        await update.message.reply_text(
            "📝 Uso: `/create [tu prompt]`\n\n"
            "Ejemplo: `/create Ethereum transformando las finanzas globales, estilo futurista`\n\n"
            "¿Necesitas ideas? Prueba `/examples`"
        )
        return
    
    prompt = ' '.join(context.args)
    user_id = update.effective_user.id
    username = update.effective_user.username

    # Generate unique folio for tracking
    import time
    import random
    folio = f"VID-{int(time.time())}-{random.randint(1000, 9999)}"

    # Send initial processing message
    processing_msg = await update.message.reply_text(
        f"🎬 **Generando tu video con IA...**\n\n"
        f"📋 **Folio:** `{folio}`\n"
        f"📝 **Tu Prompt:** _{prompt}_\n\n"
        f"⏳ **Tiempo estimado:** 2-5 minutos\n"
        f"🤖 **Tecnología:** OpenAI Sora 2 (generación de video con IA)\n"
        f"💰 **Costo:** ~$4 USD por video de 12 segundos\n\n"
        f"✅ **Validando tu prompt...**\n"
        f"_Asegúrate de que tu idea sea clara y creativa._\n\n"
        f"💡 **Consejo:** Cada video es costoso, ¡hazlo valer!",
        parse_mode="Markdown"
    )

    # Create countdown updater task
    import asyncio
    countdown_active = {"active": True}

    async def update_countdown():
        """Update message every minute with countdown"""
        countdown_messages = [
            ("⏳", "5 minutos restantes", "🎨 La IA está pintando tu visión..."),
            ("⏳", "4 minutos restantes", "🎬 Sora 2 está haciendo su magia..."),
            ("⏳", "3 minutos restantes", "🤖 Renderizando frames..."),
            ("⏱️", "2 minutos restantes", "✨ ¡Casi listo! Puliendo detalles finales..."),
            ("⏱️", "1 minuto restante", "🎉 ¡Toques finales! Tu video casi está listo..."),
            ("🎊", "¡30 segundos!", "🚀 Preparando tu obra maestra...")
        ]

        for i, (emoji, time_text, status_text) in enumerate(countdown_messages):
            if not countdown_active["active"]:
                break

            # Wait before updating (first update after 60s, then every 60s, last one at 30s)
            if i < 5:
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(30)

            if not countdown_active["active"]:
                break

            try:
                await processing_msg.edit_text(
                    f"🎬 **Generando tu video con IA...**\n\n"
                    f"📋 **Folio:** `{folio}`\n"
                    f"📝 **Tu Prompt:** _{prompt}_\n\n"
                    f"{emoji} **{time_text}**\n"
                    f"🤖 **Tecnología:** OpenAI Sora 2 (generación de video con IA)\n"
                    f"💰 **Costo:** ~$4 USD por video de 12 segundos\n\n"
                    f"{status_text}\n\n"
                    f"💡 **Consejo:** Cada video es costoso, ¡hazlo valer!",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.warning(f"Could not update countdown message: {e}")
                break

    # Start countdown in background
    countdown_task = asyncio.create_task(update_countdown())

    # Call simplified flow (direct Sora 2, no Assistant API)
    from simple_flow import create_video_simple
    logger.info(f"🎬 [{folio}] Creating video for @{username}: '{prompt[:50]}...'")

    try:
        result = await create_video_simple(user_id, username, prompt)
    finally:
        # Stop countdown and delete message
        countdown_active["active"] = False
        countdown_task.cancel()
        try:
            await countdown_task
        except asyncio.CancelledError:
            pass

        try:
            await processing_msg.delete()
        except Exception as e:
            logger.warning(f"Could not delete processing message: {e}")
    
    if result.get("success") or result.get("approved"):
        # Video generated successfully
        video_url = result.get("video_url")
        caption = result.get("caption", "")
        hashtags = result.get("hashtags", "")

        # Check if we have a video URL
        is_openai_url = video_url and video_url.startswith("https://api.openai.com/v1/videos/")
        is_public_url = video_url and (video_url.startswith("https://oqdwjrhcdlflfebujnkq.supabase.co/") or video_url.startswith("http"))

        if is_openai_url:
            # Real Sora 2 video - download first, then send to Telegram
            import httpx
            from config.settings import settings

            try:
                # Download video from authenticated Sora 2 endpoint
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.get(
                        video_url,
                        headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                        follow_redirects=True
                    )

                    if response.status_code == 200:
                        video_bytes = response.content

                        # Upload to public storage WHILE we have the bytes
                        try:
                            from utils.storage import get_storage

                            storage = get_storage()
                            public_video_url, public_thumbnail_url = await storage.upload_video(
                                video_bytes,
                                filename=f"{result.get('job_id', 'video')}.mp4"
                            )

                            # Update database with public URL if video_id exists
                            if result.get('video_id'):
                                await db.update_video_by_id(
                                    result['video_id'],
                                    {
                                        "video_url": public_video_url,
                                        "thumbnail_url": public_thumbnail_url
                                    }
                                )
                                logger.info(f"✅ Uploaded to public storage: {public_video_url}")
                            else:
                                logger.warning("No video_id in result, skipping database update")
                        except Exception as upload_error:
                            logger.error(f"❌ CRITICAL: Failed to upload to storage: {upload_error}")
                            logger.error(f"Video ID: {result.get('video_id')}, Job ID: {result.get('job_id')}")
                            import traceback
                            logger.error(traceback.format_exc())

                            # Send alert to user about storage failure
                            await update.message.reply_text(
                                "⚠️ **Storage Upload Failed**\n\n"
                                "Your video was generated but couldn't be uploaded to public storage.\n"
                                "The video will still be sent to you, but it won't be visible on the website.\n\n"
                                f"Video ID: {result.get('video_id')}\n\n"
                                "The admins have been notified.",
                                parse_mode="Markdown"
                            )
                            # Continue anyway - we still have the video bytes for Telegram

                        # Send video bytes to Telegram
                        video_caption = f"✅ **¡Video Listo!**\n\n"
                        video_caption += f"📋 Folio: `{folio}`\n"
                        video_caption += f"🆔 Video ID: #{result.get('video_id')}\n\n"
                        video_caption += f"{caption}\n\n{hashtags}"

                        await update.message.reply_video(
                            video=video_bytes,
                            caption=video_caption,
                            parse_mode="Markdown"
                        )
                    else:
                        # Fallback to URL if download fails
                        await update.message.reply_text(
                            f"✅ **Video generated!**\n\n"
                            f"{caption}\n\n{hashtags}\n\n"
                            f"📥 Download: {video_url}",
                            parse_mode="Markdown"
                        )
            except Exception as e:
                logger.error(f"Error downloading video: {e}")
                await update.message.reply_text(
                    f"✅ **Video generated!**\n\n"
                    f"{caption}\n\n{hashtags}\n\n"
                    f"⚠️ Could not upload to Telegram. Download link: {video_url}",
                    parse_mode="Markdown"
                )

            await update.message.reply_text(
                "✅ **¡Video listo!**\n\n"
                "📤 **Siguientes pasos:**\n"
                "1. Descarga el video de arriba\n"
                "2. Publícalo en TikTok/X/Instagram\n"
                "3. Usa `/posted [url]` para comenzar el seguimiento\n\n"
                "💡 Consejo: ¡Publica en horas pico (6-8 PM) para máximo alcance!\n\n"
                "🌐 **Ver todos los videos:** www.ethcreators.app",
                parse_mode="Markdown"
            )
        elif is_public_url:
            # Video already has public URL (from Supabase Storage)
            # Download and send to Telegram
            try:
                import httpx

                logger.info(f"Downloading video from public URL: {video_url[:80]}...")

                async with httpx.AsyncClient(timeout=120.0) as client:
                    response = await client.get(video_url, follow_redirects=True)

                    if response.status_code == 200:
                        video_bytes = response.content
                        logger.info(f"Downloaded {len(video_bytes)} bytes")

                        # Send to Telegram
                        video_caption = f"✅ **¡Video Listo!**\n\n"
                        video_caption += f"📋 Folio: `{folio}`\n"
                        video_caption += f"🆔 Video ID: #{result.get('video_id')}\n\n"
                        video_caption += f"{caption}\n\n{hashtags}" if caption or hashtags else "¡Mira este increíble video con IA!"

                        await update.message.reply_video(
                            video=video_bytes,
                            caption=video_caption,
                            parse_mode="Markdown"
                        )

                        await update.message.reply_text(
                            "✅ **¡Video listo!**\n\n"
                            "📤 **Siguientes pasos:**\n"
                            "1. Descarga el video de arriba\n"
                            "2. Publícalo en TikTok/X/Instagram\n"
                            "3. Usa `/posted [url]` para comenzar el seguimiento\n\n"
                            "💡 Consejo: ¡Publica en horas pico (6-8 PM) para máximo alcance!\n\n"
                            "🌐 **Ver todos los videos:** www.ethcreators.app",
                            parse_mode="Markdown"
                        )
                        logger.info(f"✅ [{folio}] Video sent to Telegram successfully (Video ID: {result.get('video_id')})")
                    else:
                        # Send URL if download fails
                        await update.message.reply_text(
                            f"✅ **Video generated!**\n\n"
                            f"{caption}\n\n{hashtags}\n\n"
                            f"📥 Watch online: {video_url}",
                            parse_mode="Markdown"
                        )

            except Exception as e:
                logger.error(f"Error sending public video: {e}")
                await update.message.reply_text(
                    f"✅ **Video generated!**\n\n"
                    f"{caption}\n\n{hashtags}\n\n"
                    f"📥 Watch online: {video_url}\n\n"
                    f"⚠️ Could not send to Telegram directly.",
                    parse_mode="Markdown"
                )
        else:
            # No real video URL - inform user
            await update.message.reply_text(
                f"✅ **Video generated!**\n\n"
                f"{caption}\n\n{hashtags}\n\n"
                f"⚠️ Video processing in progress. You'll receive it soon!",
                parse_mode="Markdown"
            )
    else:
        # Content rejected or error
        reason = result.get("reason", "Unknown error")
        suggestions = result.get("suggestions", [])

        # Check if it's a duplicate prompt
        if result.get("duplicate") or result.get("error") == "duplicate_prompt":
            message = f"⚠️ **¡Video Duplicado Detectado!**\n\n"
            message += f"📋 **Folio:** `{folio}` _(bloqueado)_\n"
            message += f"📝 **Tu Prompt:** _{prompt}_\n\n"
            message += f"Ya creaste un video con este prompt exacto recientemente.\n\n"
            message += f"**Razón:** {reason}\n\n"
            message += "💰 **Por qué bloqueamos duplicados:**\n"
            message += "• Cada video cuesta ~$4 USD generar\n"
            message += "• Los videos duplicados desperdician recursos\n"
            message += "• ¡Prueba un ángulo creativo diferente!\n\n"
            message += "💡 **Qué puedes hacer:**\n"
            message += "1. Modifica tu prompt ligeramente\n"
            message += "2. Prueba una idea completamente diferente\n"
            message += "3. Usa `/myvideos` para ver tus videos existentes\n\n"
            if result.get("existing_video_id"):
                message += f"📹 Tu video existente: ID #{result.get('existing_video_id')}\n\n"
            message += "🌐 **Ver tus videos:** www.ethcreators.app"
        # Check if it's the "no credits" error
        elif "NO_CREDITS_AVAILABLE" in reason or "NO_CREDITS_AVAILABLE" in result.get("error", ""):
            message = "🎬💸 **¡Ups! Nos quedamos sin créditos de IA!** 💸🎬\n\n"
            message += "🤖 *El robot de videos se quedó sin combustible...*\n\n"
            message += "😅 Generar videos con Sora 2 cuesta ~$4 USD por video,\n"
            message += "¡y parece que gastamos todo el presupuesto del mes! 🫠\n\n"
            message += "📢 **¡Pero no te preocupes!**\n"
            message += "Los admins ya están recargando la cuenta. 🔋⚡\n\n"
            message += "⏰ **Vuelve en unas horas** y podrás crear tu video.\n\n"
            message += "🌐 Mientras tanto, mira los videos existentes en:\n"
            message += "www.ethcreators.app\n\n"
            message += "💡 *Consejo:* ¡Síguenos en @ETHCreators para saber cuándo volvemos! 🚀"
        else:
            message = "❌ **Tu prompt no fue aprobado**\n\n"
            message += f"**Razón:** {reason}\n\n"

            message += "📋 **Criterios de aprobación:**\n"
            message += "✅ Educación sobre DeFi y Web3\n"
            message += "✅ Ethereum y tecnología blockchain\n"
            message += "✅ Layer 2s (Scroll, Arbitrum)\n"
            message += "✅ Historias de adopción\n\n"

            message += "❌ **No permitido:**\n"
            message += "• Predicciones de precios\n"
            message += "• Menciones a competidores\n"
            message += "• Contenido de apuestas\n"
            message += "• Promesas de \"hacerse rico rápido\"\n\n"

            if suggestions:
                message += "💡 **Ejemplos de prompts aprobados:**\n"
                for i, s in enumerate(suggestions, 1):
                    message += f"{i}. _{s}_\n"
                message += "\n"

        message += "🎨 Usa `/examples` para más inspiración\n"
        message += "📜 Ve `/rules` para más detalles\n\n"
        message += "💰 **Recuerda:** Cada video cuesta ~$4 USD, ¡hazlo valer!\n\n"
        message += "🌐 **Ver galería:** www.ethcreators.app"

        await update.message.reply_text(message, parse_mode="Markdown")


async def posted_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Register social post and auto-fetch metrics"""
    if not context.args:
        await update.message.reply_text(
            "📝 Usage: `/posted [url]`\n\n"
            "Example: `/posted https://tiktok.com/@user/video/123`\n\n"
            "Supported platforms: TikTok, Instagram, Twitter/X"
        )
        return

    url = ' '.join(context.args)
    user_id = update.effective_user.id

    # Validate URL format and detect platform
    platform = _detect_platform(url)

    if not platform:
        await update.message.reply_text(
            "❌ **Invalid URL**\n\n"
            "Please provide a valid URL from:\n"
            "• TikTok: tiktok.com/@user/video/...\n"
            "• Instagram: instagram.com/p/... or instagram.com/reel/...\n"
            "• Twitter/X: twitter.com/.../status/... or x.com/.../status/...\n\n"
            "Try again with a valid URL.",
            parse_mode="Markdown"
        )
        return

    # Check if URL already registered
    existing_post = await db.get_post_by_url(url)
    if existing_post:
        await update.message.reply_text(
            "⚠️ **Post already registered!**\n\n"
            f"This {platform.upper()} post is already being tracked.\n\n"
            "Check your stats: `/stats`",
            parse_mode="Markdown"
        )
        return

    # Get user's videos without posts
    user_videos_result = db.client.table("videos") \
        .select("id, prompt, created_at") \
        .eq("tg_user_id", user_id) \
        .eq("status", "ready") \
        .order("created_at", desc=True) \
        .limit(10) \
        .execute()

    if not user_videos_result.data:
        await update.message.reply_text(
            "❌ **No videos found**\n\n"
            "You need to create a video first with `/create`\n\n"
            "Once you have a video, post it and register with `/posted [url]`",
            parse_mode="Markdown"
        )
        return

    # Filter videos that don't have this URL posted yet
    videos_without_url = []
    for video in user_videos_result.data:
        # Check if this video already has a post with this URL
        existing = db.client.table("posts") \
            .select("id") \
            .eq("video_id", video["id"]) \
            .eq("post_url", url) \
            .execute()

        if not existing.data:
            videos_without_url.append(video)

    if not videos_without_url:
        await update.message.reply_text(
            "⚠️ **All your videos are already posted with this URL**\n\n"
            "Create a new video with `/create` or use a different URL.",
            parse_mode="Markdown"
        )
        return

    # If only one video available, use it automatically
    if len(videos_without_url) == 1:
        selected_video = videos_without_url[0]
    else:
        # Show list of videos to choose from
        message = f"🎬 **Which video did you post?**\n\n"
        message += f"📱 URL: `{url[:50]}...`\n"
        message += f"🌐 Platform: {platform.upper()}\n\n"
        message += "**Your videos:**\n"

        for i, video in enumerate(videos_without_url[:5], 1):
            prompt_preview = video["prompt"][:60] if video["prompt"] else "No prompt"
            message += f"{i}. {prompt_preview}...\n"

        message += f"\n💡 Reply with the number (1-{min(5, len(videos_without_url))})"

        await update.message.reply_text(message, parse_mode="Markdown")

        # TODO: Implement conversation handler to wait for user response
        # For now, use most recent video as fallback
        selected_video = videos_without_url[0]

        await update.message.reply_text(
            f"⚡ **Using most recent video** (#{1})\n\n"
            "_(In future updates, you'll be able to choose from a list)_",
            parse_mode="Markdown"
        )

    last_video = selected_video

    # Send "fetching metrics" message
    fetching_msg = await update.message.reply_text(
        f"📊 **Fetching metrics from {platform.upper()}...**\n\n"
        "This may take a few seconds...",
        parse_mode="Markdown"
    )

    # Extract post ID from URL
    post_id = _extract_post_id(url, platform)

    # Try to fetch metrics automatically
    try:
        from utils.social_scrapers_v2 import scrape_social_metrics

        metrics = await scrape_social_metrics(url, platform)

        # Create post record with metrics
        post_data = {
            "video_id": last_video["id"],
            "tg_user_id": user_id,
            "platform": platform,
            "post_url": url,
            "post_id": post_id,
            "approved": True,
            "has_required_hashtags": True,
            "views": metrics.get("views", 0),
            "likes": metrics.get("likes", 0),
            "comments_count": metrics.get("comments", 0),
            "shares": metrics.get("shares", 0),
            "platform_post_id": metrics.get("video_id") or metrics.get("shortcode") or post_id
        }

        post = await db.create_post(post_data)

        # Delete fetching message
        await fetching_msg.delete()

        # Send success message with metrics
        if metrics["success"]:
            message = (
                f"✅ **Post registered & metrics fetched!**\n\n"
                f"📱 **Platform:** {platform.upper()}\n"
                f"🎬 **Video:** {last_video['category'].replace('_', ' ').title()}\n\n"
                f"📊 **Current metrics:**\n"
                f"👀 Views: {metrics['views']:,}\n"
                f"❤️ Likes: {metrics['likes']:,}\n"
                f"💬 Comments: {metrics['comments']:,}\n"
            )

            if metrics['shares'] > 0:
                message += f"🔄 Shares: {metrics['shares']:,}\n"

            message += (
                f"\n**🔄 Auto-tracking:**\n"
                f"• Metrics will update every 6 hours\n"
                f"• You'll get notified when you climb the leaderboard\n\n"
                f"Check your rank: `/leaderboard`\n"
                f"See your stats: `/stats`"
            )

            # Update creator stats
            await db.recalculate_creator_stats(user_id)
        else:
            # Scraping failed, suggest manual entry
            message = (
                f"✅ **Post registered!**\n\n"
                f"📱 **Platform:** {platform.upper()}\n"
                f"🎬 **Video:** {last_video['category'].replace('_', ' ').title()}\n\n"
                f"⚠️ **Metrics not available yet**\n"
                f"Reason: {metrics.get('error', 'Unknown error')}\n\n"
                f"💡 **Update manually:**\n"
                f"Use `/update [views] [likes] [comments]`\n\n"
                f"Example: `/update 1500 250 30`"
            )

        await update.message.reply_text(message, parse_mode="Markdown")

        logger.info(f"Post registered: {url} for user {user_id}, metrics: {metrics}")

    except Exception as e:
        logger.error(f"Error registering post: {e}")
        await fetching_msg.delete()
        await update.message.reply_text(
            "❌ **Error registering post**\n\n"
            "Something went wrong. Please try again later.",
            parse_mode="Markdown"
        )


async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show leaderboard"""
    top_creators = await db.get_leaderboard(limit=10)

    if not top_creators:
        await update.message.reply_text("🏆 La tabla está vacía. ¡Sé el primero!")
        return

    message = "🏆 **Top Creadores**\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for i, creator in enumerate(top_creators):
        rank = i + 1
        medal = medals[i] if i < 3 else f"{rank}️⃣"
        username = creator.get("username", "Desconocido")
        views = creator.get("total_views", 0)

        message += f"{medal} @{username} — {views:,} vistas\n"

    # Add user's rank if not in top 10
    user_rank = await db.get_user_rank(update.effective_user.id)
    if user_rank and user_rank["rank"] > 10:
        message += f"\n...\n\n"
        message += f"**Tu posición:** #{user_rank['rank']} — {user_rank['total_views']:,} vistas"

    await update.message.reply_text(message, parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user stats"""
    user_id = update.effective_user.id

    # Get user data
    creator = await db.get_creator(user_id)
    user_rank = await db.get_user_rank(user_id)
    videos = await db.get_user_videos(user_id, limit=5)

    if not creator:
        await update.message.reply_text("❌ Sin estadísticas aún. ¡Crea tu primer video con `/create`!")
        return

    message = f"📊 **Tus Estadísticas**\n\n"
    message += f"**Posición:** #{user_rank['rank'] if user_rank else 'N/A'}\n"
    message += f"**Total Videos:** {creator.get('total_videos', 0)}\n"
    message += f"**Total Vistas:** {creator.get('total_views', 0):,}\n"
    message += f"**Total Interacciones:** {creator.get('total_engagements', 0):,}\n\n"

    if user_rank:
        message += f"**Cambio de Posición:** {user_rank.get('rank_change', 0):+d}\n\n"

    message += f"**Videos Recientes:**\n"
    for video in videos[:3]:
        message += f"• {video.get('category', 'desconocido')}: {video.get('prompt', '')[:30]}...\n"

    await update.message.reply_text(message, parse_mode="Markdown")


async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show approved categories"""
    message = """📋 **Categorías de Contenido Aprobadas**

1️⃣ **Características del Ecosistema**
Swaps, pools de liquidez, wallets inteligentes, staking

2️⃣ **Educación DeFi**
Stablecoins, cómo funcionan los swaps, conceptos básicos de DEX

3️⃣ **Tecnología Layer 2**
Scroll, Arbitrum, protección MEV, ordenamiento justo

4️⃣ **Multi-chain**
Swaps cross-chain, interoperabilidad, bridges

5️⃣ **Historias de Éxito**
Primeras transacciones, inclusión financiera, casos de uso real

6️⃣ **Fusión Cultural**
Cultura mexicana + temas DeFi, arte cripto

¿Necesitas ejemplos? Prueba `/examples [categoría]`"""

    await update.message.reply_text(message, parse_mode="Markdown")


async def examples_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show example prompts"""
    from agent.tools.content_validator import ContentValidator
    
    validator = ContentValidator()
    
    category = context.args[0] if context.args else "product_features"
    examples = validator.get_example_prompts(category)
    
    message = f"💡 **Example Prompts: {category.replace('_', ' ').title()}**\n\n"
    
    for i, example in enumerate(examples, 1):
        message += f"{i}. {example}\n\n"
    
    message += "Try creating your own variation! 🎨"
    
    await update.message.reply_text(message, parse_mode="Markdown")


async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show content rules"""
    message = """📜 **Guías de Contenido**

✅ **APROBADO:**
• Educación DeFi y Ethereum
• Tecnología Layer 2 (Scroll, Arbitrum)
• Multi-chain e interoperabilidad
• Historias de éxito de usuarios
• Fusión cultural mexicana

❌ **PROHIBIDO:**
• Predicciones de precios ("moon", "100x")
• Menciones a competidores
• Temas de apuestas/gambling
• Promesas de "hacerse rico rápido"
• Contenido político

⚠️ **Sistema de Strikes:**
• Strike 1: Advertencia
• Strike 2: Cooldown de 24 horas
• Strike 3: Descalificación de la campaña

**Requerido:**
• Videos de 10-60 segundos
• Hashtags: #Ethereum #ETHCreators #DeFi #Web3
• Tono positivo y educativo"""

    await update.message.reply_text(message, parse_mode="Markdown")


async def update_metrics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually update metrics for most recent post"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "📝 Usage: `/update [views] [likes] [comments]`\n\n"
            "Example: `/update 1500 250 30`\n\n"
            "This updates metrics for your most recent post.\n"
            "Use this when automatic fetching fails (Instagram, Twitter/X)."
        )
        return

    user_id = update.effective_user.id

    try:
        views = int(context.args[0])
        likes = int(context.args[1])
        comments = int(context.args[2]) if len(context.args) > 2 else 0
        shares = int(context.args[3]) if len(context.args) > 3 else 0

        # Get user's most recent post
        posts_result = db.client.table("posts") \
            .select("*") \
            .eq("tg_user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        if not posts_result.data:
            await update.message.reply_text(
                "❌ **No posts found**\n\n"
                "You need to register a post first with `/posted [url]`",
                parse_mode="Markdown"
            )
            return

        post = posts_result.data[0]

        # Update metrics
        metrics = {
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": shares
        }

        await db.update_post_metrics(post["id"], metrics)
        await db.recalculate_creator_stats(user_id)

        await update.message.reply_text(
            f"✅ **Metrics updated!**\n\n"
            f"📊 **New metrics:**\n"
            f"👀 Views: {views:,}\n"
            f"❤️ Likes: {likes:,}\n"
            f"💬 Comments: {comments:,}\n"
            + (f"🔄 Shares: {shares:,}\n" if shares > 0 else "") +
            f"\n**Updated post:** {post['post_url']}\n\n"
            f"Check your rank: `/leaderboard`",
            parse_mode="Markdown"
        )

        logger.info(f"Manual metrics update for user {user_id}: {metrics}")

    except ValueError:
        await update.message.reply_text(
            "❌ **Invalid numbers**\n\n"
            "Please use numbers only.\n"
            "Example: `/update 1500 250 30`"
        )
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")
        await update.message.reply_text(
            "❌ **Error updating metrics**\n\n"
            "Something went wrong. Please try again.",
            parse_mode="Markdown"
        )


async def myvideos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's videos and their social posts"""
    user_id = update.effective_user.id

    # Get user's videos
    videos_result = db.client.table("videos") \
        .select("id, prompt, created_at, status") \
        .eq("tg_user_id", user_id) \
        .order("created_at", desc=True) \
        .limit(10) \
        .execute()

    if not videos_result.data:
        await update.message.reply_text(
            "❌ **No videos found**\n\n"
            "Create your first video with `/create [prompt]`",
            parse_mode="Markdown"
        )
        return

    message = "🎬 **Your Videos**\n\n"

    for i, video in enumerate(videos_result.data, 1):
        prompt_preview = video["prompt"][:50] if video["prompt"] else "No prompt"
        status = video.get("status", "unknown")

        message += f"**{i}. Video #{video['id']}**\n"
        message += f"📝 {prompt_preview}...\n"
        message += f"📅 {video['created_at'][:10]}\n"

        # Get posts for this video
        posts_result = db.client.table("posts") \
            .select("platform, post_url, views, likes") \
            .eq("video_id", video["id"]) \
            .execute()

        if posts_result.data:
            message += f"📱 **Posted on:**\n"
            for post in posts_result.data:
                platform_emoji = "🎵" if post["platform"] == "tiktok" else "📸" if post["platform"] == "instagram" else "🐦"
                views = post.get("views", 0)
                likes = post.get("likes", 0)
                message += f"   {platform_emoji} {post['platform'].upper()}: {views:,} views, {likes:,} likes\n"
        else:
            message += f"⚠️ Not posted yet\n"

        message += "\n"

    message += "💡 Use `/posted [url]` to register a social post"

    await update.message.reply_text(message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    await start_command(update, context)


# Register handlers
tg_app.add_handler(CommandHandler("start", start_command))
tg_app.add_handler(CommandHandler("help", help_command))
tg_app.add_handler(CommandHandler("create", create_command))
tg_app.add_handler(CommandHandler("posted", posted_command))
tg_app.add_handler(CommandHandler("update", update_metrics_command))
tg_app.add_handler(CommandHandler("myvideos", myvideos_command))
tg_app.add_handler(CommandHandler("leaderboard", leaderboard_command))
tg_app.add_handler(CommandHandler("stats", stats_command))
tg_app.add_handler(CommandHandler("categories", categories_command))
tg_app.add_handler(CommandHandler("examples", examples_command))
tg_app.add_handler(CommandHandler("rules", rules_command))


# ==================== FASTAPI ROUTES ====================

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook"""
    # Verify webhook secret
    if settings.telegram_webhook_secret:
        token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if token != settings.telegram_webhook_secret:
            raise HTTPException(status_code=403, detail="Invalid secret")
    
    # Process update
    data = await request.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    
    return JSONResponse({"ok": True})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_ready": agent.assistant_id is not None,
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ETH Creators Bot v2",
        "description": "AgentKit-powered UGC video campaign bot",
        "docs": "/docs"
    }


@app.get("/stats")
async def campaign_stats():
    """Campaign statistics - redirects to /api/stats"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/stats")


# ==================== PUBLIC API FOR LANDING PAGE ====================

@app.get("/api/videos")
async def get_public_videos(limit: int = 20, offset: int = 0):
    """
    Get public videos for landing page gallery
    Returns videos with their metadata including social metrics

    NOTE: Filters out videos with OpenAI URLs (not publicly accessible)
          Only returns videos with public Supabase Storage URLs
    """
    try:
        # Get recent completed videos with creator info
        # Note: Fetching more than requested to account for filtering
        result = db.client.table("videos") \
            .select("id, prompt, category, caption, hashtags, video_url, watermarked_url, thumbnail_url, created_at, duration_seconds, tg_user_id, creators(username)") \
            .eq("status", "ready") \
            .order("created_at", desc=True) \
            .range(offset, offset + limit + 20 - 1) \
            .execute()

        videos = []
        for video in result.data:
            # Use watermarked_url if available, fallback to video_url
            video_url = video.get("watermarked_url") or video.get("video_url", "")

            # FILTER: Skip videos with OpenAI URLs (not publicly accessible)
            if video_url and video_url.startswith("https://api.openai.com/"):
                logger.warning(f"Skipping video {video['id']} - has OpenAI URL (not public)")
                continue

            # FILTER: Skip videos without video URLs
            if not video_url or not video_url.startswith("http"):
                logger.warning(f"Skipping video {video['id']} - missing or invalid URL")
                continue

            # Get creator username
            creator_username = None
            if video.get("creators") and isinstance(video["creators"], dict):
                creator_username = video["creators"].get("username")

            # Get associated posts with metrics
            posts_result = db.client.table("posts") \
                .select("platform, post_url, views, likes, comments_count, shares") \
                .eq("video_id", video["id"]) \
                .execute()

            # Aggregate metrics from all posts
            total_views = sum(p.get("views", 0) for p in posts_result.data)
            total_likes = sum(p.get("likes", 0) for p in posts_result.data)
            total_comments = sum(p.get("comments_count", 0) for p in posts_result.data)
            total_shares = sum(p.get("shares", 0) for p in posts_result.data)

            # Get platforms where posted with their URLs
            platform_posts = []
            for p in posts_result.data:
                if p.get("platform") and p.get("post_url"):
                    platform_posts.append({
                        "platform": p.get("platform"),
                        "url": p.get("post_url"),
                        "views": p.get("views", 0),
                        "likes": p.get("likes", 0)
                    })

            videos.append({
                "id": video["id"],
                "prompt": video.get("prompt", ""),
                "category": video.get("category", "unknown"),
                "caption": video.get("caption", ""),
                "hashtags": video.get("hashtags", ""),
                "video_url": video_url,
                "thumbnail_url": video.get("thumbnail_url", ""),
                "created_at": video.get("created_at", ""),
                "duration_seconds": video.get("duration_seconds", 12),
                "creator_username": creator_username,
                "metrics": {
                    "views": total_views,
                    "likes": total_likes,
                    "comments": total_comments,
                    "shares": total_shares,
                    "platform_posts": platform_posts
                }
            })

            # Stop if we have enough videos after filtering
            if len(videos) >= limit:
                break

        return {
            "success": True,
            "videos": videos[:limit],  # Limit to requested amount
            "total": len(videos[:limit]),
            "offset": offset,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error fetching public videos: {e}")
        return {
            "success": False,
            "error": str(e),
            "videos": []
        }


@app.get("/api/stats")
async def get_public_stats():
    """
    Get public statistics for landing page
    Shows total creators, videos, and engagement metrics
    """
    try:
        # Get total videos
        videos_result = db.client.table("videos") \
            .select("id", count="exact") \
            .eq("status", "ready") \
            .execute()

        total_videos = videos_result.count or 0

        # Get total creators (unique users)
        creators_result = db.client.table("creators") \
            .select("id", count="exact") \
            .execute()

        total_creators = creators_result.count or 0

        # Get top creator views directly from creators table
        top_creator_result = db.client.table("creators") \
            .select("total_views") \
            .order("total_views", desc=True) \
            .limit(1) \
            .execute()

        top_creator_views = top_creator_result.data[0].get("total_views", 0) if top_creator_result.data else 0

        # Get total views from all posts
        posts_result = db.client.table("posts") \
            .select("id") \
            .execute()

        total_posts = len(posts_result.data) if posts_result.data else 0

        return {
            "success": True,
            "stats": {
                "total_creators": total_creators,
                "total_videos": total_videos,
                "total_posts": total_posts,
                "top_creator_views": top_creator_views,
                "avg_videos_per_creator": round(total_videos / total_creators, 1) if total_creators > 0 else 0
            }
        }

    except Exception as e:
        logger.error(f"Error fetching public stats: {e}")
        return {
            "success": False,
            "error": str(e),
            "stats": {
                "total_creators": 0,
                "total_videos": 0,
                "total_posts": 0,
                "top_creator_views": 0,
                "avg_videos_per_creator": 0
            }
        }


@app.get("/api/leaderboard")
async def get_public_leaderboard(limit: int = 10):
    """
    Get public leaderboard for landing page
    Shows top creators by views/engagement
    """
    try:
        # Get creators directly from creators table, ordered by views
        result = db.client.table("creators") \
            .select("username, total_views, total_videos, total_engagements") \
            .order("total_views", desc=True) \
            .limit(limit) \
            .execute()

        top_creators = []
        for rank, entry in enumerate(result.data, start=1):
            top_creators.append({
                "rank": rank,
                "username": entry.get("username", "Anonymous"),
                "total_views": entry.get("total_views", 0),
                "total_videos": entry.get("total_videos", 0),
                "total_engagements": entry.get("total_engagements", 0)
            })

        return {
            "success": True,
            "leaderboard": top_creators
        }

    except Exception as e:
        logger.error(f"Error fetching public leaderboard: {e}")
        return {
            "success": False,
            "error": str(e),
            "leaderboard": []
        }


@app.get("/api/leaderboard/winners/{epoch_id}")
async def get_epoch_winners(epoch_id: int):
    """
    Get top 3 creators for a specific epoch (week)
    Used by betting pool smart contract settlement
    Epoch format: YYYYWW (e.g., 202542 = Year 2025, Week 42)
    """
    try:
        from datetime import datetime, timedelta

        # Parse epoch_id to get year and week
        year = epoch_id // 100
        week = epoch_id % 100

        # Calculate date range for this week
        # ISO week starts on Monday
        jan_4 = datetime(year, 1, 4)
        week_1_start = jan_4 - timedelta(days=jan_4.weekday())
        target_week_start = week_1_start + timedelta(weeks=week - 1)
        target_week_end = target_week_start + timedelta(days=7)

        logger.info(f"📊 Fetching winners for epoch {epoch_id} ({target_week_start.date()} to {target_week_end.date()})")

        # Get top 3 creators by total_views (all-time ranking for now)
        # TODO: Filter by time range when you add timestamp tracking
        result = db.client.table("creators") \
            .select("tg_user_id, username, total_views, total_videos, total_engagements") \
            .order("total_views", desc=True) \
            .limit(3) \
            .execute()

        if not result.data or len(result.data) < 3:
            return {
                "success": False,
                "error": "Not enough creators in database",
                "epoch_id": epoch_id,
                "winners": []
            }

        winners = []
        for rank, creator in enumerate(result.data, start=1):
            winners.append({
                "rank": rank,
                "creator_id": creator["tg_user_id"],
                "username": creator["username"],
                "total_views": creator["total_views"],
                "total_videos": creator["total_videos"],
                "total_engagements": creator["total_engagements"]
            })

        logger.info(f"✅ Top 3 for epoch {epoch_id}: {[w['username'] for w in winners]}")

        return {
            "success": True,
            "epoch_id": epoch_id,
            "week_start": target_week_start.isoformat(),
            "week_end": target_week_end.isoformat(),
            "winners": winners,
            "winner_ids": [w["creator_id"] for w in winners]  # For smart contract
        }

    except Exception as e:
        logger.error(f"Error fetching epoch winners: {e}")
        return {
            "success": False,
            "error": str(e),
            "epoch_id": epoch_id,
            "winners": []
        }


@app.post("/api/metrics/update")
async def trigger_metrics_update():
    """
    Manually trigger metrics update for all posts
    Admin endpoint to force refresh of social media metrics
    """
    try:
        logger.info("📊 Manual metrics update triggered via API")
        metrics_updater = get_metrics_updater()
        stats = await metrics_updater.update_all_metrics()

        return {
            "success": True,
            "message": "Metrics update completed",
            "stats": stats
        }

    except Exception as e:
        logger.error(f"Error in manual metrics update: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ==================== HELPER FUNCTIONS ====================

def _detect_platform(url: str) -> str:
    """
    Detect social media platform from URL
    Returns: 'tiktok', 'twitter', 'x', 'instagram', or None
    """
    url_lower = url.lower()

    if "tiktok.com" in url_lower:
        return "tiktok"
    elif "twitter.com" in url_lower:
        return "twitter"
    elif "x.com" in url_lower:
        return "x"
    elif "instagram.com" in url_lower:
        return "instagram"

    return None


def _extract_post_id(url: str, platform: str) -> str:
    """
    Extract post ID from URL

    Examples:
    - TikTok: https://tiktok.com/@user/video/1234567890 -> 1234567890
    - Twitter: https://twitter.com/user/status/1234567890 -> 1234567890
    - Instagram: https://instagram.com/p/ABC123def/ -> ABC123def
    """
    import re

    try:
        if platform == "tiktok":
            match = re.search(r'/video/(\d+)', url)
            return match.group(1) if match else url

        elif platform in ["twitter", "x"]:
            match = re.search(r'/status/(\d+)', url)
            return match.group(1) if match else url

        elif platform == "instagram":
            match = re.search(r'/p/([^/]+)', url)
            return match.group(1) if match else url

        return url

    except Exception as e:
        logger.warning(f"Failed to extract post ID from {url}: {e}")
        return url


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
