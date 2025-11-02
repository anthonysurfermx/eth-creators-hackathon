# 🚨 Problema: Creación Excesiva de Videos

## Diagnóstico

### Estado Actual
- **Total videos:** 16 (aumentó de 9 a 16)
- **Nuevos videos:** 7 videos creados entre 00:30 y 00:41 (13 Oct 2025)
- **Usuario:** anthonysurfermx (ID: 1026323121)
- **Prompt repetido:** "Traditional Mexican mercado transforms into hologr..."
- **Duración del burst:** 11 minutos

### Timeline de Creación
```
ID: 26 - 2025-10-13T00:30:07
ID: 27 - 2025-10-13T00:30:56
ID: 28 - 2025-10-13T00:33:13
ID: 29 - 2025-10-13T00:35:25
ID: 30 - 2025-10-13T00:37:12
ID: 31 - 2025-10-13T00:39:07
ID: 32 - 2025-10-13T00:41:11
```

---

## Causas Posibles

### 1. Testing Manual ✅ (Más Probable)
- Alguien estaba probando el bot anoche
- Ejecutó `/create` múltiples veces
- El mismo prompt se usó repetidamente

### 2. Bot Loop ❌ (Menos Probable)
- No hay evidencia de loop automático en logs
- No hay scheduler que genere videos automáticamente
- Los timestamps muestran intervalos irregulares (2-3 minutos)

### 3. Webhook Duplicado ❌ (No Aplica)
- Las creaciones fueron hace 2 días
- No hay actividad reciente similar

---

## Problemas Identificados

### ❌ 1. Sin Rate Limiting Efectivo
Actualmente NO hay límites implementados para:
- Videos por usuario por día
- Cooldown entre creaciones
- Límite de intentos fallidos

### ❌ 2. Sin Costo Tracking
- Cada video cuesta ~$2-5 (Sora 2)
- 7 videos = ~$14-35 en costos no planificados
- No hay alertas de gasto

### ❌ 3. Sin Confirmación de Usuario
- El bot ejecuta `/create` inmediatamente
- No hay "¿Estás seguro?" para prompts costosos
- No hay preview antes de generar

---

## Soluciones Recomendadas

### 🔧 1. Implementar Rate Limiting (URGENTE)

**Archivo:** `app.py` o nuevo `middleware/rate_limiter.py`

```python
from datetime import datetime, timedelta
from collections import defaultdict

# In-memory rate limiter (usar Redis en producción)
user_video_count = defaultdict(list)
user_last_video = {}

MAX_VIDEOS_PER_DAY = 5
COOLDOWN_MINUTES = 10

async def check_rate_limit(user_id: int) -> tuple[bool, str]:
    """
    Returns: (allowed: bool, message: str)
    """
    now = datetime.utcnow()

    # Check cooldown
    if user_id in user_last_video:
        last_time = user_last_video[user_id]
        cooldown_end = last_time + timedelta(minutes=COOLDOWN_MINUTES)
        if now < cooldown_end:
            wait_minutes = int((cooldown_end - now).total_seconds() / 60)
            return False, f"⏳ Cooldown active. Try again in {wait_minutes} minutes."

    # Check daily limit
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if user_id in user_video_count:
        # Remove old timestamps
        user_video_count[user_id] = [
            ts for ts in user_video_count[user_id]
            if ts > today_start
        ]

        if len(user_video_count[user_id]) >= MAX_VIDEOS_PER_DAY:
            reset_time = today_start + timedelta(days=1)
            hours_left = int((reset_time - now).total_seconds() / 3600)
            return False, f"🚫 Daily limit reached ({MAX_VIDEOS_PER_DAY} videos/day). Resets in {hours_left}h."

    return True, ""

def record_video_creation(user_id: int):
    """Record that user created a video"""
    now = datetime.utcnow()
    user_video_count[user_id].append(now)
    user_last_video[user_id] = now
```

**Integrar en comando `/create`:**

```python
async def create_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Check rate limit FIRST
    allowed, message = await check_rate_limit(user_id)
    if not allowed:
        await update.message.reply_text(message)
        return

    # ... rest of create logic ...

    # After successful creation
    record_video_creation(user_id)
```

---

### 🔧 2. Confirmación para Prompts Similares

```python
async def create_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    prompt = ' '.join(context.args)

    # Check if user created similar video recently
    recent_videos = db.client.table("videos") \
        .select("prompt, created_at") \
        .eq("tg_user_id", user_id) \
        .gte("created_at", (datetime.utcnow() - timedelta(hours=1)).isoformat()) \
        .execute()

    if recent_videos.data:
        similar = [v for v in recent_videos.data if v["prompt"][:50] == prompt[:50]]
        if similar:
            await update.message.reply_text(
                f"⚠️ **Similar video created recently**\n\n"
                f"You created a similar video {len(similar)} time(s) in the last hour.\n\n"
                f"Cost: ~${2 + len(similar) * 2} today\n\n"
                f"Reply 'yes' to confirm or /cancel to abort.",
                parse_mode="Markdown"
            )
            # Wait for confirmation (implement conversation handler)
            return

    # ... continue with creation ...
```

---

### 🔧 3. Cost Tracking y Alertas

**Nuevo archivo:** `utils/cost_tracker.py`

```python
from datetime import datetime, timedelta

SORA2_COST_PER_VIDEO = 3.0  # USD promedio

class CostTracker:
    def __init__(self):
        self.daily_costs = {}

    def record_video_cost(self, user_id: int, cost: float = SORA2_COST_PER_VIDEO):
        """Record cost of video generation"""
        today = datetime.utcnow().date().isoformat()
        key = f"{today}:{user_id}"

        if key not in self.daily_costs:
            self.daily_costs[key] = 0

        self.daily_costs[key] += cost

        # Alert if user exceeds daily budget
        if self.daily_costs[key] > 15:  # $15/day limit per user
            logger.warning(f"🚨 User {user_id} exceeded daily budget: ${self.daily_costs[key]}")
            return True

        return False

    def get_user_daily_cost(self, user_id: int) -> float:
        """Get user's spending today"""
        today = datetime.utcnow().date().isoformat()
        key = f"{today}:{user_id}"
        return self.daily_costs.get(key, 0)

cost_tracker = CostTracker()
```

**Integrar:**

```python
async def create_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Check cost before creating
    current_cost = cost_tracker.get_user_daily_cost(user_id)
    await update.message.reply_text(
        f"💰 Today's cost: ${current_cost:.2f}\n"
        f"This video: ~$3.00\n"
        f"Total: ~${current_cost + 3:.2f}"
    )

    # ... create video ...

    # Record cost after creation
    exceeded = cost_tracker.record_video_cost(user_id)
    if exceeded:
        await update.message.reply_text(
            "🚨 **Daily budget exceeded**\n\n"
            "You've spent over $15 today. Please try again tomorrow."
        )
```

---

### 🔧 4. Admin Dashboard para Monitoreo

**Nuevo endpoint:** `/api/admin/videos/recent`

```python
@app.get("/api/admin/videos/recent")
async def get_recent_videos(hours: int = 24):
    """Get videos created in last N hours"""
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

    result = db.client.table("videos") \
        .select("id, created_at, tg_user_id, prompt, status") \
        .gte("created_at", cutoff) \
        .order("created_at", desc=True) \
        .execute()

    # Group by user
    by_user = {}
    for video in result.data:
        uid = video["tg_user_id"]
        if uid not in by_user:
            by_user[uid] = []
        by_user[uid].append(video)

    # Calculate stats
    stats = {
        "total_videos": len(result.data),
        "unique_users": len(by_user),
        "estimated_cost": len(result.data) * 3,
        "by_user": {
            uid: {
                "count": len(videos),
                "cost": len(videos) * 3,
                "prompts": [v["prompt"][:50] for v in videos[:3]]
            }
            for uid, videos in by_user.items()
        }
    }

    return {
        "success": True,
        "period_hours": hours,
        "stats": stats,
        "videos": result.data
    }
```

---

### 🔧 5. Variables de Entorno para Límites

**Añadir a `.env`:**

```bash
# Rate Limiting
MAX_VIDEOS_PER_DAY=5
MAX_VIDEOS_PER_HOUR=2
COOLDOWN_MINUTES=10
MAX_DAILY_COST_PER_USER=15

# Admin Alerts
ALERT_EMAIL=admin@unicreator.com
ALERT_TELEGRAM_CHAT_ID=123456789
ALERT_THRESHOLD_COST=50
```

---

## Acciones Inmediatas

### 1. ✅ Revisar si fue Testing Intencional
```bash
# Verificar quién es el usuario
curl http://localhost:8000/api/leaderboard | jq
# anthonysurfermx = ID 1026323121
```

**Si eres tú o tu equipo probando → OK, pero añadir rate limiting**

### 2. ⚠️ Verificar Costos en OpenAI
```bash
# Ir a: https://platform.openai.com/usage
# Verificar gasto en Sora 2 API
# 7 videos × $3 = ~$21 USD
```

### 3. 🔧 Implementar Rate Limiting HOY
```bash
# Prioridad 1: Cooldown de 10 minutos
# Prioridad 2: Límite de 5 videos/día
# Prioridad 3: Cost tracking
```

### 4. 📊 Monitorear las Próximas 24 Horas
```bash
# Cada hora, ejecutar:
curl http://localhost:8000/api/admin/videos/recent?hours=1

# O setup alert:
watch -n 3600 'curl -s http://localhost:8000/api/admin/videos/recent?hours=1 | jq .stats.total_videos'
```

---

## Prevención Futura

### ✅ Checklist de Seguridad

- [ ] Rate limiting implementado (cooldown + daily limit)
- [ ] Cost tracking activo
- [ ] Alertas configuradas (Telegram/email)
- [ ] Confirmación para prompts similares
- [ ] Admin dashboard para monitoreo
- [ ] Logs de auditoria (quién, cuándo, cuánto)
- [ ] Tests de rate limiting

### ✅ Mejores Prácticas

1. **Siempre usar límites en producción**
   - 5 videos/día para usuarios normales
   - 10 videos/día para usuarios verificados
   - 10 minutos cooldown entre videos

2. **Monitorear costos diariamente**
   - Setup billing alerts en OpenAI
   - Track costos por usuario
   - Set budget limits

3. **Testing en ambiente separado**
   - Usar variables TESTING=true
   - Mock Sora 2 API en tests
   - No usar producción para demos

4. **Documentar patrones de uso**
   - Cuántos videos por usuario típico
   - Horarios pico
   - Costos promedio

---

## Comandos Útiles

### Limpiar Videos de Prueba (Opcional)
```bash
# CUIDADO: Esto borra videos
# Solo ejecutar si los 7 videos son pruebas no deseadas

python3 << 'EOF'
from db.client import db

# Delete test videos (IDs 26-32)
for video_id in range(26, 33):
    db.client.table("videos").delete().eq("id", video_id).execute()
    print(f"Deleted video {video_id}")
EOF
```

### Ver Videos por Usuario
```bash
source venv/bin/activate
python3 << 'EOF'
from db.client import db
from collections import Counter

result = db.client.table("videos").select("tg_user_id").execute()
counter = Counter([v["tg_user_id"] for v in result.data])

print("Videos per user:")
for uid, count in counter.most_common():
    print(f"  User {uid}: {count} videos")
EOF
```

### Calcular Costos
```bash
python3 -c "
total_videos = 16
cost_per_video = 3.0
print(f'Total videos: {total_videos}')
print(f'Estimated cost: \${total_videos * cost_per_video:.2f}')
print(f'Last 7 videos cost: \${7 * cost_per_video:.2f}')
"
```

---

## Conclusión

**Problema:** 7 videos creados en 11 minutos → ~$21 en costos no planificados

**Causa:** Testing manual sin rate limiting

**Solución:** Implementar rate limiting + cost tracking + confirmaciones

**Prioridad:** 🔴 ALTA - Implementar antes de abrir beta pública

**Tiempo estimado:** 2-3 horas para implementación completa

---

**Última actualización:** 2025-10-12 18:10 UTC
