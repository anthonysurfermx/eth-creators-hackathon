# 🎬 DEMO FLOW - Uni Creator Bot v2
## Flujo Completo Paso a Paso (15 minutos)

---

## ⏱️ TIMELINE

| Tiempo | Sección | Duración |
|--------|---------|----------|
| 0:00 | Introducción + Setup | 2 min |
| 2:00 | Demo Bot Telegram (Flujo Completo) | 5 min |
| 7:00 | Sistema de Moderación | 2 min |
| 9:00 | API y Frontend Integration | 2 min |
| 11:00 | Smart Contracts Unichain | 2 min |
| 13:00 | Métricas y Analytics | 1 min |
| 14:00 | Q&A y Próximos Pasos | 1 min |

---

## 🎯 PREPARACIÓN (Antes de la Demo)

### Checklist Pre-Demo

```bash
# 1. Verificar que el servidor esté corriendo
curl http://localhost:8000/health

# 2. Verificar base de datos
source venv/bin/activate
python3 check_db.py

# 3. Tener abierto en tabs del navegador:
# - http://localhost:8000/docs (Swagger UI)
# - https://vt.tiktok.com/ZSUkwsTbD/ (Video real en TikTok)
# - Terminal con logs: tail -f bot.log

# 4. Tener Telegram abierto en el bot
# - @UniCreatorBot (o tu bot name)

# 5. Tener preparado VS Code con archivos clave:
# - app.py
# - agent/tools/content_validator.py
# - betting-pool-contracts/contracts/LeaderboardBetting.sol
```

---

## 📍 PARTE 1: INTRODUCCIÓN (0:00 - 2:00)

### Slide 1: El Problema
**"Uniswap necesita contenido UGC auténtico a escala para la campaña de México"**

Desafíos:
- ❌ Moderation manual no escala
- ❌ Calidad inconsistente
- ❌ Sin tracking de métricas
- ❌ No hay gamificación

### Slide 2: La Solución
**"Uni Creator Bot v2 - Plataforma completa de UGC con IA"**

Stack:
- 🤖 OpenAI AgentKit + Sora 2
- 📱 Telegram Bot (interfaz familiar)
- 🗄️ Supabase (base de datos + storage)
- ⛓️ Unichain (smart contracts para betting)

### Mostrar en Pantalla:
```
Arquitectura:

Telegram → FastAPI → AgentKit → Tools:
                                  ├─ Content Validator (GPT-4)
                                  ├─ Sora 2 Generator
                                  ├─ Watermark (FFmpeg)
                                  ├─ Caption Generator
                                  ├─ Social Scraping
                                  └─ Database Ops
                                       ↓
                               Supabase + Storage
                                       ↓
                              APScheduler (6h)
                                       ↓
                           Auto-update Metrics
```

---

## 📍 PARTE 2: DEMO BOT TELEGRAM - FLUJO COMPLETO (2:00 - 7:00)

### PASO 1: Onboarding (30 seg)

**Abre Telegram, muestra el chat con el bot**

```
Tú: /start
```

**Bot responde:**
```
¡Bienvenido a Uni Creator Bot! 🦄

Crea videos increíbles sobre Uniswap usando Sora 2 (IA de OpenAI).

🎬 Cómo funciona:
1. Escribe tu idea con /create [tu prompt]
2. El bot genera un video HD (10-60s)
3. Comparte en TikTok/Twitter/Instagram
4. Registra tu post con /posted [url]
5. Sube en el leaderboard y gana premios!

📋 Comandos:
/create - Genera un video
/categories - Ver temas aprobados
/examples - Ver ejemplos de prompts
/posted - Registrar tu post
/leaderboard - Ver rankings
/stats - Tus estadísticas
/rules - Reglas de contenido

¡Empecemos a crear! 🚀
```

**Menciona:** "El bot usa conversación natural, nada de interfaces complejas"

---

### PASO 2: Ver Categorías (30 seg)

```
Tú: /categories
```

**Bot responde:**
```
📂 Categorías Aprobadas

1. 🚀 Product Features
   Gasless swaps, UniswapX, limit orders, smart wallets, bridging

2. 📚 DeFi Education
   Stablecoins, how swaps work, DEX basics, blockchain education

3. 🔗 Unichain Tech
   MEV protection, fair ordering, TEE, efficient markets

4. 🌍 Multi-chain
   Cross-chain swaps, Layer 2s, Soneium integration

5. 💡 User Success
   First swap stories, financial inclusion, accessibility

6. 🎨 Cultural Fusion
   Mexican culture + DeFi (mercados, arte, tradiciones)

Usa /examples [category] para ver prompts de ejemplo.
```

**Menciona:** "Tenemos 6 categorías pre-aprobadas para mantener brand consistency"

---

### PASO 3: Ver Ejemplos (30 seg)

```
Tú: /examples cultural_fusion
```

**Bot responde:**
```
🎨 Ejemplos: Cultural Fusion

1. "Traditional Mexican mercado transforms into holographic DeFi
   marketplace with papel picado as blockchain connections,
   vibrant colors, cinematic lighting, 4K"

2. "Talavera pottery patterns morph into blockchain networks,
   swirling tokens flow through colorful ceramic designs,
   artistic and cultural"

3. "Mariachi band plays as tokens dance in crypto celebration,
   confetti made of transaction receipts, festive and joyful,
   Mexican cultural pride meets Web3"

💡 Tip: Sé específico con:
- Estilo visual (cinematic, artistic, futuristic)
- Colores y mood
- Elementos culturales concretos
- Duración deseada (10-60s)
```

**Menciona:** "El bot da ejemplos para inspirar y mejorar la calidad"

---

### PASO 4: Crear Video - FLUJO COMPLETO (2 min)

**Ahora viene la parte importante - mostrar todo el flujo de generación**

```
Tú: /create Traditional Mexican mercado transforms into a holographic
DeFi marketplace, papel picado becomes blockchain connections,
vibrant magenta and violet colors, cinematic 4K, 15 seconds
```

**Bot responde EN TIEMPO REAL (muestra cada paso):**

```
🔍 Validando contenido...

✅ Contenido Aprobado
Categoría: cultural_fusion
Confianza: 0.92

────────────────────────────

🎬 Generando video con Sora 2...

Prompt optimizado:
"Traditional Mexican mercado transforms into a holographic DeFi
marketplace, papel picado becomes blockchain connections,
vibrant magenta and violet Uniswap colors, cinematic lighting,
4K resolution, 15 seconds, elegant and sophisticated"

⏳ Esto puede tomar 2-3 minutos...
```

**MIENTRAS ESPERA (muestra en pantalla):**

```bash
# Terminal con logs (tail -f bot.log)
2025-10-12 18:30:15 | INFO | Content validation passed: cultural_fusion
2025-10-12 18:30:16 | INFO | Calling Sora 2 API...
2025-10-12 18:30:18 | INFO | Video generation started: video_xyz123
2025-10-12 18:32:45 | INFO | Video ready, downloading...
2025-10-12 18:32:50 | INFO | Adding watermark...
2025-10-12 18:32:55 | INFO | Generating caption with GPT-4...
```

**Bot continúa:**
```
✅ Video generado!

🎨 Añadiendo watermark de Uniswap...
✅ Watermark aplicado

✍️ Generando caption con GPT-4...
✅ Caption listo

────────────────────────────

[VIDEO SE ENVÍA AQUÍ - 15 segundos, HD, con watermark Uniswap]

────────────────────────────

📝 Caption:
"Donde la tradición se encuentra con la innovación 🇲🇽✨

El mercado mexicano evoluciona hacia DeFi, manteniendo su
esencia cultural mientras abraza el futuro descentralizado.

#Uniswap #UniswapMexico #DeFi #Web3 #MexicanCulture
#Blockchain #CulturalFusion

🦄 Hecho con Uni Creator Bot"

────────────────────────────

💡 Próximos pasos:
1. Descarga el video
2. Súbelo a TikTok, Twitter o Instagram
3. Usa el caption y hashtags incluidos
4. Registra tu post: /posted [URL]

¡Tu video está listo para compartir! 🚀
```

**Menciona durante la espera:**
- "Sora 2 está generando el video en tiempo real"
- "AgentKit orquesta múltiples herramientas: validación, generación, watermarking, captions"
- "Todo es automático - el usuario solo dio el prompt"
- "El watermark asegura que todos los videos tengan branding de Uniswap"

---

### PASO 5: Simular Post y Tracking (1 min)

```
Tú: /posted https://vt.tiktok.com/ZSUkwsTbD/
```

**Bot responde:**
```
✅ Post Registrado!

📊 Empezaremos a trackear métricas cada 6 horas:
- Views
- Likes
- Comments
- Shares

Tu video: https://vt.tiktok.com/ZSUkwsTbD/
Plataforma: TikTok

🔔 Te notificaremos cuando:
- Subas o bajes de ranking
- Alcances milestones (100, 500, 1k views)
- Seas elegible para premios

Usa /stats para ver tu progreso.
```

**Menciona:** "El bot scrapea métricas automáticamente sin API keys de TikTok"

---

### PASO 6: Ver Stats Personales (30 seg)

```
Tú: /stats
```

**Bot responde:**
```
📊 Tus Estadísticas

👤 Usuario: anthonysurfermx
🏆 Ranking: #1

📹 Videos: 9
👁️ Views Totales: 322
❤️ Likes Totales: 2
💬 Comments: 0
🔄 Shares: 1

📈 Engagement Rate: 0.93%
⭐ Mejor Video: 322 views
📅 Último Video: hace 2 días

🎯 Progreso hacia Premios:
✅ Early Adopter (5+ videos)
⏳ Rising Star (500+ views) - 55% completado
⏳ Viral Hit (1000+ views) - 32% completado

Sigue creando contenido de calidad! 🚀
```

---

### PASO 7: Ver Leaderboard (30 seg)

```
Tú: /leaderboard
```

**Bot responde:**
```
🏆 LEADERBOARD - Top Creators

1. 🥇 anthonysurfermx
   👁️ 322 views | 📹 9 videos | ❤️ 2 likes

2. 🥈 anawgmi
   👁️ 0 views | 📹 0 videos | ❤️ 0 likes

3. 🥉 Jardian
   👁️ 0 views | 📹 0 videos | ❤️ 0 likes

────────────────────────────

🎁 Premios:
🏆 Top 10 - $500 cada uno
🚀 Most Viral - $1,000
🌟 Early Adopter - $200
💎 Best Cultural Fusion - $500

Última actualización: hace 3 horas
Próxima actualización: en 3 horas

¡Sigue subiendo contenido para mejorar tu ranking!
```

**ABRE EL VIDEO REAL EN NAVEGADOR:**
- https://vt.tiktok.com/ZSUkwsTbD/
- **Menciona:** "Este es un video REAL con métricas REALES - 322 vistas verificables"

---

## 📍 PARTE 3: SISTEMA DE MODERACIÓN (7:00 - 9:00)

### PASO 8: Mostrar Rechazo (1 min)

**Menciona:** "Ahora mostremos el sistema de moderación - dos capas de protección"

```
Tú: /create Uniswap going to the moon! 100x gains guaranteed!
We're getting lambos! 🚀
```

**Bot responde INMEDIATAMENTE:**
```
❌ Contenido Rechazado

Razón: Contains prohibited content: 'to the moon'

El prompt viola nuestras políticas de contenido. No permitimos:
- Predicciones de precio
- Promesas de ganancias
- Contenido de "get rich quick"

💡 Sugerencias:
• Focus on DeFi education or Uniswap features
• Avoid price predictions and gambling themes
• Highlight user stories or cultural elements

Intenta con prompts sobre características del producto,
educación DeFi, o historias de usuarios reales.

Usa /examples para ver prompts aprobados.
```

**Menciona:**
- "Rechazo instantáneo por keyword filtering"
- "40+ palabras/frases prohibidas"
- "Protege la marca de asociaciones negativas"

---

### PASO 9: Mostrar AI Validation (1 min)

```
Tú: /create Video showing how Uniswap will make everyone
millionaires with guaranteed passive income
```

**Bot responde (después de 2-3 segundos):**
```
❌ Contenido Rechazado (AI Validation)

Razón: Unrealistic financial promises detected

La validación AI (GPT-4) detectó:
- Promesas implícitas de riqueza sin disclaimers
- "Get rich quick" scheme indicators
- Misleading information about Uniswap capabilities

Confidence: 0.94

💡 Sugerencias:
• Focus on realistic educational content
• Show actual Uniswap features and use cases
• Include balanced risk/benefit information
• Promote financial literacy, not get-rich schemes

Ejemplo mejorado:
"Educational animation showing how liquidity pools work on
Uniswap, explaining both APY opportunities and impermanent
loss risks, balanced and informative"
```

**Menciona:**
- "La AI detecta intenciones ocultas que keywords no capturan"
- "Análisis semántico profundo con GPT-4"
- "Da sugerencias constructivas, no solo rechaza"

**Muestra código (VS Code):**
```python
# agent/tools/content_validator.py (líneas 40-53)
BANNED_KEYWORDS = [
    "moon", "100x", "1000x", "to the moon", "lambo",
    "casino", "roulette", "betting", "gamble",
    "get rich", "easy money", "guaranteed profit",
    "pancakeswap", "sushiswap", "1inch",
    "pump", "dump", "rug pull", "scam token"
]
```

---

## 📍 PARTE 4: API Y FRONTEND (9:00 - 11:00)

### PASO 10: Swagger UI (1 min)

**Abre navegador:** http://localhost:8000/docs

**Muestra endpoints:**
```
GET /health          - Health check
GET /api/stats       - Estadísticas globales
GET /api/leaderboard - Rankings
GET /api/videos      - Galería de videos
POST /webhook        - Telegram webhook
```

**Click en GET /api/videos → Try it out:**
```json
Parameters:
limit: 3
offset: 0

Execute →
```

**Response:**
```json
{
  "success": true,
  "videos": [
    {
      "id": 24,
      "prompt": "Traditional Mexican mercado...",
      "category": "cultural_fusion",
      "caption": "Donde la tradición...",
      "hashtags": "#Uniswap #UniswapMexico...",
      "video_url": "https://oqdwjrhcdlflfebujnkq.supabase.co/...",
      "created_at": "2025-10-10T22:03:38.221295+00:00",
      "duration_seconds": 15,
      "creator_username": "anthonysurfermx",
      "metrics": {
        "views": 322,
        "likes": 2,
        "platform_posts": [
          {
            "platform": "tiktok",
            "url": "https://vt.tiktok.com/ZSUkwsTbD/",
            "views": 322
          }
        ]
      }
    }
  ],
  "total": 9,
  "limit": 3
}
```

**Menciona:** "API pública lista para conectar con frontend de Lovable"

---

### PASO 11: Terminal Commands (1 min)

**Muestra terminal con comandos curl:**

```bash
# 1. Health check
curl http://localhost:8000/health | jq
```
**Output:**
```json
{
  "status": "healthy",
  "agent_ready": true,
  "version": "2.0.0"
}
```

```bash
# 2. Stats globales
curl http://localhost:8000/api/stats | jq
```
**Output:**
```json
{
  "success": true,
  "stats": {
    "total_creators": 3,
    "total_videos": 9,
    "total_posts": 1,
    "top_creator_views": 322,
    "avg_videos_per_creator": 3.0
  }
}
```

```bash
# 3. Leaderboard
curl http://localhost:8000/api/leaderboard | jq
```
**Output:**
```json
{
  "success": true,
  "leaderboard": [
    {
      "rank": 1,
      "username": "anthonysurfermx",
      "total_views": 322,
      "total_videos": 9,
      "total_engagements": 3
    }
  ]
}
```

**Menciona:**
- "Endpoints RESTful estándar"
- "Respuestas en JSON"
- "CORS habilitado para desarrollo"
- "Listo para integrar con React/Next.js"

---

## 📍 PARTE 5: SMART CONTRACTS UNICHAIN (11:00 - 13:00)

### PASO 12: Mostrar Contrato (1 min)

**Abre VS Code:** `betting-pool-contracts/contracts/LeaderboardBetting.sol`

**Scroll a funciones clave y explica:**

```solidity
// Líneas 14-27
struct Pool {
    uint256 epochId;          // Semana/ciclo
    uint64  startTime;
    uint64  freezeTime;       // Cierra apuestas
    uint64  settleTime;       // Resultados finales
    uint256 totalAmount;      // Pool total
    uint32  participants;
    bool    settled;
    uint256[3] winners;       // Top 3 IDs
    bytes32 merkleRoot;       // Gas-efficient payouts
}
```

**Menciona:**
- "Sistema de apuestas semanales para top 3 creators"
- "Merkle proofs para distribución eficiente de premios"
- "Configurado específicamente para Unichain"

**Scroll a distribución:**
```solidity
// Líneas 40-42
uint16 public exactBucketBps = 5556;   // 55.56% si aciertas los 3
uint16 public twoBucketBps   = 3333;   // 33.33% si aciertas 2
uint16 public oneBucketBps   = 1111;   // 11.11% si aciertas 1
```

**Menciona:**
- "Sistema justo de distribución"
- "5% fee protocolo, 5% fee para creadores"
- "Pausable y con reentrancy protection"

---

### PASO 13: Configuración Unichain (1 min)

**Abre:** `betting-pool-contracts/hardhat.config.ts`

```typescript
// Líneas 23-28
unichain: {
  url: process.env.UNICHAIN_RPC || "https://rpc.unichain.org",
  accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
  chainId: parseInt(process.env.UNICHAIN_CHAIN_ID || "1301"),
  gasPrice: "auto",
}
```

**Terminal:**
```bash
cd betting-pool-contracts

# Compilar
npx hardhat compile

# Resultado esperado:
# ✓ Compiled 1 Solidity file successfully
```

**Menciona:**
- "Listo para desplegar en Unichain testnet/mainnet"
- "Costos bajos de gas"
- "MEV protection nativa"
- "Perfecto para gambling/betting pool"

**Comando de deploy (no ejecutar, solo mostrar):**
```bash
# Para desplegar:
npx hardhat run scripts/deploy.ts --network unichain

# Verificar en explorer:
npx hardhat verify --network unichain DEPLOYED_ADDRESS
```

---

## 📍 PARTE 6: MÉTRICAS Y ANALYTICS (13:00 - 14:00)

### PASO 14: Mostrar Scheduler (30 seg)

**Abre:** `app.py` líneas 44-55

```python
# Start metrics auto-updater (every 6 hours)
metrics_updater = get_metrics_updater()
scheduler.add_job(
    metrics_updater.update_all_metrics,
    'interval',
    hours=6,
    id='metrics_updater',
    replace_existing=True
)
scheduler.start()
logger.info("✅ Metrics auto-updater scheduled (every 6 hours)")
```

**Menciona:**
- "APScheduler actualiza métricas cada 6 horas automáticamente"
- "Scrapea TikTok, Twitter, Instagram sin API keys"
- "Notifica a usuarios cuando cambian de ranking"

---

### PASO 15: Datos Reales (30 seg)

**Terminal:**
```bash
python3 check_db.py
```

**Output:**
```
=== CREATORS ===
ID: 528305790, Username: anawgmi, Videos: 0
ID: 170416910, Username: Jardian, Videos: 0
ID: 1026323121, Username: anthonysurfermx, Videos: 9

=== VIDEOS ===
ID: 24, User: anthonysurfermx, Status: ready
ID: 23, User: anthonysurfermx, Status: ready
ID: 22, User: anthonysurfermx, Status: ready
...
```

**Menciona:**
- "Base de datos Supabase con datos reales"
- "9 videos generados"
- "1 post con métricas verificables"
- "Sistema funcionando end-to-end"

---

## 📍 PARTE 7: Q&A Y PRÓXIMOS PASOS (14:00 - 15:00)

### Key Metrics para Mencionar

✅ **Técnicamente:**
- AgentKit real (no simulado)
- Sora 2 integrado
- 2 capas de moderación (keyword + AI)
- Sistema de strikes automático
- API pública funcional
- Smart contracts listos para deploy

✅ **Tracción:**
- 3 creadores en beta privada
- 9 videos generados
- 322 vistas reales verificables
- 0.93% engagement rate

✅ **Escalabilidad:**
- Supabase (millones de usuarios)
- Merkle proofs (gas-efficient)
- CDN-ready (Supabase Storage)
- Rate limiting configurable

---

### Roadmap

**Corto Plazo (1 semana):**
- Desplegar contratos en Unichain Sepolia
- Conectar frontend Lovable
- Abrir beta a 50 usuarios

**Mediano Plazo (1 mes):**
- YouTube Shorts + Instagram Reels
- Sistema de referidos
- Panel de admin completo

**Largo Plazo (3 meses):**
- Token de gobernanza
- NFTs de mejores videos
- Marketplace de prompts

---

### FAQs Preparadas

**Q: ¿Cuánto cuesta generar un video?**
A: ~$2-5 por video con Sora 2 (según duración)

**Q: ¿Puede escalar a miles de usuarios?**
A: Sí, Supabase + rate limiting + async workers

**Q: ¿Por qué Telegram y no web app?**
A: Familiaridad, bajo friction, notificaciones nativas, mobile-first

**Q: ¿Las métricas son reales?**
A: Sí, scraping real de TikTok (322 vistas verificables)

**Q: ¿Qué pasa si Sora 2 falla?**
A: Retry logic + fallback a queue + notificación al usuario

**Q: ¿Cómo previenen abuse?**
A: Daily limits, cooldowns, 3-strike system, AI validation

---

## 🎬 CIERRE

**Mensaje Final:**

"Uni Creator Bot v2 es más que un generador de videos - es una plataforma completa de UGC que:

✅ Democratiza la creación con IA (Sora 2)
✅ Mantiene brand consistency (moderación automática)
✅ Gamifica la participación (leaderboard + betting)
✅ Trackea ROI real (métricas de social media)
✅ Se construye en Unichain (descentralización + bajos costos)

**Estamos listos para escalar a 500+ creadores en México y más allá.**"

---

## 📋 CHECKLIST FINAL

Antes de la demo, verifica:
- [ ] Servidor corriendo (port 8000)
- [ ] Telegram bot activo
- [ ] Navegador con tabs: /docs, TikTok video, logs
- [ ] VS Code con archivos clave abiertos
- [ ] Terminal con venv activado
- [ ] Screenshots de backup por si algo falla

---

## 🚀 ¡A ROMPERLA!

**Duración:** 15 minutos
**Impacto:** Alto
**Complejidad técnica demostrada:** Avanzada
**Tracción real:** Verificable

💜🦄
