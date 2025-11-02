# 📹 Guía para Recuperar Videos desde Telegram

## 🎯 Objetivo
Recuperar los 6 videos con URLs de OpenAI que ya expiraron, descargándolos directamente desde el historial de Telegram.

---

## 📋 Paso 1: Obtener API ID y API Hash

### 1. Ve a https://my.telegram.org/apps

### 2. Inicia sesión con tu número de teléfono
   - Usa el número asociado a tu cuenta de Telegram
   - Recibirás un código de verificación en Telegram

### 3. Crea una nueva aplicación
   - **App title:** `Video Recovery Bot`
   - **Short name:** `videorecovery`
   - **Platform:** Selecciona cualquiera (Desktop, Android, etc.)

### 4. Copia tus credenciales
   Verás algo como:
   ```
   App api_id: 12345678
   App api_hash: 1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
   ```

---

## 📋 Paso 2: Configurar Variables de Entorno

Agrega estas líneas a tu archivo `.env`:

```bash
# Telegram User API (para recuperar videos)
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
TELEGRAM_PHONE=+521234567890  # Tu número con código de país
```

**IMPORTANTE:** Reemplaza con tus datos reales:
- `TELEGRAM_API_ID`: El número que copiaste
- `TELEGRAM_API_HASH`: El hash que copiaste
- `TELEGRAM_PHONE`: Tu número de teléfono con código de país (ej: +52 para México)

---

## 📋 Paso 3: Ejecutar el Script de Recuperación

```bash
./venv/bin/python recover_with_telethon.py
```

### ¿Qué pasará?

1. **Primera vez:**
   - Te pedirá un código de verificación
   - Ese código llegará a tu Telegram
   - Ingrésalo cuando lo pida
   - Se guardará una sesión (archivo `telegram_recovery_session.session`)

2. **Siguientes veces:**
   - Ya no pedirá código
   - Usará la sesión guardada

3. **Proceso:**
   ```
   🔐 Iniciando sesión en Telegram...
   ✅ Autenticado en Telegram
   🤖 Bot ID: 8305969739
   📹 Videos a recuperar: 6

   👤 Usuario 1026323121 - 5 videos
      🔍 Buscando mensajes desde 2025-10-09 21:00
      ✅ Encontrado video ID 13
         ⬇️  Descargando...
         ✅ Descargado: 2.45 MB
         ✅ RECUPERADO: https://oqdwjrhcdlflfebujnkq.supabase.co/storage/...

   👤 Usuario 170416910 - 1 video
      🔍 Buscando mensajes desde 2025-10-09 21:30
      ✅ Encontrado video ID 19
         ⬇️  Descargando...
         ✅ Descargado: 3.12 MB
         ✅ RECUPERADO: https://oqdwjrhcdlflfebujnkq.supabase.co/storage/...

   ======================================================================
   📊 RESUMEN FINAL:
      ✅ Videos recuperados: 6
      ❌ Videos fallidos: 0
      📹 Total procesados: 6
   ======================================================================
   ```

---

## ⚠️ Notas Importantes

### 1. **Privacidad**
   - El script usa TU cuenta de Telegram (no el bot)
   - Solo puede ver chats donde TÚ tengas acceso
   - Si creaste el bot, necesitas acceso a los chats de los usuarios

### 2. **Alternativa si no tienes acceso a los chats**
   Si no puedes acceder a los chats privados entre el bot y los usuarios:

   **Opción A:** Pedirle a los usuarios que te reenvíen los videos
   ```
   Hey @anthonysurfermx, ¿me puedes reenviar los videos que generaste?
   Los necesito para actualizar el sistema de almacenamiento.
   ```

   **Opción B:** Si eres admin del bot en Telegram, puedes ver el historial
   - Debes tener permisos de admin
   - El script buscará en el historial del bot

### 3. **Usuarios afectados**
   Según la base de datos:
   - **@anthonysurfermx** (user_id: 1026323121) - 5 videos
   - **@Jardian** (user_id: 170416910) - 1 video

---

## 🚀 Después de Recuperar

Una vez recuperados:
1. ✅ Los videos estarán en Supabase Storage
2. ✅ Las URLs en la base de datos se actualizarán automáticamente
3. ✅ Aparecerán en el frontend (http://localhost:8080)
4. ✅ Se podrán reproducir sin problemas

---

## ❓ Troubleshooting

### Error: "Cannot find any entity corresponding to..."
- Significa que tu cuenta no tiene acceso a ese chat
- Solución: Pide a los usuarios que te reenvíen los videos

### Error: "Phone number invalid"
- Verifica que el número tenga código de país (+52, +1, etc.)
- Formato: `TELEGRAM_PHONE=+521234567890`

### Error: "API ID invalid"
- Revisa que copiaste correctamente el API ID y Hash
- Deben ser de https://my.telegram.org/apps

---

## 📊 Estado Actual

### Videos en base de datos:
- ✅ **12 videos** con URLs públicas (funcionando)
- ❌ **6 videos** con URLs de OpenAI (expiradas)

### Después de recuperar:
- ✅ **18 videos** con URLs públicas (todos funcionando)

---

## 🎉 ¡Listo!

Cuando ejecutes el script y recuperes los 6 videos, tendrás tu galería completa funcionando en el frontend.
