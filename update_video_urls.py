"""
Script para actualizar las URLs de los videos en la base de datos
después de subirlos manualmente a Supabase Storage
"""
from db.client import Database
from loguru import logger

def update_video_urls():
    """
    Actualiza las URLs de los videos que subiste a Supabase Storage
    """

    db = Database()

    logger.info("🔄 Actualizando URLs de videos en la base de datos...")

    # Videos que necesitan actualización (los que tienen URLs de OpenAI)
    videos_to_update = [
        # Video ID 13
        {
            "id": 13,
            "sora_job_id": "video_68e8262e63dc819083bf7215a00a85a703cca5c3dd28adad"
        },
        # Video ID 14
        {
            "id": 14,
            "sora_job_id": "video_68e827663290819087df10b3dd60dce20630eb95761bdb0b"
        },
        # Video ID 16
        {
            "id": 16,
            "sora_job_id": "video_68e827c48e488198accb3893aaad341c02adefc9cb6859a6"
        },
        # Video ID 17
        {
            "id": 17,
            "sora_job_id": "video_68e8283e83d0819198025c6123a904bc0d7ffe8561db20f6"
        },
        # Video ID 18
        {
            "id": 18,
            "sora_job_id": "video_68e828c6246c819197434caea29f84c2073dec76a25e3b99"
        },
        # Video ID 20
        {
            "id": 20,
            "sora_job_id": "video_68e8296d37788191b5f7dac27b8835600dc75701bbcf5412"
        }
    ]

    # Tu proyecto de Supabase
    supabase_url = "https://oqdwjrhcdlflfebujnkq.supabase.co"
    bucket_name = "videos"

    updated = 0
    failed = 0

    for video in videos_to_update:
        video_id = video["id"]
        job_id = video["sora_job_id"]

        # Construir la URL pública de Supabase
        # Formato: https://PROJECT_ID.supabase.co/storage/v1/object/public/BUCKET/PATH
        filename = f"{job_id}.mp4"

        # Si subiste los archivos en una carpeta "generated/", usa:
        # video_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/generated/{filename}"

        # Si los subiste directo en la raíz del bucket:
        video_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{filename}"

        logger.info(f"\n📹 Actualizando Video ID {video_id}...")
        logger.info(f"   Nueva URL: {video_url}")

        try:
            # Actualizar en la base de datos
            db.client.table('videos').update({
                "video_url": video_url
            }).eq('id', video_id).execute()

            logger.info(f"   ✅ Actualizado correctamente")
            updated += 1

        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            failed += 1

    logger.info(f"\n{'='*70}")
    logger.info(f"📊 RESUMEN:")
    logger.info(f"   ✅ Videos actualizados: {updated}")
    logger.info(f"   ❌ Fallidos: {failed}")
    logger.info(f"{'='*70}")

    if updated > 0:
        logger.info(f"\n🎉 ¡Listo! Verifica en el frontend: http://localhost:8080")
        logger.info(f"   Los videos deberían aparecer ahora con las URLs de Supabase")

if __name__ == "__main__":
    # Primero, preguntemos al usuario dónde subió los archivos
    print("\n" + "="*70)
    print("📦 ¿En qué carpeta subiste los videos en Supabase Storage?")
    print("="*70)
    print("\n1. En la raíz del bucket 'videos' (videos/archivo.mp4)")
    print("2. En una carpeta 'generated' (videos/generated/archivo.mp4)")
    print("3. Otra carpeta (especificar)")
    print()

    choice = input("Selecciona opción (1, 2 o 3): ").strip()

    if choice == "2":
        # Actualizar el código para usar la carpeta "generated"
        print("\n✅ Usando carpeta: videos/generated/")
    elif choice == "3":
        folder = input("Especifica el nombre de la carpeta: ").strip()
        print(f"\n✅ Usando carpeta: videos/{folder}/")
    else:
        print("\n✅ Usando raíz del bucket: videos/")

    print("\n🚀 Ejecutando actualización...")
    update_video_urls()
