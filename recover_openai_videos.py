"""
Script para recuperar videos de OpenAI y subirlos a Supabase Storage
"""
import asyncio
import httpx
from db.client import Database
from utils.storage import get_storage
from config.settings import settings
from loguru import logger

async def recover_openai_videos():
    """Intenta descargar y re-subir los videos de OpenAI a Supabase Storage"""

    db = Database()
    storage = get_storage()

    # Get videos with OpenAI URLs
    result = db.client.table('videos').select('*').eq('status', 'ready').execute()
    openai_videos = [v for v in result.data if 'api.openai.com' in v['video_url']]

    logger.info(f"📹 Encontrados {len(openai_videos)} videos de OpenAI para recuperar")

    recovered = 0
    failed = 0

    for video in openai_videos:
        video_id = video['id']
        video_url = video['video_url']
        job_id = video.get('sora_job_id', f'video_{video_id}')

        logger.info(f"\n🔄 Intentando recuperar video ID {video_id}...")
        logger.info(f"   Job ID: {job_id}")

        try:
            # Intentar descargar el video con autenticación
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    video_url,
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                    follow_redirects=True
                )

                if response.status_code == 200:
                    video_bytes = response.content
                    size_mb = len(video_bytes) / (1024 * 1024)
                    logger.info(f"   ✅ Descargado: {size_mb:.2f} MB")

                    # Subir a Supabase Storage
                    filename = f"{job_id}.mp4"
                    public_video_url, public_thumbnail_url = await storage.upload_video(
                        video_bytes,
                        filename=filename
                    )

                    # Actualizar BD con URL pública
                    await db.update_video_by_id(video_id, {
                        "video_url": public_video_url,
                        "thumbnail_url": public_thumbnail_url
                    })

                    logger.info(f"   ✅ RECUPERADO: {public_video_url}")
                    recovered += 1

                elif response.status_code == 404:
                    logger.warning(f"   ❌ Video ya expiró (404) - OpenAI solo guarda videos ~24 horas")
                    failed += 1

                elif response.status_code == 401:
                    logger.error(f"   ❌ Error de autenticación (401) - Verifica tu API key")
                    failed += 1

                else:
                    logger.error(f"   ❌ Error HTTP {response.status_code}: {response.text[:100]}")
                    failed += 1

        except Exception as e:
            logger.error(f"   ❌ Error: {str(e)}")
            failed += 1

        # Esperar un poco entre requests para no saturar la API
        await asyncio.sleep(1)

    logger.info(f"\n📊 RESUMEN:")
    logger.info(f"   ✅ Recuperados: {recovered}")
    logger.info(f"   ❌ Fallidos: {failed}")
    logger.info(f"   📹 Total procesados: {len(openai_videos)}")

    return recovered, failed

if __name__ == "__main__":
    asyncio.run(recover_openai_videos())
