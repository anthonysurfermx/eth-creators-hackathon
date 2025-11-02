# 🔑 Credentials Guide - Paso a Paso

Esta guía te ayudará a obtener todas las credenciales necesarias para el bot.

---

## 📋 **Credenciales Necesarias**

### ✅ Obligatorias (sin estas el bot no funciona):
1. OpenAI API Key
2. Telegram Bot Token
3. Supabase URL + Keys

### ⏳ Opcionales (para más tarde):
4. Social Media APIs (Twitter, Instagram, TikTok)
5. Sentry DSN (monitoring)

---|

## 1️⃣ **OpenAI API Key** (3 minutos)

### Paso 1: Crear cuenta OpenAI
- Ve a: https://platform.openai.com/signup
- Regístrate con tu email

### Paso 2: Obtener API Key
1. Ve a: https://platform.openai.com/api-keys
2. Click en **"Create new secret key"**
3. Nombre: `Uniswap Bot`
4. Click **"Create secret key"**
5. **¡IMPORTANTE!** Copia la key (empieza con `sk-proj-...`)
6. Guárdala en un lugar seguro (no la podrás ver de nuevo)

### Paso 3: Agregar créditos
1. Ve a: https://platform.openai.com/settings/organization/billing/overview
2. Click "Add payment method"
3. Agrega tarjeta
4. Recomendado: $20 USD para empezar

### Uso en .env:
```bash
OPENAI_API_KEY=sk-proj-abc123def456ghi789...
```

### 💰 **Costos estimados:**
- GPT-4 Turbo: ~$0.01 por video (caption)
- Validación: ~$0.005 por prompt
- Sora 2: TBD (cuando esté disponible)
- **Estimado por usuario:** ~$0.02 - $0.05 por video completo

---

## 2️⃣ **Telegram Bot Token** (5 minutos)

### Paso 1: Abrir Telegram
- Abre la app de Telegram en tu teléfono o escritorio

### Paso 2: Buscar BotFather
1. Busca: `@BotFather`
2. Es el bot oficial con el check azul ✅
3. Inicia conversación

### Paso 3: Crear bot
1. Envía: `/newbot`
2. BotFather preguntará:

```
BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.

Tú: Uniswap Creator Bot

BotFather: Good. Now let's choose a username for your bot. It must end in `bot`.

Tú: uniswap_creator_mx_bot
(o el nombre que prefieras que termine en 'bot')

BotFather: Done! Congratulations on your new bot. You will find it at t.me/uniswap_creator_mx_bot
```

3. **Copia el token** que te da BotFather:
```
Use this token to access the HTTP API:
1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

### Paso 4: Configurar el bot (Opcional)
```
/setdescription - Descripción del bot
Create AI videos about Uniswap and DeFi using Sora 2

/setabouttext - Texto "About"
Official Uniswap Creator Challenge Bot - Generate AI videos and win prizes!

/setcommands - Comandos
start - Join the campaign
create - Generate video with Sora 2
posted - Register your social post
leaderboard - View top crators
stats - Your stats   
categories - Content themes
examples - Prompt examples
rules - Content guidelines
```

### Uso en .env:
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

---

## 3️⃣ **Supabase Database** (10 minutos)

### Paso 1: Crear cuenta Supabase
- Ve a: https://supabase.com
- Click "Start your project"
- Sign up con GitHub o email

### Paso 2: Crear proyecto
1. Click "New project"
2. Configura:
   - **Name:** `uniswap-creator-bot`
   - **Database Password:** (genera una fuerte o usa password generator)
     - Guarda este password, lo necesitarás
   - **Region:** `South America (São Paulo)` (más cercano a México)
   - **Pricing Plan:** Free (suficiente para empezar)
3. Click "Create new project"
4. Espera 2 minutos mientras se crea...

### Paso 3: Obtener credenciales
1. Una vez creado, ve a **Settings** (⚙️ en el menú izquierdo)
2. Click en **API** en el submenú
3. Verás:

```
Project URL
https://xxxxxxxxxxxxx.supabase.co

Project API keys

anon public
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBh...
[Este es tu SUPABASE_KEY]

service_role secret
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBh...
[Este es tu SUPABASE_SERVICE_KEY - opcional]
```

### Paso 4: Setup Database Schema
1. En Supabase, ve a **SQL Editor** (menú izquierdo)
2. Click "New query"
3. Abre el archivo `db/schema.sql` de tu proyecto
4. Copia TODO el contenido
5. Pega en el editor de Supabase
6. Click **"Run"** (botón verde abajo a la derecha)
7. Deberías ver: ✅ **Success. No rows returned**

### Paso 5: Verificar tablas
1. Ve a **Table Editor** (menú izquierdo)
2. Deberías ver todas las tablas:
   - creators
   - videos
   - posts
   - metrics
   - leaderboard
   - notifications
   - violations
   - votes
   - prizes
   - agent_conversations

### Uso en .env:
```bash
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... # Opcional
```

---

## 4️⃣ **Webhook Secret** (30 segundos)

Genera un token seguro aleatorio:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copia el output, algo como:
```
abc123-XYZ_789_def456_GHI_jkl012_MNO
```

### Uso en .env:
```bash
TELEGRAM_WEBHOOK_SECRET=abc123-XYZ_789_def456_GHI_jkl012_MNO
```

---

## 5️⃣ **Configurar .env** (2 minutos)

Abre el archivo `.env` y reemplaza estos valores:

```bash
# OpenAI API (Del paso 1)
OPENAI_API_KEY=sk-proj-TU_KEY_AQUI

# Telegram Bot (Del paso 2)
TELEGRAM_BOT_TOKEN=TU_TOKEN_AQUI

# Supabase (Del paso 3)
SUPABASE_URL=https://TU_PROJECT.supabase.co
SUPABASE_KEY=TU_ANON_KEY_AQUI

# Webhook Secret (Del paso 4)
TELEGRAM_WEBHOOK_SECRET=TU_SECRET_AQUI

# Webhook URL (dejar vacío por ahora, lo configuraremos con ngrok)
TELEGRAM_WEBHOOK_URL=
```

---

## ✅ **Checklist de Credenciales**

Marca las que ya tienes:

- [ ] OpenAI API Key configurada en .env
- [ ] Créditos agregados a cuenta OpenAI ($20+ recomendado)
- [ ] Telegram Bot Token configurado
- [ ] Supabase proyecto creado
- [ ] Supabase URL en .env
- [ ] Supabase Key en .env
- [ ] Database schema ejecutado (tablas creadas)
- [ ] Webhook secret generado y en .env

---

## 🔐 **Seguridad**

### ⚠️ NUNCA COMPARTAS:
- OpenAI API Key
- Telegram Bot Token
- Supabase service_role key
- Webhook secret

### ✅ Buenas prácticas:
- No commitees `.env` a Git (ya está en `.gitignore`)
- Usa variables de entorno en producción
- Rota keys si se comprometen
- Usa el `anon` key de Supabase para el bot (no el `service_role`)

---

## 🆘 **Troubleshooting**

### OpenAI API no funciona
- Verifica que la key empiece con `sk-proj-` o `sk-`
- Checa que tengas créditos en tu cuenta
- Prueba en: https://platform.openai.com/playground

### Telegram Bot no responde
- Verifica que el token sea correcto
- Busca tu bot en Telegram: `@tu_bot_username`
- Envía `/start` para probar

### Supabase connection error
- Verifica la URL (debe terminar en `.supabase.co`)
- Verifica que usaste la key `anon public`
- Checa que las tablas existan en Table Editor

---

## 📞 **Soporte**

Si tienes problemas:
1. Revisa los logs del bot
2. Ejecuta `python setup.py` para validar
3. Checa este archivo de nuevo

---

## 🎯 **Siguiente Paso**

Una vez que tengas todas las credenciales:

```bash
# Valida que todo esté configurado
python3 setup.py

# Si todo está ✅, arranca el bot
python3 -m uvicorn app:app --reload
```

¡Listo! 🚀
