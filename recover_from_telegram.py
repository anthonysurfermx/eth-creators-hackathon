"""
Script para recuperar videos desde el historial de Telegram
Lee los mensajes del bot, descarga los videos y los sube a Supabase Storage
"""
import asyncio
import os
from datetime import datetime, timedelta
from telegram import Bot
from telegram.constants import ChatAction
from db.client import Database
from utils.storage import get_storage
from config.settings import settings
from loguru import logger

async def recover_videos_from_telegram():
    """
    Recupera videos desde el historial de Telegram y los sube a Supabase Storage
    """

    # Inicializar bot y servicios
    bot = Bot(token=settings.telegram_bot_token)
    db = Database()
    storage = get_storage()

    logger.info("🤖 Iniciando recuperación de videos desde Telegram...")

    # Obtener todos los videos con URLs de OpenAI que necesitan recuperarse
    result = db.client.table('videos').select('*').eq('status', 'ready').execute()
    openai_videos = [v for v in result.data if 'api.openai.com' in v['video_url']]

    logger.info(f"📹 Encontrados {len(openai_videos)} videos de OpenAI para recuperar")

    if len(openai_videos) == 0:
        logger.info("✅ No hay videos para recuperar")
        return 0, 0

    # Agrupar por usuario
    videos_by_user = {}
    for video in openai_videos:
        user_id = video['tg_user_id']
        if user_id not in videos_by_user:
            videos_by_user[user_id] = []
        videos_by_user[user_id].append(video)

    logger.info(f"👥 Videos distribuidos entre {len(videos_by_user)} usuarios")

    recovered = 0
    failed = 0

    # Para cada usuario, buscar sus videos en el historial
    for user_id, user_videos in videos_by_user.items():
        logger.info(f"\n👤 Procesando usuario {user_id} ({len(user_videos)} videos)...")

        try:
            # Obtener información del creador
            creator_result = db.client.table('creators').select('username').eq('tg_user_id', user_id).execute()
            username = creator_result.data[0]['username'] if creator_result.data else f"user_{user_id}"
            logger.info(f"   Usuario: @{username}")

            # Obtener el rango de fechas de los videos de este usuario
            video_dates = [datetime.fromisoformat(v['created_at'].replace('Z', '+00:00')) for v in user_videos]
            oldest_date = min(video_dates)
            newest_date = max(video_dates)

            logger.info(f"   Buscando videos entre {oldest_date.strftime('%Y-%m-%d %H:%M')} y {newest_date.strftime('%Y-%m-%d %H:%M')}")

            # Buscar mensajes con videos en el chat del usuario
            # Buscar desde un poco antes de la fecha más antigua
            search_from = oldest_date - timedelta(minutes=10)

            # Obtener historial de mensajes con el usuario
            chat_id = user_id
            messages_checked = 0
            videos_found = 0

            logger.info(f"   🔍 Buscando en el historial del chat...")

            # Telegram permite obtener hasta 100 mensajes por request
            # Iteramos desde los más recientes hacia atrás
            offset_id = 0
            limit = 100
            max_iterations = 10  # Máximo 1000 mensajes para no tardar mucho

            for iteration in range(max_iterations):
                try:
                    # Obtener mensajes del chat
                    # Nota: Necesitamos los updates del bot, no hay API directa para historial
                    # Como alternativa, vamos a buscar los mensajes que el bot envió

                    logger.warning(f"   ⚠️ Limitación: Telegram Bot API no permite leer historial de chats privados fácilmente")
                    logger.info(f"   💡 Alternativa: Los videos están en la base de datos pero las URLs expiraron")
                    logger.info(f"   💡 Solución: Descarga manualmente desde Telegram o usa Telegram Client API (requiere user account)")

                    # Para usar esta funcionalidad completa necesitamos:
                    # 1. Telethon o Pyrogram (Telegram Client, no Bot API)
                    # 2. API ID y API Hash de Telegram
                    # 3. Session de usuario (phone number + code)

                    logger.info(f"\n   📋 Videos de este usuario que necesitan recuperación:")
                    for v in user_videos:
                        logger.info(f"      - ID {v['id']}: {v['prompt'][:60]}...")
                        logger.info(f"        Creado: {v['created_at'][:19]}")

                    break

                except Exception as e:
                    logger.error(f"   ❌ Error buscando mensajes: {e}")
                    break

        except Exception as e:
            logger.error(f"   ❌ Error procesando usuario {user_id}: {e}")
            failed += len(user_videos)
            continue

    logger.info(f"\n" + "="*70)
    logger.info(f"📊 RESUMEN:")
    logger.info(f"   ✅ Videos recuperados: {recovered}")
    logger.info(f"   ❌ Videos fallidos: {failed}")
    logger.info(f"   ⚠️  Total intentados: {len(openai_videos)}")
    logger.info(f"\n💡 SIGUIENTE PASO:")
    logger.info(f"   Para recuperar videos de chats privados necesitas:")
    logger.info(f"   1. Usar Telethon/Pyrogram (Telegram User Client)")
    logger.info(f"   2. API ID y Hash desde https://my.telegram.org/apps")
    logger.info(f"   3. Autenticación con tu número de teléfono")
    logger.info(f"\n   O alternativamente:")
    logger.info(f"   - Descarga manualmente desde Telegram Desktop/Mobile")
    logger.info(f"   - Súbelos con: python upload_manual_videos.py")
    logger.info("="*70)

    return recovered, failed

if __name__ == "__main__":
    asyncio.run(recover_videos_from_telegram())
