#!/usr/bin/env python3
"""
Setup Supabase Database Schema
Ejecuta el schema SQL en Supabase automáticamente
"""

import asyncio
from pathlib import Path
from supabase import create_client, Client
from config.settings import settings
from loguru import logger

async def setup_database():
    """Ejecuta el schema SQL en Supabase"""
    try:
        logger.info("🗄️  Conectando a Supabase...")

        # Crear cliente Supabase
        supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key  # Usar service_role key para DDL
        )

        logger.info("✅ Conectado a Supabase")

        # Leer el archivo SQL
        schema_path = Path("db/schema.sql")
        if not schema_path.exists():
            logger.error(f"❌ No se encontró el archivo: {schema_path}")
            return False

        logger.info(f"📄 Leyendo schema desde: {schema_path}")
        schema_sql = schema_path.read_text()

        # Dividir en statements individuales
        statements = [
            stmt.strip()
            for stmt in schema_sql.split(";")
            if stmt.strip() and not stmt.strip().startswith("--")
        ]

        logger.info(f"📝 Ejecutando {len(statements)} statements SQL...")

        # Ejecutar cada statement
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue

            try:
                # Supabase client no soporta ejecutar SQL directo
                # Necesitamos usar el REST API directamente
                logger.warning(
                    f"⚠️  Statement {i}/{len(statements)}: "
                    "Supabase Python client no soporta SQL DDL directo"
                )
                logger.info(
                    "💡 Por favor ejecuta el schema manualmente en Supabase Dashboard"
                )
                break

            except Exception as e:
                logger.error(f"❌ Error en statement {i}: {e}")
                continue

        logger.info("\n" + "="*60)
        logger.info("📋 INSTRUCCIONES MANUALES:")
        logger.info("="*60)
        logger.info("1. Ve a: https://supabase.com/dashboard")
        logger.info(f"2. Abre tu proyecto: {settings.supabase_url}")
        logger.info("3. Ve a 'SQL Editor' en el menú lateral")
        logger.info("4. Copia el contenido de: db/schema.sql")
        logger.info("5. Pega en el editor y ejecuta (RUN)")
        logger.info("="*60 + "\n")

        # Alternativa: mostrar las instrucciones de curl
        logger.info("💡 ALTERNATIVA - Usar API REST directo:")
        logger.info("="*60)
        logger.info("Ejecuta este comando en tu terminal:")
        logger.info("")
        logger.info(f'curl -X POST "{settings.supabase_url}/rest/v1/rpc/exec_sql" \\')
        logger.info(f'  -H "apikey: {settings.supabase_service_key[:20]}..." \\')
        logger.info(f'  -H "Authorization: Bearer {settings.supabase_service_key[:20]}..." \\')
        logger.info('  -H "Content-Type: application/json" \\')
        logger.info(f'  -d \'{{"sql": "$(cat db/schema.sql)"}}\'')
        logger.info("="*60 + "\n")

        return True

    except Exception as e:
        logger.error(f"❌ Error al setup de base de datos: {e}")
        return False

async def verify_database():
    """Verifica que las tablas existan"""
    try:
        logger.info("🔍 Verificando estructura de base de datos...")

        supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )

        # Intentar hacer un query simple a cada tabla
        tables = [
            "creators",
            "videos",
            "posts",
            "metrics",
            "leaderboard",
            "notifications",
            "violations",
            "votes",
            "prizes",
            "agent_conversations"
        ]

        results = {}
        for table in tables:
            try:
                response = supabase.table(table).select("id").limit(1).execute()
                results[table] = "✅"
            except Exception as e:
                results[table] = f"❌ {str(e)[:50]}"

        logger.info("\n" + "="*60)
        logger.info("📊 ESTADO DE TABLAS:")
        logger.info("="*60)
        for table, status in results.items():
            logger.info(f"{table:20} {status}")
        logger.info("="*60 + "\n")

        # Verificar si todas las tablas existen
        all_exist = all("✅" in status for status in results.values())

        if all_exist:
            logger.success("✅ Todas las tablas existen correctamente")
            return True
        else:
            logger.warning("⚠️  Algunas tablas no existen. Ejecuta el schema SQL primero.")
            return False

    except Exception as e:
        logger.error(f"❌ Error al verificar base de datos: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 UniCreate Bot - Database Setup")
    logger.info("="*60 + "\n")

    # Primero verificar si las tablas ya existen
    logger.info("Paso 1: Verificando tablas existentes...")
    exists = asyncio.run(verify_database())

    if exists:
        logger.success("✅ Base de datos ya está configurada!")
    else:
        logger.info("\nPaso 2: Configurando base de datos...")
        asyncio.run(setup_database())

        logger.info("\nPaso 3: Verificando nuevamente...")
        exists = asyncio.run(verify_database())

        if not exists:
            logger.warning("\n⚠️  Ejecuta el schema manualmente siguiendo las instrucciones arriba")
