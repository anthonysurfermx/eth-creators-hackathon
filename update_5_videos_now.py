"""
Actualizar los 5 videos con las URLs proporcionadas
"""
from db.client import Database
from loguru import logger

def update_videos_now():
    db = Database()

    # URLs exactas proporcionadas
    video_updates = [
        {"id": 13, "url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/application.octet-stream.mp4"},
        {"id": 14, "url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/application.octet-stream%20(2).mp4"},
        {"id": 16, "url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/application.octet-stream%20(3).mp4"},
        {"id": 17, "url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/application.octet-stream%20(4).mp4"},
        {"id": 18, "url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/application.octet-stream%20(5).mp4"},
    ]

    print("\n" + "="*80)
    print("🔄 ACTUALIZANDO 5 VIDEOS EN LA BASE DE DATOS")
    print("="*80)

    updated = 0

    for video in video_updates:
        video_id = video["id"]
        video_url = video["url"]

        print(f"\n📹 Video ID {video_id}")
        print(f"   URL: {video_url[:80]}...")

        try:
            db.client.table('videos').update({
                "video_url": video_url
            }).eq('id', video_id).execute()

            print(f"   ✅ Actualizado correctamente")
            updated += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print(f"\n{'='*80}")
    print(f"📊 RESUMEN:")
    print(f"   ✅ Videos actualizados: {updated}/5")
    print(f"{'='*80}")
    print(f"\n🎉 ¡Listo! Verifica en: http://localhost:8080")

if __name__ == "__main__":
    update_videos_now()
