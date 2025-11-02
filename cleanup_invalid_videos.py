#!/usr/bin/env python3
"""
Limpia videos que no tienen URLs válidas de Supabase.
Solo mantiene los videos con URLs de Supabase Storage que funcionan.
"""

import asyncio
from db.client import Database

async def main():
    db = Database()

    # IDs de videos con URLs válidas de Supabase que funcionan
    valid_video_ids = [13, 14, 16, 17, 18]

    print("=" * 80)
    print("🧹 LIMPIEZA DE VIDEOS INVÁLIDOS")
    print("=" * 80)
    print(f"\n✅ Videos que se mantendrán: {valid_video_ids}")

    # Obtener todos los videos
    result = db.client.table("videos").select("id, video_url, prompt").execute()
    all_videos = result.data

    videos_to_delete = [v for v in all_videos if v["id"] not in valid_video_ids]

    print(f"\n❌ Videos a eliminar: {len(videos_to_delete)}")
    for video in videos_to_delete:
        prompt_preview = video["prompt"][:60] + "..." if len(video["prompt"]) > 60 else video["prompt"]
        print(f"   • ID {video['id']}: {prompt_preview}")

    if not videos_to_delete:
        print("\n✅ No hay videos para eliminar")
        return

    # Eliminar videos automáticamente
    print(f"\n🗑️  Eliminando {len(videos_to_delete)} videos...")
    for video in videos_to_delete:
        db.client.table("videos").delete().eq("id", video["id"]).execute()
        print(f"   ✅ Eliminado ID {video['id']}")

    print(f"\n✅ Limpieza completada. {len(valid_video_ids)} videos activos.")
    print("\n" + "=" * 80)

    # Mostrar videos restantes
    print("📹 VIDEOS ACTIVOS:")
    print("=" * 80)
    result = db.client.table("videos").select("id, prompt, video_url, creators(username)").order("id").execute()

    for video in result.data:
        username = video.get("creators", {}).get("username", "Unknown") if video.get("creators") else "Unknown"
        prompt_preview = video["prompt"][:60] + "..." if len(video["prompt"]) > 60 else video["prompt"]
        print(f"\n  📹 ID {video['id']} - @{username}")
        print(f"     {prompt_preview}")
        print(f"     URL: {video['video_url'][:80]}...")

if __name__ == "__main__":
    asyncio.run(main())
