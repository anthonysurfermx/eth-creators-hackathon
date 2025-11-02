# 🛡️ SEGURIDAD PARA LA DEMO

## Estado Actual del Fix

✅ **Fixes aplicados:**
- Cache de tool calls (previene duplicados en mismo request)
- max_iterations = 20 (reduce daño máximo de 60 a 20 videos)
- Logging mejorado (visibilidad de duplicados)

❌ **AÚN FALTAN:**
- Rate limiting por usuario
- Cooldown entre videos
- Límite diario de videos
- Circuit breaker

## Riesgo Actual

**Si alguien hace `/create` en la demo:**

| Escenario | Probabilidad | Daño Máximo |
|-----------|--------------|-------------|
| **Funciona normal** | 80% | $3 (1 video) ✅ |
| **Bug parcial** | 15% | $60 (20 videos) ⚠️ |
| **Bug crítico** | 5% | $60+ (si múltiples usuarios) 🔴 |

## Opciones para la Demo

### 🟢 Opción 1: Demo SIN creación en vivo (SEGURO)

**Mostrar:**
- ✅ Videos ya creados (9 disponibles)
- ✅ Screenshots del bot en Telegram
- ✅ API funcionando (GET /api/videos)
- ✅ Código y arquitectura
- ✅ Leaderboard y métricas

**NO mostrar:**
- ❌ Creación de videos en vivo
- ❌ Bot activo en Telegram

**Ventajas:**
- Riesgo: $0
- Sin sorpresas
- Demo controlada

**Desventajas:**
- Menos impactante
- No se ve el flujo completo

---

### 🟡 Opción 2: Demo CON creación controlada (MEDIO RIESGO)

**Implementar ANTES de la demo:**

1. **Rate Limiting Temporal** (5 minutos)
   ```python
   # Añadir a app.py
   from datetime import datetime, timedelta

   demo_users = {}  # {user_id: last_video_time}
   DEMO_COOLDOWN = 600  # 10 minutos

   async def check_demo_limit(user_id):
       now = datetime.now()
       if user_id in demo_users:
           last = demo_users[user_id]
           if (now - last).seconds < DEMO_COOLDOWN:
               return False, "⏳ Demo cooldown: 1 video cada 10 minutos"
       return True, None
   ```

2. **Límite Total de Videos** (5 minutos)
   ```python
   # Máximo 3 videos durante la demo
   MAX_DEMO_VIDEOS = 3
   demo_video_count = 0

   if demo_video_count >= MAX_DEMO_VIDEOS:
       return "Demo limit reached - contact admin"
   ```

3. **Whitelist de Usuarios** (2 minutos)
   ```python
   # Solo TÚ puedes crear videos en la demo
   DEMO_ALLOWED_USERS = [1026323121]  # Tu user ID

   if user_id not in DEMO_ALLOWED_USERS:
       return "Demo mode - video creation disabled"
   ```

**Ventajas:**
- Demo más impresionante
- Muestras el flujo completo
- Controlado (solo tú creas)

**Desventajas:**
- Riesgo: hasta $9-60 si algo falla
- Requiere implementación previa

---

### 🔴 Opción 3: Demo completamente abierta (ALTO RIESGO)

**NO RECOMENDADO** sin implementar rate limiting completo.

**Riesgo:** Si 10 personas hacen `/create`:
- Caso normal: $30 (10 videos)
- Caso malo: $600 (10 × 20 videos cada uno)

---

## Recomendación Final

### Para la demo de HOY/MAÑANA:

**🟢 USA OPCIÓN 1 (Sin creación en vivo)**

**Por qué:**
- Ya tienes 9 videos excelentes para mostrar
- El video de TikTok tiene 323 vistas REALES
- Puedes mostrar TODO excepto creación en vivo
- Riesgo: $0
- Tiempo de implementación: 0 minutos

### Para producción (después de la demo):

**Implementar TODO esto:**
1. Rate limiting por usuario (5 videos/día)
2. Cooldown entre videos (10 minutos)
3. Circuit breaker (abort si >3 tool calls en 1 min)
4. Billing limits en OpenAI ($50/día)
5. Alertas en tiempo real de costos
6. Tests automatizados del fix

---

## Script de Demo Recomendado

### Parte 1: Intro (2 min)
"Este es Uni Creator Bot, que permite crear videos UGC con Sora 2..."

### Parte 2: Mostrar Videos (3 min)
- Abre http://localhost:8000/api/videos
- Muestra los 9 videos en Supabase
- Abre el de TikTok con 323 vistas REALES

### Parte 3: Bot en Telegram (screenshots) (2 min)
- Screenshots del flujo: /start → /create → video generado
- Muestras los comandos disponibles
- Explicas el sistema de moderación

### Parte 4: Arquitectura (2 min)
- AgentKit + Sora 2
- Cache de tool calls (el fix del bug)
- Smart contracts en Unichain

### Parte 5: Leaderboard (1 min)
- http://localhost:8000/api/leaderboard
- Métricas en tiempo real

**Total: 10 minutos, $0 de riesgo**

---

## Si INSISTES en crear video en vivo

### Implementar esto AHORA (10 minutos):

```python
# Añadir a app.py antes del comando /create

# DEMO MODE - SAFETY
DEMO_MODE = True
DEMO_ALLOWED_USER = 1026323121  # TU user ID
demo_videos_created = 0
MAX_DEMO_VIDEOS = 2

async def create_video_command(update, context):
    user_id = update.effective_user.id

    if DEMO_MODE:
        # Only you can create
        if user_id != DEMO_ALLOWED_USER:
            await update.message.reply_text(
                "🎬 Demo Mode Active\n\n"
                "Video creation is temporarily disabled.\n"
                "Showing existing videos only.\n\n"
                "Check out our gallery: /videos"
            )
            return

        # Max 2 videos during demo
        global demo_videos_created
        if demo_videos_created >= MAX_DEMO_VIDEOS:
            await update.message.reply_text(
                "⚠️ Demo limit reached (2 videos max)\n\n"
                "This is to prevent costs during the demo.\n"
                "In production: 5 videos/day per user."
            )
            return

        demo_videos_created += 1

    # Continue with normal flow...
```

---

## Decisión Requerida

**¿Qué opción quieres para la demo?**

**A) Opción 1 - Sin creación en vivo** (SEGURO, 0 min setup)
**B) Opción 2 - Solo tú puedes crear** (MEDIO, 10 min setup)
**C) Opción 3 - Abierto a todos** (RIESGO, no recomendado)

**Mi recomendación: Opción A**

Ya tienes:
- 9 videos excelentes
- 1 con 323 vistas reales
- API funcionando
- Arquitectura completa

No necesitas arriesgar $60+ para una demo. Puedes decir:
"El bot está funcionando en producción, aquí están los videos reales que usuarios ya crearon"

---

**¿Cuál eliges?**
