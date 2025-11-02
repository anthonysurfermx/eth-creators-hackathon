"""
Add new videos to database with proper prompts
"""
from supabase import create_client
from config.settings import settings
from datetime import datetime

supabase = create_client(settings.supabase_url, settings.supabase_key)

# Video data
videos = [
    {
        "id": 19,
        "tg_user_id": 1026323121,  # anthonysurfermx
        "prompt": "Ultra-wide shot of a modern workspace at sunrise. A sleek laptop opens slowly. The Uniswap Interface appears on screen with subtle reflections. Camera glides over the screen in macro focus, showing token pairs, charts, and the swap button in a clean pastel palette (pink × purple gradient lighting).",
        "category": "product_features",
        "video_url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/video_19.mp4",
        "status": "ready",
        "duration_seconds": 12
    },
    {
        "id": 20,
        "tg_user_id": 1026323121,
        "prompt": "Cut to people around the world interacting with the app — a woman in Tokyo, a developer in Mexico City, a trader in London. Slow-motion, natural light, cinematic depth of field. Their faces reflect curiosity and confidence. The screen glows softly on their faces, symbolizing empowerment and transparency.",
        "category": "user_success",
        "video_url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/video_20.mp4",
        "status": "ready",
        "duration_seconds": 12
    },
    {
        "id": 21,
        "tg_user_id": 1026323121,
        "prompt": "The interface elements (charts, tokens, pools) dissolve into abstract particles of light that merge into a fluid digital wave — representing liquidity. The wave flows across the screen, transforming into the Uniswap logo",
        "category": "defi_education",
        "video_url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/video_21.mp4",
        "status": "ready",
        "duration_seconds": 12
    },
    {
        "id": 22,
        "tg_user_id": 1026323121,
        "prompt": "Scene 4 (Outro): Text appears in elegant typography: \"Uniswap Interface — The Simplest Way to Trade On-chain.\" Visual style: cinematic, ultra-HD 8K, volumetric lighting, realistic lens flares, minimalistic color palette (white / magenta / violet), dynamic camera motion. Tone: futuristic yet human, elegant, sophisticated, inspired by Apple Keynote films.",
        "category": "product_features",
        "video_url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/video_22.mp4",
        "status": "ready",
        "duration_seconds": 12
    }
]

print("Insertando videos...")
for video in videos:
    try:
        result = supabase.table("videos").insert(video).execute()
        print(f"✅ Video {video['id']} insertado: {video['prompt'][:60]}...")
    except Exception as e:
        print(f"❌ Error insertando video {video['id']}: {e}")

print("\nActualizando total de videos del creador...")
# Update creator total_videos
creator_result = supabase.table("creators").select("*").eq("tg_user_id", 1026323121).execute()
if creator_result.data:
    videos_count = supabase.table("videos").select("id", count="exact").eq("tg_user_id", 1026323121).execute()
    total = videos_count.count
    supabase.table("creators").update({"total_videos": total}).eq("tg_user_id", 1026323121).execute()
    print(f"✅ Total de videos actualizado: {total}")

print("\n✅ Proceso completado!")
