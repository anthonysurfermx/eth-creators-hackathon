"""
Script rápido para actualizar los 5 videos subidos a Supabase
Asume que los archivos se llaman: application.octet-stream.mp4, application.octet-stream (1).mp4, etc.
"""
from db.client import Database
from loguru import logger
import urllib.parse

def quick_update_5_videos():
    """
    Actualiza los primeros 5 videos con las URLs de Supabase
    """

    db = Database()

    base_url = "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/"

    # Mapeo de Video ID a nombre de archivo en Supabase
    # AJUSTA ESTOS NOMBRES según los archivos reales que subiste
    video_mappings = [
        {"id": 13, "filename": "application.octet-stream.mp4"},
        {"id": 14, "filename": "application.octet-stream (1).mp4"},
        {"id": 16, "filename": "application.octet-stream (2).mp4"},  # Este lo confirmaste
        {"id": 17, "filename": "application.octet-stream (3).mp4"},
        {"id": 18, "filename": "application.octet-stream (4).mp4"},
    ]

    print("\n" + "="*80)
    print("🔄 ACTUALIZACIÓN RÁPIDA DE 5 VIDEOS")
    print("="*80)
    print("\nVamos a actualizar estos videos:")

    for mapping in video_mappings:
        video_id = mapping["id"]
        filename = mapping["filename"]
        # URL encode el nombre del archivo para manejar espacios y paréntesis
        encoded_filename = urllib.parse.quote(filename)
        full_url = f"{base_url}{encoded_filename}"

        print(f"\n  Video ID {video_id}:")
        print(f"    → {full_url}")

    confirm = input("\n¿Los nombres de archivo son correctos? (s/n): ").strip().lower()

    if confirm != 's':
        print("\n❌ Cancelado. Edita el archivo quick_update_5_videos.py con los nombres correctos.")
        print("   O usa: ./venv/bin/python update_videos_interactive.py")
        return

    updated = 0
    failed = 0

    print("\n🚀 Actualizando base de datos...")

    for mapping in video_mappings:
        video_id = mapping["id"]
        filename = mapping["filename"]
        encoded_filename = urllib.parse.quote(filename)
        full_url = f"{base_url}{encoded_filename}"

        try:
            db.client.table('videos').update({
                "video_url": full_url
            }).eq('id', video_id).execute()

            logger.info(f"✅ Video ID {video_id} actualizado")
            updated += 1

        except Exception as e:
            logger.error(f"❌ Video ID {video_id} falló: {e}")
            failed += 1

    print(f"\n{'='*80}")
    print(f"📊 RESUMEN:")
    print(f"   ✅ Actualizados: {updated}")
    print(f"   ❌ Fallidos: {failed}")
    print(f"{'='*80}")

    if updated > 0:
        print(f"\n🎉 ¡Listo! Verifica en: http://localhost:8080")

if __name__ == "__main__":
    quick_update_5_videos()
