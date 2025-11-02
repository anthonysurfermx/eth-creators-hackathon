"""
Script interactivo para actualizar URLs de videos en la base de datos
"""
from db.client import Database
from loguru import logger

def update_videos_interactive():
    """
    Actualiza las URLs de los videos de forma interactiva
    """

    db = Database()

    # Videos que necesitan actualización
    videos_pending = [
        {"id": 13, "prompt": "A Mexican mercado transforms into a digital DeFi hub... (21:19)"},
        {"id": 14, "prompt": "A Mexican mercado transforms into a digital DeFi hub... (21:24)"},
        {"id": 16, "prompt": "A Mexican mercado transforms into a digital DeFi hub... (21:26)"},
        {"id": 17, "prompt": "A Mexican mercado transforms into a digital DeFi hub... (21:28)"},
        {"id": 18, "prompt": "A Mexican mercado transforms into a digital DeFi hub... (21:30)"},
        {"id": 20, "prompt": "A Mexican mercado transforms into a digital DeFi hub... (21:33)"},
    ]

    print("\n" + "="*80)
    print("🎬 ACTUALIZAR URLs DE VIDEOS MANUALMENTE")
    print("="*80)
    print("\nSubiste 5 videos a Supabase Storage.")
    print("Vamos a actualizar las URLs en la base de datos.\n")

    updated = 0

    for video in videos_pending:
        video_id = video["id"]
        prompt = video["prompt"]

        print(f"\n{'─'*80}")
        print(f"📹 Video ID {video_id}")
        print(f"   Prompt: {prompt}")
        print(f"{'─'*80}")

        # Preguntar si ya subió este video
        has_video = input(f"\n¿Ya subiste este video a Supabase? (s/n): ").strip().lower()

        if has_video != 's':
            print("   ⏭️  Saltando...")
            continue

        # Pedir la URL
        print("\nPega la URL completa del video en Supabase:")
        print("Ejemplo: https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/archivo.mp4")

        video_url = input("URL: ").strip()

        if not video_url.startswith('http'):
            print("   ❌ URL inválida, saltando...")
            continue

        # Actualizar en la base de datos
        try:
            db.client.table('videos').update({
                "video_url": video_url
            }).eq('id', video_id).execute()

            print(f"   ✅ Video ID {video_id} actualizado correctamente")
            updated += 1

        except Exception as e:
            logger.error(f"   ❌ Error actualizando: {e}")

    print(f"\n{'='*80}")
    print(f"📊 RESUMEN:")
    print(f"   ✅ Videos actualizados: {updated} / {len(videos_pending)}")
    print(f"{'='*80}")

    if updated > 0:
        print(f"\n🎉 ¡Listo! Recarga el frontend: http://localhost:8080")
        print(f"   Los videos actualizados deberían aparecer ahora")

if __name__ == "__main__":
    update_videos_interactive()
