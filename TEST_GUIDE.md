# 🧪 Guía de Testing Local

## Flujo Completo de Testing

### 1️⃣ **Setup Inicial** (Una sola vez)

```bash
# ✅ Ya completado:
- Python venv creado
- Dependencias instaladas
- .env configurado
- ngrok instalado y autenticado

# ⏳ Pendiente:
- Base de datos en Supabase (ejecutar schema.sql)
```

---

### 2️⃣ **Iniciar el Bot Localmente**

**Terminal 1: Bot**
```bash
cd /Users/mrrobot/Documents/GitHub/Unicreate/uniswap_sora_bot_v2
./start.sh
```

Deberías ver:
```
2025-10-09 14:45:00 | INFO | Iniciando Uniswap Sora Bot...
2025-10-09 14:45:01 | INFO | ✅ Conectado a Supabase
2025-10-09 14:45:01 | INFO | ✅ OpenAI client inicializado
2025-10-09 14:45:02 | INFO | 🤖 Bot iniciado correctamente
2025-10-09 14:45:02 | INFO | Uvicorn running on http://0.0.0.0:8000
```

---

### 3️⃣ **Exponer con ngrok**

**Terminal 2: ngrok**
```bash
ngrok http 8000
```

Verás algo como:
```
Forwarding: https://abc123.ngrok.io -> http://localhost:8000
```

**Copia la URL HTTPS** (ejemplo: `https://abc123.ngrok.io`)

---

### 4️⃣ **Actualizar Webhook URL**

Edita [.env](.env):
```env
TELEGRAM_WEBHOOK_URL=https://abc123.ngrok.io/webhook
```

**Reinicia el bot** (Ctrl+C en Terminal 1, luego `./start.sh`)

---

### 5️⃣ **Probar el Bot en Telegram**

1. **Busca tu bot en Telegram**
   - Abre Telegram
   - Busca: `@tu_bot_username` (el que configuraste con BotFather)

2. **Envía comandos:**

   ```
   /start
   → Debería responder con mensaje de bienvenida

   /create
   → Debería pedirte que elijas una categoría

   /help
   → Muestra lista de comandos

   /stats
   → Muestra tus estadísticas (0 videos al inicio)
   ```

---

### 6️⃣ **Crear un Video de Prueba**

**Flujo completo:**

1. **Envía:** `/create`
2. **Bot responde:** Botones de categorías
3. **Click:** "🎨 Product Features"
4. **Bot pregunta:** "Describe el video que quieres"
5. **Envía:** "A futuristic city with Uniswap trading screens"
6. **Bot pregunta:** "¿Duración? (10-60s)"
7. **Envía:** "15"
8. **Bot confirma:** Generando video...
9. **Espera:** 2-3 minutos (Sora tarda)
10. **Bot envía:** Video generado + caption + hashtags

---

### 7️⃣ **Monitorear Requests**

Abre en tu navegador:
```
http://localhost:4040
```

Verás todos los webhooks de Telegram en tiempo real:
- Request headers
- Body (JSON con el mensaje del usuario)
- Response del bot
- Timing

**Súper útil para debugging!**

---

## 🧪 Comandos para Probar

### Básicos
```
/start       → Registro inicial
/help        → Lista de comandos
/stats       → Ver tus estadísticas
/leaderboard → Ver top 10 creadores
```

### Creación de Videos
```
/create      → Iniciar creación de video
/mycontent   → Ver tus videos creados
```

### Registro de Posts
```
/posted https://tiktok.com/@user/video/123
→ Registrar video publicado en TikTok
```

### Admin (si eres admin)
```
/campaigns   → Ver estadísticas de campaña
```

---

## 🐛 Debugging

### Ver logs del bot
```bash
# Terminal 1 (donde corre el bot)
# Los logs aparecen en tiempo real
```

### Ver requests de Telegram
```
http://localhost:4040
```

### Verificar base de datos
```bash
./venv/bin/python setup_db.py
```

### Reiniciar todo
```bash
# Terminal 1: Ctrl+C → ./start.sh
# Terminal 2: Ctrl+C → ngrok http 8000
# Actualizar .env con nueva URL de ngrok
```

---

## ⚠️ Troubleshooting

### "Bot no responde"
1. ✅ Verificar que el bot esté corriendo (Terminal 1)
2. ✅ Verificar que ngrok esté activo (Terminal 2)
3. ✅ Verificar que TELEGRAM_WEBHOOK_URL en .env tenga la URL correcta de ngrok
4. ✅ Reiniciar el bot después de cambiar .env

### "Database error"
```bash
./venv/bin/python setup_db.py
# Verificar que todas las tablas muestren ✅
```

### "OpenAI API error"
- Verificar que OPENAI_API_KEY en .env sea correcto
- Verificar que tengas crédito en OpenAI
- Verificar que tengas acceso a Sora 2

### "Webhook not set"
El bot automáticamente configura el webhook al iniciar.
Si hay error, verás en los logs del bot.

---

## 📊 Flujo de Datos

```
Usuario en Telegram
    ↓
Envía mensaje: "/create"
    ↓
Telegram API → POST https://abc123.ngrok.io/webhook
    ↓
ngrok → localhost:8000/webhook
    ↓
FastAPI app.py recibe webhook
    ↓
python-telegram-bot procesa mensaje
    ↓
Llama a AgentKit (OpenAI Assistants API)
    ↓
Agent usa tools (sora2.py, moderation.py, etc)
    ↓
Genera video con Sora 2
    ↓
Guarda en Supabase
    ↓
Bot envía video al usuario
    ↓
Usuario ve el video en Telegram ✨
```

---

## 🎯 Testing Checklist

- [ ] Bot inicia sin errores
- [ ] ngrok expone el puerto
- [ ] Webhook URL actualizado en .env
- [ ] `/start` funciona
- [ ] `/help` funciona
- [ ] `/create` muestra categorías
- [ ] Puedo describir un video
- [ ] Bot genera video con Sora
- [ ] Video llega a Telegram
- [ ] `/posted` registra posts
- [ ] Dashboard ngrok muestra requests
- [ ] Base de datos guarda registros

---

## 🚀 Próximo Paso: Deploy a Producción

Una vez que todo funcione localmente:

1. **Railway** → Deploy automático desde GitHub
2. **URL permanente** → Ya no necesitas ngrok
3. **24/7 uptime** → Bot siempre disponible
4. **Logs centralizados** → Ver errores remotamente

---

**¿Listo para probar?** ✨
