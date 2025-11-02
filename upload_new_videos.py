#!/usr/bin/env python3
"""
Script to upload new ETH Creators videos to Supabase
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# New videos data
new_videos = [
    {
        "tg_user_id": 1026323121,  # Tu user ID
        "prompt": "A cinematic explainer video introducing Ethereum (ETH) in a visually stunning, futuristic yet approachable style. The video starts with a glowing digital globe made of interconnected nodes pulsing with light. A friendly AI voice narrates: 'Ethereum is more than money — it's a decentralized computer for the world.' Visuals transition to animated smart contracts forming in the air like holographic blocks. Show diverse people around the world using apps, trading art, lending, gaming, and voting — all powered by Ethereum. Display the Ethereum logo subtly as light particles merge into the symbol. Tone: inspiring, clear, and modern. Color palette: soft violet, deep blue, neon orange accents. Lighting: cinematic, clean, futuristic. End with the line on screen: 'Ethereum — the internet of value.'",
        "video_url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/20251031_2023_01k8ykgzttf4s9cta4h1g3hmz7.mp4",
        "caption": "Ethereum — the internet of value 🌐✨",
        "hashtags": "#Ethereum #ETH #Blockchain #Web3 #Crypto #DeFi #SmartContracts",
        "category": "defi_education",
        "duration_seconds": 45,
        "status": "ready"
    },
    {
        "tg_user_id": 1026323121,
        "prompt": "Video divertido y visualmente impactante que explica qué es Ethereum (ETH) para jóvenes de Monterrey, México. Escena inicial: vista aérea del Cerro de la Silla al atardecer con luces digitales encendiéndose poco a poco, conectando toda la ciudad como una red. Una voz energética y relajada dice: '¿Sabías que Ethereum no es solo una cripto? Es como si el internet tuviera su propio cerebro… pero sin jefes.' Cambia a animaciones de tacos, cheves y programadores regiomontanos construyendo apps en laptops brillantes con logos de Ethereum flotando. Visuales muestran cómo la gente manda dinero, crea arte digital, o abre su propio mini-banco sin pedir permiso. Termina con el narrador diciendo: 'Así que la próxima vez que escuches ETH, no pienses solo en lana… piensa en el futuro del dinero hecho por la raza.'",
        "video_url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/20251031_2038_01k8ykvbzjeq1r3setaz99sdjn.mp4",
        "caption": "¿Qué es Ethereum? - Versión Monterrey 🌮⚡",
        "hashtags": "#Ethereum #ETH #Monterrey #Mexico #Crypto #Web3 #LaRaza",
        "category": "cultural_fusion",
        "duration_seconds": 45,
        "status": "ready"
    },
    {
        "tg_user_id": 1026323121,
        "prompt": "Video corto, divertido y educativo sobre qué es Ethereum (ETH), hecho para la raza de Monterrey. Empieza con un plano del Cerro de la Silla al amanecer, la ciudad despertando, y una voz relajada dice: 'Oye, ¿sabías que Ethereum no es nomás pa' los ricos o pa' los gringos? Es una tecnología bien chida que deja que la raza mueva lana, cree apps y hasta tenga su propio banco… sin que nadie te ande diciendo qué hacer.' El narrador sigue: 'Haz de cuenta que Ethereum es como una carne asada digital: cada quien trae algo pa' compartir — unos ponen el asador, otros la cheve, y todos se benefician. Nomás que aquí, todo corre con código, no con carbón.' Cierra con el narrador diciendo: 'Así que la próxima vez que escuches ETH, no pienses nomás en lana… piensa en el futuro hecho por la raza, sin jefes y sin rollos.'",
        "video_url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/20251031_2023_01k8ykgzttf4s9cta4h1g3hmz7.mp4",
        "caption": "Ethereum explicado 100% regio 🔥🌮",
        "hashtags": "#Ethereum #ETH #Monterrey #Mexico #Crypto #LaRaza #Web3",
        "category": "cultural_fusion",
        "duration_seconds": 50,
        "status": "ready"
    },
    {
        "tg_user_id": 1026323121,
        "prompt": "Video corto, divertido y cinematográfico para anunciar ETH Mexico en Monterrey. Escena inicial: el Cerro de la Silla iluminado con luces moradas y azules al anochecer. Aparece texto brillante: 'ETH Mexico llega al norte 🔥'. Una voz animada, con acento regio, dice: '¡Qué onda raza! Ahora sí, el crypto se viene pa' Monterrey. ETH Mexico va a estar más prendido que una carne asada en sábado.' La voz continúa: 'Va a haber builders, devs, y compas de todo el mundo hablando de cómo Ethereum está cambiando la forma de mover lana, crear apps y conectar comunidades. Y sí… también va a haber cheve 🍻.' La voz cierra con: 'Así que si te late la innovación, el cotorreo y poner a Monterrey en el mapa global del crypto… nos vemos en ETH Mexico, compa. Porque el futuro también se construye acá, entre el cerro y la carne asada.'",
        "video_url": "https://oqdwjrhcdlflfebujnkq.supabase.co/storage/v1/object/public/videos/20251031_2056_01k8ynb3ahezmsqwp9xd3xx3qe.mp4",
        "caption": "ETH Mexico viene a Monterrey 🔥🍻",
        "hashtags": "#ETHMexico #Ethereum #Monterrey #Crypto #Web3 #Blockchain",
        "category": "cultural_fusion",
        "duration_seconds": 50,
        "status": "ready"
    }
]

def main():
    """Upload new videos to Supabase"""
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    print("=" * 80)
    print("UPLOADING NEW ETH CREATORS VIDEOS TO SUPABASE")
    print("=" * 80)
    print(f"\nDatabase: {SUPABASE_URL}")
    print(f"Videos to upload: {len(new_videos)}\n")
    
    uploaded = 0
    errors = 0
    
    for idx, video_data in enumerate(new_videos, 1):
        try:
            print(f"\n[{idx}/{len(new_videos)}] Uploading video...")
            print(f"  Caption: {video_data['caption']}")
            print(f"  Category: {video_data['category']}")
            print(f"  Duration: {video_data['duration_seconds']}s")
            
            # Insert video
            result = supabase.table("videos").insert(video_data).execute()
            
            if result.data:
                video_id = result.data[0]['id']
                print(f"  ✓ Successfully uploaded! Video ID: {video_id}")
                uploaded += 1
            else:
                print(f"  ✗ Failed to upload")
                errors += 1
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            errors += 1
    
    print("\n" + "=" * 80)
    print("UPLOAD SUMMARY")
    print("=" * 80)
    print(f"Successfully uploaded: {uploaded}")
    print(f"Errors: {errors}")
    print(f"Total: {len(new_videos)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
