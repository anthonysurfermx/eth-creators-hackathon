"""
Script para arreglar el content-type de los videos en Supabase Storage
Los videos deben tener content-type 'video/mp4' para reproducirse en el navegador
"""
from supabase import create_client
from config.settings import settings
from loguru import logger

def fix_content_types():
    """
    Actualiza el content-type de los videos en Supabase Storage
    """

    supabase = create_client(settings.supabase_url, settings.supabase_key)

    # Archivos que necesitan actualizarse
    files_to_fix = [
        "application.octet-stream.mp4",
        "application.octet-stream (2).mp4",
        "application.octet-stream (3).mp4",
        "application.octet-stream (4).mp4",
        "application.octet-stream (5).mp4",
    ]

    print("\n" + "="*80)
    print("🔧 ARREGLANDO CONTENT-TYPE DE VIDEOS")
    print("="*80)
    print("\nProblema: Los videos tienen content-type 'application/octet-stream'")
    print("Solución: Cambiar a 'video/mp4' para que se reproduzcan en el navegador")
    print("\n⚠️  NOTA: Supabase Storage no permite cambiar el content-type después de subir")
    print("          Necesitas volver a subir los archivos con el content-type correcto")
    print("\n" + "="*80)

    print("\n📋 INSTRUCCIONES:")
    print("\n1. Ve a Supabase Dashboard → Storage → videos")
    print("\n2. BORRA los 5 archivos actuales:")
    for f in files_to_fix:
        print(f"   • {f}")

    print("\n3. Vuelve a subir los mismos archivos desde Telegram")
    print("   PERO esta vez:")
    print("   - Renómbralos ANTES de subir a nombres sin espacios:")
    print("     • video_13.mp4")
    print("     • video_14.mp4")
    print("     • video_16.mp4")
    print("     • video_17.mp4")
    print("     • video_18.mp4")

    print("\n4. O alternativamente, usa este script:")
    print("   ./venv/bin/python download_and_reupload.py")
    print("   (Descargará desde Telegram y subirá correctamente)")

    print("\n" + "="*80)

    # Alternativa: Intentar mover/copiar con nuevo content-type
    print("\n🔄 Intentando solución alternativa...")
    print("   (Copiar archivos con nuevo content-type)")

    fixed = 0
    failed = 0

    for filename in files_to_fix:
        try:
            logger.info(f"\n📹 Procesando: {filename}")

            # Intentar descargar el archivo
            logger.info(f"   ⬇️  Descargando...")
            data = supabase.storage.from_('videos').download(filename)

            if data:
                logger.info(f"   ✅ Descargado: {len(data) / 1024 / 1024:.2f} MB")

                # Borrar el archivo original
                logger.info(f"   🗑️  Borrando original...")
                supabase.storage.from_('videos').remove([filename])

                # Subir de nuevo con content-type correcto
                logger.info(f"   ⬆️  Re-subiendo con content-type correcto...")
                supabase.storage.from_('videos').upload(
                    filename,
                    data,
                    file_options={"content-type": "video/mp4", "upsert": "true"}
                )

                logger.info(f"   ✅ ARREGLADO: {filename}")
                fixed += 1
            else:
                logger.error(f"   ❌ No se pudo descargar")
                failed += 1

        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            failed += 1

    print(f"\n{'='*80}")
    print(f"📊 RESUMEN:")
    print(f"   ✅ Arreglados: {fixed}")
    print(f"   ❌ Fallidos: {failed}")
    print(f"{'='*80}")

    if fixed > 0:
        print(f"\n🎉 ¡Videos arreglados! Recarga: http://localhost:8080")
        print(f"   Ahora deberían reproducirse correctamente")

if __name__ == "__main__":
    fix_content_types()
