# 🎬 User Flow Completo - Uniswap Creator Bot v2

**Fecha:** Octubre 15, 2025
**Sistema:** Bot de Telegram + Website + Leaderboard
**Objetivo:** Usuarios crean videos AI sobre Uniswap/DeFi, los publican en redes, y compiten en un leaderboard

---

## 🌊 FLUJO PRINCIPAL: De Idea a Leaderboard

### 📱 PASO 1: Usuario Descubre el Bot

**Punto de entrada:**
- Usuario encuentra el bot en Telegram: `@UniswapSoraBot` (o el nombre que tenga)
- O visita el website: `https://www.unicreators.app`
- O es invitado por otro creador

**Primera interacción:**
```
Usuario: /start
```

**Bot responde:**
```
🦄 Welcome to Uniswap Creator Challenge!

Create AI videos about DeFi & Uniswap using Sora 2!

Quick Start:
1. Type /create [your idea] to generate a video
2. Post it on TikTok/X/Instagram
3. Submit with /posted [url] to enter the leaderboard

Commands:
• /create - Generate video with Sora 2
• /categories - See approved themes
• /examples - Get prompt inspiration
• /leaderboard - View rankings
• /stats - Your performance
• /rules - Content guidelines

Get on the Leaderboard:
🎯 People can bet on you as a creator!
📈 Higher views = More betting pool rewards
🏆 Compete for the top spot

🌐 See all videos: www.unicreators.app

Let's create something amazing! 🚀
```

**Backend:**
- Crea registro del usuario en tabla `creators`
- Guarda: `tg_user_id`, `username`, `display_name`
- Inicializa stats en 0

---

### 🎨 PASO 2: Usuario Explora Ideas

**Usuario quiere inspiración:**

```
Usuario: /categories
```

**Bot muestra:**
```
📋 Approved Content Categories

1️⃣ Product Features
Gasless swaps, UniswapX, limit orders, smart wallets

2️⃣ DeFi Education
Stablecoins, how swaps work, DEX basics

3️⃣ Unichain Tech
MEV protection, fair ordering, efficient markets

4️⃣ Multi-chain
Cross-chain swaps, Layer 2s, Soneium

5️⃣ User Success
First swap stories, financial inclusion

6️⃣ Cultural Fusion
Mexican culture + DeFi themes

Need examples? Try /examples [category]
```

**Usuario pide ejemplos:**
```
Usuario: /examples cultural_fusion
```

**Bot muestra:**
```
💡 Example Prompts: Cultural Fusion

1. A Mexican mercado transforms into a DeFi trading hub with neon lights and floating price charts

2. Ancient Aztec pyramids reimagined as Uniswap liquidity pools with flowing digital assets

3. Mariachi band playing in a futuristic crypto exchange

4. Day of the Dead celebration where altars display blockchain transactions instead of photos

Try creating your own variation! 🎨
```

---

### 🎬 PASO 3: Usuario Genera un Video

**Usuario tiene su idea:**
```
Usuario: /create A futuristic Mexican mercado becomes a DeFi hub with neon lights, floating price charts, and people trading tokens
```

**Backend procesa (simple_flow.py):**

**3.1 - Verificación de límites (1-2 segundos):**
- ✅ Chequea límite diario (20 videos/día) → OK
- ✅ Chequea duplicados (mismo prompt en 24h) → OK
- ✅ Puede continuar

**Bot muestra:**
```
🎬 Generating your AI video...

⏳ Estimated time: 2-5 minutes
🤖 Technology: OpenAI Sora 2 (AI video generation)
💰 Cost: ~$4 USD per 12-second video

📝 Validating your prompt...
Make sure your idea is clear and creative.

💡 Tip: Each video is expensive, make it count!
```

**3.2 - Validación de contenido (5-10 segundos):**
- GPT-4 analiza el prompt
- Verifica que sea sobre Uniswap/DeFi
- Asigna categoría: `cultural_fusion`

**Criterios de aprobación:**
- ✅ Menciona DeFi/Uniswap/crypto
- ✅ No tiene price predictions
- ✅ No menciona competidores
- ✅ No es contenido de apuestas
- ✅ Tono positivo/educativo

**Si es rechazado:**
```
❌ Your prompt was not approved

Reason: No Uniswap/DeFi connection found

📋 Approval criteria:
✅ DeFi and Web3 education
✅ Uniswap features (swaps, pools)
✅ Mexican culture + crypto
✅ Adoption stories

❌ Not allowed:
• Price predictions
• Competitor mentions
• Gambling content
• "Get rich quick" promises

💡 Examples of approved prompts:
1. Uniswap interface as a futuristic trading terminal
2. Cross-chain swap visualized as a bridge between worlds

🎨 Use /examples for more inspiration
```

**3.3 - Generación con Sora 2 (2-5 minutos):**
- Llama a OpenAI Sora 2 API
- Genera video de 12-15 segundos
- Recibe URL temporal de OpenAI

**3.4 - Upload a storage público (10-30 segundos):**
- Descarga video de OpenAI
- Sube a Supabase Storage
- Genera URL pública
- Crea thumbnail (opcional)

**3.5 - Generación de caption (3-5 segundos):**
- GPT-4 crea caption atractivo
- Genera hashtags relevantes

**3.6 - Guardado en base de datos:**
```sql
INSERT INTO videos (
  tg_user_id,
  video_url,        -- URL pública de Supabase
  thumbnail_url,
  prompt,
  enhanced_prompt,
  duration_seconds,
  category,
  sora_job_id,
  status
) VALUES (...)
```

**Bot envía el video:**
```
[VIDEO SE MUESTRA EN TELEGRAM]

Caption:
🎨 Un vibrante mercado mexicano se transforma en un hub DeFi
futurista con gráficos flotantes y trading de tokens.

#Uniswap #UniswapMexico #DeFi #Web3 #CryptoMexico #AI

---

✅ Video ready!

📤 Next steps:
1. Download the video above
2. Post it on TikTok/X/Instagram
3. Use /posted [url] to start tracking

💡 Tip: Post during peak hours (6-8 PM) for maximum reach!

🌐 See all videos: www.unicreators.app
```

---

### 📱 PASO 4: Usuario Publica en Redes Sociales

**Usuario descarga el video y lo sube a TikTok:**

1. Descarga video de Telegram
2. Abre TikTok
3. Sube el video
4. Copia caption + hashtags del bot
5. Publica
6. Copia URL del post: `https://tiktok.com/@user/video/123456`

---

### 📊 PASO 5: Usuario Registra el Post

**Usuario regresa al bot:**
```
Usuario: /posted https://tiktok.com/@user/video/123456
```

**Backend procesa:**

**5.1 - Validación de URL:**
- ✅ Detecta plataforma: TikTok
- ✅ Extrae post_id: `123456`
- ✅ Verifica que URL no esté ya registrada

**5.2 - Asociación con video:**
- Busca videos del usuario sin ese URL
- Si tiene varios, pregunta cuál es
- Si solo tiene uno, lo asocia automáticamente

**Bot muestra:**
```
📊 Fetching metrics from TIKTOK...

This may take a few seconds...
```

**5.3 - Scraping de métricas (10-20 segundos):**
```python
# utils/social_scrapers_v2.py
metrics = scrape_social_metrics(url, "tiktok")
# Devuelve:
{
  "views": 150,
  "likes": 12,
  "comments": 3,
  "shares": 2
}
```

**5.4 - Guardado en base de datos:**
```sql
INSERT INTO posts (
  video_id,
  tg_user_id,
  platform,
  post_url,
  post_id,
  views,
  likes,
  comments_count,
  shares,
  platform_post_id
) VALUES (...)
```

**5.5 - Recálculo de estadísticas:**
```sql
-- Recalcula stats del creador
UPDATE creators SET
  total_videos = (SELECT COUNT(*) FROM videos WHERE tg_user_id = ...),
  total_views = (SELECT SUM(views) FROM posts WHERE tg_user_id = ...),
  total_engagements = (SELECT SUM(likes + comments + shares) FROM posts WHERE tg_user_id = ...)
WHERE tg_user_id = ...
```

**Bot responde:**
```
✅ Post registered & metrics fetched!

📱 Platform: TIKTOK
🎬 Video: Cultural Fusion

📊 Current metrics:
👀 Views: 150
❤️ Likes: 12
💬 Comments: 3
🔄 Shares: 2

🔄 Auto-tracking:
• Metrics will update every 6 hours
• You'll get notified when you climb the leaderboard

Check your rank: /leaderboard
See your stats: /stats
```

---

### 📈 PASO 6: Métricas se Actualizan Automáticamente

**Sistema background (APScheduler):**

**Cada 6 horas:**
```python
# scheduler/metrics_updater.py
async def update_all_metrics():
    # 1. Busca todos los posts activos
    posts = get_all_posts()

    # 2. Para cada post:
    for post in posts:
        metrics = scrape_social_metrics(post.url, post.platform)

        # 3. Actualiza métricas
        update_post_metrics(post.id, metrics)

    # 4. Recalcula stats de todos los creadores
    recalculate_all_creator_stats()
```

**Si hay cambio significativo (+100 views, subió de ranking):**
```
[NOTIFICACIÓN DE TELEGRAM]

🎉 Great news!

Your video just hit 250 views! 🚀

You moved up to #5 on the leaderboard!

Current stats:
👀 Total views: 250
❤️ Total likes: 25
📊 Engagement rate: 10%

Keep sharing! 💪
```

---

### 🏆 PASO 7: Usuario Revisa Leaderboard

**Usuario quiere ver su ranking:**
```
Usuario: /leaderboard
```

**Bot muestra:**
```
🏆 Top Creators

🥇 @cryptoking — 5,234 views
🥈 @defi_creator — 3,890 views
🥉 @web3_artist — 2,456 views
4️⃣ @mexicrypto — 1,523 views
5️⃣ @anthonysurfermx — 250 views  ← TÚ
6️⃣ @soramaster — 180 views
7️⃣ @uniswapper — 120 views
8️⃣ @tokentrader — 95 views
9️⃣ @nftcreator — 67 views
🔟 @cryptoenthusiast — 45 views
```

**Usuario revisa sus stats personales:**
```
Usuario: /stats
```

**Bot muestra:**
```
📊 Your Stats

Rank: #5
Total Videos: 1
Total Views: 250
Total Engagements: 27

Rank Change: +3 ↗️

Recent Videos:
• cultural_fusion: A futuristic Mexican mercado...
```

**Usuario ve todos sus videos:**
```
Usuario: /myvideos
```

**Bot muestra:**
```
🎬 Your Videos

1. Video #54
📝 A futuristic Mexican mercado becomes a DeFi hub...
📅 2025-10-15

📱 Posted on:
   🎵 TIKTOK: 250 views, 12 likes

2. Video #48
📝 Uniswap interface as a holographic trading terminal...
📅 2025-10-14
⚠️ Not posted yet

💡 Use /posted [url] to register a social post
```

---

### 💰 PASO 8: Betting Pool (Opcional - Smart Contract)

**Otros usuarios pueden apostar en creadores:**

**En el website (unicreators.app):**

1. Usuario visita el leaderboard
2. Ve los top creadores
3. Click en "Bet on Creator"
4. Conecta wallet (MetaMask)
5. Selecciona cantidad (ej: 10 UNI)
6. Firma transacción en Unichain
7. Apuesta registrada en smart contract

**Al final de la semana (epoch):**
- Smart contract consulta: `/api/leaderboard/winners/{epoch_id}`
- Obtiene top 3 creadores
- Distribuye pool de apuestas:
  - 🥇 1er lugar: 50%
  - 🥈 2do lugar: 30%
  - 🥉 3er lugar: 20%
- Los apostadores reciben rewards proporcionales

---

## 🔄 FLUJOS ALTERNATIVOS

### ❌ Flujo: Video Duplicado

```
Usuario: /create A futuristic Mexican mercado becomes a DeFi hub...
```

**Backend detecta duplicado:**
- Busca en DB: mismo `prompt` + mismo `tg_user_id` + últimas 24h
- Encuentra match → Video ID 54

**Bot responde:**
```
⚠️ Duplicate Video Detected!

You already created this video recently.

Reason: You already created this video recently (Video ID: 54).
Please try a different prompt.

💰 Why we block duplicates:
• Each video costs ~$4 USD to generate
• Duplicate videos waste resources
• Try a different creative angle!

💡 What you can do:
1. Modify your prompt slightly
2. Try a completely different idea
3. Use /myvideos to see your existing videos

📹 Your existing video: ID #54

🌐 See your videos: www.unicreators.app
```

---

### ⚠️ Flujo: Sin Créditos de OpenAI

```
Usuario: /create Beautiful DeFi animation
```

**Backend intenta generar pero OpenAI devuelve error:**
```
Error: insufficient_quota
```

**Bot responde:**
```
🎬💸 Oops! We ran out of AI credits! 💸🎬

🤖 The video robot ran out of fuel...

😅 Generating videos with Sora 2 costs ~$4 USD per video,
and it looks like we spent this month's entire budget! 🫠

📢 But don't worry!
The admins are already reloading the account. 🔋⚡

⏰ Come back in a few hours and you'll be able to create your video.

🌐 Meanwhile, check out existing videos at:
www.unicreators.app

💡 Tip: Follow @UniswapCreators to know when we're back! 🚀
```

---

### 🚫 Flujo: Límite Diario Alcanzado

```
Usuario: /create [intenta crear video #21 del día]
```

**Backend detecta:**
- Usuario ya creó 20 videos hoy
- Límite: `MAX_VIDEOS_PER_DAY=20`

**Bot responde:**
```
⚠️ Daily Limit Reached

You've created 20 videos today!

To prevent spam and ensure quality, we limit videos to 20 per day.

⏰ Come back tomorrow to create more videos.

Meanwhile:
• Share your existing videos
• Check the /leaderboard
• See your /stats

🌐 View all videos: www.unicreators.app
```

---

### 📱 Flujo: Actualización Manual de Métricas

**Si el scraping automático falla:**

```
Usuario: /update 1500 250 30
```

**Backend interpreta:**
- Views: 1500
- Likes: 250
- Comments: 30

**Bot actualiza:**
```
✅ Metrics updated!

📊 New metrics:
👀 Views: 1,500
❤️ Likes: 250
💬 Comments: 30

Updated post: https://tiktok.com/@user/video/123456

Check your rank: /leaderboard
```

---

## 🌐 FLUJO EN EL WEBSITE

### Visitante Llega a unicreators.app

**Homepage muestra:**

1. **Hero Section:**
   ```
   🎬 Create Viral AI Videos About DeFi

   Generate stunning videos with Sora 2 AI
   Share on social media • Compete for rewards

   [Start Creating] [View Gallery]
   ```

2. **Video Gallery:**
   - Grid de videos más recientes
   - Cada card muestra:
     - Video thumbnail
     - Creator username
     - Views, likes
     - Platforms donde se publicó (TikTok, Instagram, X)
   - Click en video → Se reproduce
   - Click en creator → Ver perfil

3. **Leaderboard:**
   ```
   🏆 Top Creators This Week

   1. @cryptoking      5,234 views    [Bet on Creator]
   2. @defi_creator    3,890 views    [Bet on Creator]
   3. @web3_artist     2,456 views    [Bet on Creator]
   ```

4. **Stats Dashboard:**
   ```
   📊 Campaign Stats

   Total Creators: 127
   Total Videos: 453
   Total Views: 125K
   Total Engagement: 15K
   ```

5. **How It Works:**
   ```
   1️⃣ Open Telegram Bot → @UniswapSoraBot
   2️⃣ Create AI Video → /create [your idea]
   3️⃣ Post on Social → Share on TikTok/Instagram/X
   4️⃣ Submit & Track → /posted [url]
   5️⃣ Compete & Win → Climb the leaderboard!
   ```

---

## 🔗 INTEGRACIONES

### Telegram Bot ↔ Backend API
```
Telegram Webhook → FastAPI /webhook
↓
Process Update → Command Handlers
↓
Call simple_flow.py → Generate video
↓
Save to Supabase → Database
↓
Send response → Telegram Bot API
```

### Website ↔ Backend API
```
Frontend (React/Next.js)
↓
Fetch: GET /api/videos?limit=20
↓
Backend filters videos (only public URLs)
↓
Returns JSON with videos + metrics
↓
Frontend renders gallery
```

### Smart Contract ↔ Backend API
```
Smart Contract (Unichain)
↓
Call: getEpochWinners(epoch_id)
↓
Backend: GET /api/leaderboard/winners/{epoch_id}
↓
Returns top 3 creator IDs
↓
Smart Contract distributes rewards
```

### Background Scheduler ↔ Social Media
```
APScheduler (every 6 hours)
↓
Get all posts from DB
↓
For each post:
  - Call social_scrapers_v2.scrape_social_metrics()
  - Update metrics in DB
  - Recalculate creator stats
↓
Send notifications if rankings changed
```

---

## 📊 DATA FLOW

### Tablas en Supabase:

**creators:**
```sql
- tg_user_id (PK)
- username
- display_name
- total_videos
- total_views
- total_engagements
- created_at
```

**videos:**
```sql
- id (PK)
- tg_user_id (FK)
- video_url
- watermarked_url
- thumbnail_url
- prompt
- enhanced_prompt
- category
- caption
- hashtags
- duration_seconds
- sora_job_id
- status (pending, processing, ready, failed)
- created_at
```

**posts:**
```sql
- id (PK)
- video_id (FK)
- tg_user_id (FK)
- platform (tiktok, instagram, twitter, x)
- post_url
- post_id
- platform_post_id
- views
- likes
- comments_count
- shares
- approved
- has_required_hashtags
- created_at
- updated_at
```

---

## 🎯 KPIs y Métricas

**Por Usuario:**
- Total videos creados
- Total views across all platforms
- Total engagements (likes + comments + shares)
- Engagement rate
- Ranking position
- Ranking change (↗️↘️)

**Por Video:**
- Views por platform
- Likes, comments, shares
- Engagement rate
- Tiempo desde publicación
- Performance vs promedio

**Globales:**
- Total creadores activos
- Total videos generados
- Total views agregadas
- Average engagement rate
- Top performing category
- Most active platform

---

## ⚙️ CONFIGURACIÓN

### Variables de Entorno Clave:
```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...
SORA2_MODEL=sora-2
GPT_MODEL=gpt-4-turbo-preview

# Telegram
TELEGRAM_BOT_TOKEN=...
TELEGRAM_WEBHOOK_URL=...

# Database
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_SERVICE_KEY=...

# Storage
STORAGE_TYPE=supabase

# Límites
MAX_VIDEOS_PER_DAY=20
COOLDOWN_HOURS=24
MAX_STRIKES=3

# Scheduler
METRICS_UPDATE_INTERVAL_HOURS=6
```

---

## 🚀 PRÓXIMOS FEATURES

**Fase 2:**
- Watermarking automático de videos
- Generación de thumbnails
- Remix de videos existentes
- Votación comunitaria
- Badges y achievements

**Fase 3:**
- Multi-idioma
- Integración con más redes (YouTube Shorts)
- Analytics dashboard para creadores
- A/B testing de prompts
- AI-powered prompt suggestions

---

**Versión:** 2.0
**Última actualización:** 2025-10-15
**Autor:** Anthony | Uniswap Labs
