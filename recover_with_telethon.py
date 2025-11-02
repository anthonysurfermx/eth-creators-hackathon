"""
Script para recuperar videos desde Telegram usando Telethon (User Client)
Este script SÍ puede leer el historial de mensajes

REQUISITOS:
1. pip install telethon
2. API ID y API Hash desde https://my.telegram.org/apps
3. Tu número de teléfono para autenticación

USO:
1. Configura en .env:
   TELEGRAM_API_ID=tu_api_id
   TELEGRAM_API_HASH=tu_api_hash
   TELEGRAM_PHONE=+521234567890

2. Ejecuta: python recover_with_telethon.py

3. La primera vez te pedirá un código de verificación que llegará a tu Telegram
"""
import asyncio
import os
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument
from db.client import Database
from utils.storage import get_storage
from loguru import logger

# Configuración
API_ID = os.getenv('TELEGRAM_API_ID')  # Obtener de https://my.telegram.org/apps
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')  # Tu número de teléfono con código de país, ej: +52123456789
SESSION_NAME = 'telegram_recovery_session'

async def recover_videos_with_telethon():
    """
    Recupera videos desde Telegram usando User Client (Telethon)
    """

    # Validar configuración
    if not API_ID or not API_HASH:
        logger.error("❌ Falta configuración en .env:")
        logger.error("   TELEGRAM_API_ID=tu_api_id")
        logger.error("   TELEGRAM_API_HASH=tu_api_hash")
        logger.error("   TELEGRAM_PHONE=+521234567890")
        logger.error("\n   Obtén API ID y Hash desde: https://my.telegram.org/apps")
        return 0, 0

    db = Database()
    storage = get_storage()

    logger.info("🔐 Iniciando sesión en Telegram como usuario...")

    # Crear cliente de Telegram
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    try:
        await client.start(phone=PHONE)
        logger.info("✅ Autenticado en Telegram")

        # Obtener información del bot
        from config.settings import settings
        bot_token = settings.telegram_bot_token
        bot_username = bot_token.split(':')[0]  # Extraer bot ID del token

        logger.info(f"🤖 Bot ID: {bot_username}")

        # Obtener videos que necesitan recuperarse
        result = db.client.table('videos').select('*').eq('status', 'ready').execute()
        openai_videos = [v for v in result.data if 'api.openai.com' in v['video_url']]

        logger.info(f"📹 Videos a recuperar: {len(openai_videos)}")

        # Agrupar por usuario
        videos_by_user = {}
        for video in openai_videos:
            user_id = video['tg_user_id']
            if user_id not in videos_by_user:
                videos_by_user[user_id] = []
            videos_by_user[user_id].append(video)

        recovered = 0
        failed = 0

        # Para cada usuario, buscar videos en el historial
        for user_id, user_videos in videos_by_user.items():
            logger.info(f"\n👤 Usuario {user_id} - {len(user_videos)} videos")

            try:
                # Obtener rango de fechas
                video_dates = [datetime.fromisoformat(v['created_at'].replace('Z', '+00:00').replace('+00:00', '')) for v in user_videos]
                oldest_date = min(video_dates) - timedelta(minutes=30)
                newest_date = max(video_dates) + timedelta(minutes=30)

                logger.info(f"   🔍 Buscando mensajes desde {oldest_date.strftime('%Y-%m-%d %H:%M')}")

                # Buscar mensajes en el chat privado con el usuario
                # IMPORTANTE: Esto solo funciona si TÚ (el dueño de la API key) puedes ver el chat
                # Si eres el admin del bot, busca en el chat del bot con ese usuario

                messages_count = 0
                videos_found = 0

                # Iterar mensajes del chat
                async for message in client.iter_messages(
                    user_id,
                    offset_date=newest_date,
                    reverse=True,
                    limit=200  # Últimos 200 mensajes
                ):
                    messages_count += 1

                    # Salir si ya pasamos la fecha más nueva
                    if message.date > newest_date:
                        break

                    # Buscar mensajes con videos
                    if message.video or (message.media and isinstance(message.media, MessageMediaDocument)):
                        videos_found += 1

                        # Intentar matchear con nuestros videos por fecha
                        message_time = message.date.replace(tzinfo=None)

                        for video_data in user_videos:
                            video_time = datetime.fromisoformat(video_data['created_at'].replace('Z', '').replace('+00:00', ''))
                            time_diff = abs((message_time - video_time).total_seconds())

                            # Si el mensaje es dentro de 5 minutos del video generado
                            if time_diff < 300:  # 5 minutos
                                logger.info(f"   ✅ Encontrado video ID {video_data['id']}")
                                logger.info(f"      Fecha mensaje: {message_time}")
                                logger.info(f"      Fecha video: {video_time}")
                                logger.info(f"      Diferencia: {time_diff:.0f}s")

                                try:
                                    # Descargar el video
                                    logger.info(f"      ⬇️  Descargando...")
                                    video_bytes = await message.download_media(bytes)

                                    if video_bytes:
                                        size_mb = len(video_bytes) / (1024 * 1024)
                                        logger.info(f"      ✅ Descargado: {size_mb:.2f} MB")

                                        # Subir a Supabase Storage
                                        job_id = video_data.get('sora_job_id', f"video_{video_data['id']}")
                                        filename = f"{job_id}.mp4"

                                        public_url, thumbnail_url = await storage.upload_video(
                                            video_bytes,
                                            filename=filename
                                        )

                                        # Actualizar BD
                                        await db.update_video_by_id(video_data['id'], {
                                            "video_url": public_url,
                                            "thumbnail_url": thumbnail_url
                                        })

                                        logger.info(f"      ✅ RECUPERADO: {public_url}")
                                        recovered += 1

                                        # Remover de la lista para no procesarlo de nuevo
                                        user_videos.remove(video_data)

                                except Exception as e:
                                    logger.error(f"      ❌ Error descargando: {e}")
                                    failed += 1

                                break  # Ya encontramos match, siguiente mensaje

                logger.info(f"   📊 Mensajes revisados: {messages_count}")
                logger.info(f"   🎬 Videos encontrados: {videos_found}")

            except Exception as e:
                logger.error(f"   ❌ Error con usuario {user_id}: {e}")
                failed += len(user_videos)

        logger.info(f"\n{'='*70}")
        logger.info(f"📊 RESUMEN FINAL:")
        logger.info(f"   ✅ Videos recuperados: {recovered}")
        logger.info(f"   ❌ Videos fallidos: {failed}")
        logger.info(f"   📹 Total procesados: {len(openai_videos)}")
        logger.info(f"{'='*70}")

        return recovered, failed

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 0, 0

    finally:
        await client.disconnect()
        logger.info("👋 Desconectado de Telegram")

if __name__ == "__main__":
    asyncio.run(recover_videos_with_telethon())
