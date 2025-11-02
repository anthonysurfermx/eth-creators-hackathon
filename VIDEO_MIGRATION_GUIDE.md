# 📹 Guía: Migrar Videos de OpenAI API a Supabase Storage

## Problema

Los videos generados por Sora 2 tienen URLs como:
```
https://api.openai.com/v1/videos/video_abc123/content
```

Estas URLs:
- ❌ Requieren autenticación (Bearer token)
- ❌ No se pueden ver directamente en navegador
- ❌ No funcionan en `<video>` tags sin proxy
- ❌ Expiran después de cierto tiempo

## Solución

Descargar videos de OpenAI y subirlos a Supabase Storage (URLs públicas).

---

## Opción 1: Script de Migración Manual

### Paso 1: Crear el script

```python
# migrate_videos_to_supabase.py

import asyncio
from openai import AsyncOpenAI
from supabase import create_client
from config.settings import settings
import aiohttp
import os

openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
supabase = create_client(settings.supabase_url, settings.supabase_key)

async def migrate_video(video_id: int, openai_url: str):
    """
    Descarga video de OpenAI y sube a Supabase
    """
    try:
        print(f"📥 Descargando video {video_id} de OpenAI...")

        # Download video from OpenAI
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {settings.openai_api_key}'
            }
            async with session.get(openai_url, headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Error descargando: {response.status}")
                    return False

                video_data = await response.read()
                print(f"✅ Descargado: {len(video_data)} bytes")

        # Save temporarily
        temp_file = f"/tmp/video_{video_id}.mp4"
        with open(temp_file, 'wb') as f:
            f.write(video_data)

        # Upload to Supabase Storage
        print(f"📤 Subiendo a Supabase...")
        with open(temp_file, 'rb') as f:
            result = supabase.storage.from_('videos').upload(
                f'video_{video_id}.mp4',
                f,
                file_options={"content-type": "video/mp4"}
            )

        # Get public URL
        public_url = supabase.storage.from_('videos').get_public_url(f'video_{video_id}.mp4')

        # Update database
        supabase.table('videos').update({
            'video_url': public_url
        }).eq('id', video_id).execute()

        # Clean up
        os.remove(temp_file)

        print(f"✅ Video {video_id} migrado exitosamente")
        print(f"   Nueva URL: {public_url}")
        return True

    except Exception as e:
        print(f"❌ Error migrando video {video_id}: {e}")
        return False

async def migrate_all_openai_videos():
    """
    Encuentra y migra todos los videos de OpenAI API
    """
    # Get videos with OpenAI URLs
    result = supabase.table('videos').select('id, video_url').execute()

    openai_videos = [
        v for v in result.data
        if 'api.openai.com' in v['video_url']
    ]

    print(f"🔍 Encontrados {len(openai_videos)} videos de OpenAI API")

    if not openai_videos:
        print("✅ No hay videos para migrar")
        return

    # Migrate each video
    success = 0
    failed = 0

    for video in openai_videos:
        result = await migrate_video(video['id'], video['video_url'])
        if result:
            success += 1
        else:
            failed += 1

        # Wait between migrations to avoid rate limits
        await asyncio.sleep(2)

    print(f"\n=== RESUMEN ===")
    print(f"✅ Exitosos: {success}")
    print(f"❌ Fallidos: {failed}")
    print(f"📊 Total: {len(openai_videos)}")

if __name__ == "__main__":
    asyncio.run(migrate_all_openai_videos())
```

### Paso 2: Ejecutar el script

```bash
source venv/bin/activate
python3 migrate_videos_to_supabase.py
```

---

## Opción 2: Migración Automática en el Bot

Modificar el código para que SIEMPRE suba videos a Supabase después de generarlos.

### Modificar `agent/tools/sora2.py`

```python
# agent/tools/sora2.py

async def generate(self, prompt: str, duration: int, category: str) -> Dict:
    """Generate video with Sora 2 and upload to Supabase"""

    try:
        # 1. Generate video with Sora 2
        logger.info(f"🎬 Generating video with Sora 2...")
        response = await self.client.video.generate(
            model=settings.sora2_model,
            prompt=prompt,
            duration=duration,
            resolution="1080x1920"
        )

        video_id = response.id
        openai_url = f"https://api.openai.com/v1/videos/{video_id}/content"

        # 2. Download video from OpenAI
        logger.info(f"📥 Downloading video from OpenAI...")
        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {settings.openai_api_key}'}
            async with session.get(openai_url, headers=headers) as resp:
                video_data = await resp.read()

        # 3. Upload to Supabase Storage
        logger.info(f"📤 Uploading to Supabase Storage...")

        import uuid
        filename = f"video_{uuid.uuid4().hex[:12]}.mp4"

        # Save temp file
        temp_path = f"/tmp/{filename}"
        with open(temp_path, 'wb') as f:
            f.write(video_data)

        # Upload to Supabase
        from supabase import create_client
        supabase = create_client(settings.supabase_url, settings.supabase_service_key)

        with open(temp_path, 'rb') as f:
            supabase.storage.from_('videos').upload(
                filename,
                f,
                file_options={"content-type": "video/mp4"}
            )

        # Get public URL
        public_url = supabase.storage.from_('videos').get_public_url(filename)

        # Clean up
        os.remove(temp_path)

        logger.info(f"✅ Video uploaded to Supabase: {public_url}")

        return {
            "success": True,
            "video_id": video_id,
            "video_url": public_url,  # ← Ahora usa URL de Supabase
            "duration": duration,
            "openai_video_id": video_id  # Guardamos el ID original
        }

    except Exception as e:
        logger.error(f"Error generating/uploading video: {e}")
        return {"success": False, "error": str(e)}
```

---

## Opción 3: Proxy de Videos (Sin migración)

Crear un endpoint en tu API que haga de proxy para videos de OpenAI.

### Añadir a `app.py`

```python
# app.py

@app.get("/proxy/video/{video_id}")
async def proxy_video(video_id: str):
    """
    Proxy endpoint para videos de OpenAI
    Permite acceder a videos sin exponer API key
    """
    try:
        # Get video info from DB
        result = db.client.table("videos").select("video_url").eq("id", video_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Video not found")

        openai_url = result.data[0]["video_url"]

        # If already Supabase URL, redirect
        if 'supabase.co' in openai_url:
            return RedirectResponse(url=openai_url)

        # Download from OpenAI with authentication
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)

        async with aiohttp.ClientSession() as session:
            headers = {'Authorization': f'Bearer {settings.openai_api_key}'}
            async with session.get(openai_url, headers=headers) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="OpenAI error")

                video_data = await response.read()

                # Return video with proper headers
                return Response(
                    content=video_data,
                    media_type="video/mp4",
                    headers={
                        "Content-Disposition": f"inline; filename=video_{video_id}.mp4",
                        "Cache-Control": "public, max-age=31536000"
                    }
                )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Modificar el endpoint `/api/videos`

```python
# En get_videos endpoint

for video in result.data:
    # Si es URL de OpenAI, usar proxy
    if 'api.openai.com' in video['video_url']:
        video['video_url'] = f"http://localhost:8000/proxy/video/{video['id']}"
```

---

## Comparación de Opciones

| Opción | Pros | Contras | Costo |
|--------|------|---------|-------|
| **1. Migración Manual** | ✅ URLs públicas permanentes<br>✅ No requiere API key después<br>✅ Más rápido para usuarios | ❌ Una vez (no repetible)<br>❌ Usa ancho de banda | Storage |
| **2. Migración Automática** | ✅ Todos los videos futuros públicos<br>✅ No requiere acción manual | ❌ Duplica storage (OpenAI + Supabase)<br>❌ Más lento en generación | API + Storage |
| **3. Proxy** | ✅ No usa storage extra<br>✅ Fácil implementar | ❌ Requiere API key activa siempre<br>❌ Más lento (descarga on-demand)<br>❌ Expone API key en servidor | Solo API |

---

## Recomendación

### Para videos existentes (ya eliminados):
✅ **No hacer nada** - Ya los borraste

### Para videos futuros:
✅ **Opción 2: Migración Automática**

Modificar `sora2.py` para que SIEMPRE:
1. Genere video en OpenAI
2. Descargue el video
3. Suba a Supabase Storage
4. Guarde URL pública en DB
5. (Opcional) Borre de OpenAI si tienen límite de storage

---

## Implementación Rápida (15 min)

Si quieres implementar la migración automática AHORA:

```bash
# 1. Instalar dependencias
pip install aiohttp

# 2. Modificar sora2.py con el código de Opción 2

# 3. Reiniciar servidor
pkill -f uvicorn
uvicorn app:app --reload

# 4. Probar con /create
# Los nuevos videos irán directo a Supabase
```

---

## Nota Importante

**Los videos que eliminamos (IDs 26-44) YA NO existen en la DB.**

Si los quisieras recuperar:
- ❌ No puedes - ya los eliminaste de la DB
- ✅ Pero aún existen en servidores de OpenAI (por ~30 días)
- ✅ Podrías recuperarlos SI tienes los IDs de OpenAI guardados

En `agent_conversations` table puede haber logs con los IDs...

---

## ¿Quieres implementar la migración automática para futuros videos?

**Tiempo:** 15 minutos
**Beneficio:** Todos los videos futuros serán públicos automáticamente
**Costo:** +2-3 segundos por video generado

¿Lo implementamos?
