"""
Script para ver el estado de los videos en la base de datos
"""
from db.client import Database
from datetime import datetime

def check_videos_status():
    """Muestra el estado de todos los videos"""

    db = Database()

    print("\n" + "="*80)
    print("📊 ESTADO DE LOS VIDEOS EN LA BASE DE DATOS")
    print("="*80)

    # Obtener todos los videos
    result = db.client.table('videos').select('*').eq('status', 'ready').order('created_at', desc=False).execute()

    # Clasificar por tipo de URL
    public_videos = []
    openai_videos = []

    for video in result.data:
        url = video['video_url']
        if 'api.openai.com' in url:
            openai_videos.append(video)
        else:
            public_videos.append(video)

    print(f"\n✅ Videos con URLs PÚBLICAS (funcionan): {len(public_videos)}")
    print(f"❌ Videos con URLs de OpenAI (expiradas): {len(openai_videos)}")
    print(f"📹 TOTAL: {len(result.data)}")

    # Mostrar videos con URLs públicas
    if public_videos:
        print(f"\n{'─'*80}")
        print("✅ VIDEOS CON URLs PÚBLICAS (ya funcionan en el frontend):")
        print(f"{'─'*80}")
        for v in public_videos:
            created = datetime.fromisoformat(v['created_at'].replace('Z', '').replace('+00:00', ''))
            creator_result = db.client.table('creators').select('username').eq('tg_user_id', v['tg_user_id']).execute()
            username = creator_result.data[0]['username'] if creator_result.data else f"user_{v['tg_user_id']}"

            print(f"\n  📹 ID: {v['id']}")
            print(f"     Usuario: @{username}")
            print(f"     Prompt: {v['prompt'][:60]}...")
            print(f"     Creado: {created.strftime('%Y-%m-%d %H:%M')}")
            print(f"     URL: {v['video_url'][:70]}...")

    # Mostrar videos que necesitan recuperarse
    if openai_videos:
        print(f"\n{'─'*80}")
        print("❌ VIDEOS QUE NECESITAN RECUPERARSE:")
        print(f"{'─'*80}")

        users_affected = {}
        for v in openai_videos:
            user_id = v['tg_user_id']
            if user_id not in users_affected:
                users_affected[user_id] = []
            users_affected[user_id].append(v)

        for user_id, videos in users_affected.items():
            creator_result = db.client.table('creators').select('username').eq('tg_user_id', user_id).execute()
            username = creator_result.data[0]['username'] if creator_result.data else f"user_{user_id}"

            print(f"\n  👤 @{username} (ID: {user_id}) - {len(videos)} videos")

            for v in videos:
                created = datetime.fromisoformat(v['created_at'].replace('Z', '').replace('+00:00', ''))
                print(f"     • ID {v['id']}: {v['prompt'][:50]}... ({created.strftime('%H:%M')})")

    # Instrucciones
    print(f"\n{'='*80}")
    print("📋 SIGUIENTE PASO:")
    print("="*80)

    if openai_videos:
        print(f"\nPara recuperar los {len(openai_videos)} videos con URLs expiradas:")
        print("\n1. Configura tus credenciales de Telegram en .env:")
        print("   TELEGRAM_API_ID=tu_api_id")
        print("   TELEGRAM_API_HASH=tu_api_hash")
        print("   TELEGRAM_PHONE=+521234567890")
        print("\n2. Obtén API ID y Hash desde: https://my.telegram.org/apps")
        print("\n3. Ejecuta el script de recuperación:")
        print("   ./venv/bin/python recover_with_telethon.py")
        print("\n📖 Ver guía completa: cat TELEGRAM_RECOVERY_GUIDE.md")
    else:
        print("\n✅ ¡Todos los videos tienen URLs públicas!")
        print("   No hay nada que recuperar.")

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    check_videos_status()
