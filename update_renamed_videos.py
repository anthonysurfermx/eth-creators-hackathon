"""
Actualizar URLs después de renombrar los videos en Supabase
"""
from db.client import Database

def update_renamed_videos():
    db = Database()

    base_url = "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/"

    # Nuevos nombres de archivo (sin espacios ni caracteres raros)
    video_updates = [
        {"id": 13, "filename": "video_13.mp4"},
        {"id": 14, "filename": "video_14.mp4"},
        {"id": 16, "filename": "video_16.mp4"},
        {"id": 17, "filename": "video_17.mp4"},
        {"id": 18, "filename": "video_18.mp4"},
    ]

    print("\n" + "="*80)
    print("🔄 ACTUALIZANDO URLs CON NUEVOS NOMBRES")
    print("="*80)

    updated = 0

    for video in video_updates:
        video_id = video["id"]
        filename = video["filename"]
        video_url = f"{base_url}{filename}"

        print(f"\n📹 Video ID {video_id}: {filename}")

        try:
            db.client.table('videos').update({
                "video_url": video_url
            }).eq('id', video_id).execute()

            print(f"   ✅ Actualizado: {video_url}")
            updated += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print(f"\n{'='*80}")
    print(f"📊 Actualizados: {updated}/5")
    print(f"{'='*80}")
    print(f"\n🎉 Recarga: http://localhost:8080")

if __name__ == "__main__":
    update_renamed_videos()
