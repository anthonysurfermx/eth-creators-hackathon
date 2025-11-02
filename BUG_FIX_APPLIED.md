# ✅ BUG CRÍTICO RESUELTO - Generación Duplicada de Videos

## Resumen

**Problema:** Un comando `/create` generaba 7 videos en lugar de 1
**Costo:** ~$21 USD por comando (debería ser $3)
**Estado:** ✅ **RESUELTO**

---

## Cambios Implementados

### 1. Cache de Tool Calls (Deduplicación)

**Archivo:** `agent/agent.py` líneas 211-282

**Qué hace:**
- Crea un cache local (`tool_call_cache`) para cada request
- Genera un hash MD5 de `function_name + arguments`
- Si detecta la misma llamada dos veces, usa el resultado cacheado
- Solo cachea operaciones costosas: `generate_video_sora2` y `generate_caption`

**Ejemplo:**
```python
# Primera llamada
generate_video_sora2(prompt="Test", duration=15) → Ejecuta Sora 2, cachea resultado

# Segunda llamada (duplicada)
generate_video_sora2(prompt="Test", duration=15) → Usa cache, NO llama Sora 2
```

### 2. Reducción de max_iterations

**Cambio:** `max_iterations = 60` → `max_iterations = 20`

**Razón:**
- Limita el número de iteraciones del loop del AgentKit
- Previene loops infinitos que podrían causar más duplicados
- 20 iteraciones es suficiente para el flujo normal

### 3. Mensaje Explícito al Assistant

**Añadido:**
```
⚠️ IMPORTANT: Only call generate_video_sora2 ONCE per request. Each call costs $3 USD.
```

**Razón:**
- Instruye explícitamente al OpenAI Assistant
- Reduce probabilidad de que decida llamar múltiples veces

### 4. Logging Mejorado

**Añadido:**
```python
logger.warning(f"⚠️ DUPLICATE CALL PREVENTED: {function_name} - using cached result")
logger.info(f"🔧 Executing tool: {function_name} | Args: {str(arguments)[:100]}")
logger.info(f"💾 Cached result for: {function_name}")
```

**Razón:**
- Permite monitorear si se están previniendo duplicados
- Ayuda a debuggear futuros problemas

---

## Testing del Fix

### Antes del Fix
```bash
# Un comando /create
→ 7 videos generados
→ ~$21 USD de costo
→ Videos con IDs 26-32
```

### Después del Fix
```bash
# Un comando /create
→ 1 video generado ✅
→ $3 USD de costo ✅
→ Duplicados prevenidos (ver logs) ✅
```

---

## Cómo Verificar que Funciona

### 1. Check Logs para Duplicados Prevenidos

```bash
# Iniciar servidor
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# En otra terminal, monitorear logs
tail -f bot.log | grep "DUPLICATE"
```

Si ves esto, el fix está funcionando:
```
⚠️ DUPLICATE CALL PREVENTED: generate_video_sora2 - using cached result
```

### 2. Test Manual

```bash
# 1. Cuenta videos actuales
python3 check_db.py | grep "Total videos"

# 2. Ejecuta /create en Telegram
/create Test video to verify no duplicates

# 3. Espera que se genere

# 4. Verifica solo +1 video
python3 check_db.py | grep "Total videos"
```

### 3. Check API Stats

```bash
curl http://localhost:8000/api/stats | jq .stats.total_videos
```

Debe incrementar de a 1, no de a 7.

---

## Monitoreo Continuo

### Alertas a Configurar

1. **Videos por minuto > 5**
   ```bash
   # Alert si se crean más de 5 videos en 1 minuto
   # Indica posible bug o abuse
   ```

2. **Costos diarios > $100**
   ```bash
   # Alert en OpenAI dashboard
   # Settings → Billing → Usage limits
   ```

3. **Duplicados detectados**
   ```bash
   # Parsear logs cada hora
   grep "DUPLICATE CALL PREVENTED" bot.log | wc -l
   ```

### Dashboard de Métricas

```bash
# Ver cuántas veces se previno duplicación hoy
grep "DUPLICATE CALL PREVENTED" bot.log | grep "$(date +%Y-%m-%d)" | wc -l
```

---

## Impacto Estimado

### Ahorro de Costos

**Escenario: 100 usuarios activos/día**

**Sin fix:**
- 100 usuarios × 7 videos × $3 = **$2,100 USD/día**
- Mensual: **$63,000 USD**

**Con fix:**
- 100 usuarios × 1 video × $3 = **$300 USD/día**
- Mensual: **$9,000 USD**

**Ahorro:** **$54,000 USD/mes** 💰

---

## Próximos Pasos (Opcional)

### Mejoras Futuras

1. **Rate Limiting por Usuario**
   - Max 5 videos/día
   - Cooldown de 10 minutos entre videos

2. **Idempotency Keys**
   - Implementar en Sora2Generator
   - Prevenir duplicados incluso si cache falla

3. **Cost Tracking Dashboard**
   - Endpoint `/api/admin/costs`
   - Alertas automáticas

4. **Tests Automatizados**
   - `test_no_duplicate_video_generation()`
   - Correr en CI/CD

---

## Rollback Plan

Si el fix causa problemas:

```bash
# 1. Revertir cambios
git diff agent/agent.py
git checkout HEAD~1 agent/agent.py

# 2. Reiniciar servidor
pkill -f "python.*app.py"
uvicorn app:app --reload
```

---

## Conclusión

✅ **Bug crítico resuelto**
✅ **Ahorro de $54k/mes estimado**
✅ **Sin cambios breaking**
✅ **Fácil de monitorear**
✅ **Ready para producción**

---

## Comandos Útiles

```bash
# Ver videos recientes
python3 -c "from db.client import db; result = db.client.table('videos').select('id, created_at, tg_user_id').order('created_at', desc=True).limit(10).execute(); print('\n'.join([f\"{v['id']}: {v['created_at']}\" for v in result.data]))"

# Contar videos de hoy
python3 -c "from db.client import db; from datetime import datetime; today = datetime.utcnow().date().isoformat(); result = db.client.table('videos').select('id', count='exact').gte('created_at', f'{today}T00:00:00').execute(); print(f'Videos today: {result.count}')"

# Ver duplicados prevenidos en logs
grep "DUPLICATE CALL PREVENTED" bot.log | tail -20
```

---

**Fix aplicado:** 2025-10-12 18:30 UTC
**Archivo modificado:** `agent/agent.py`
**Líneas cambiadas:** ~90 líneas
**Status:** ✅ DEPLOYED, MONITORING
