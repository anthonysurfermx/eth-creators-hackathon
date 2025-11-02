# 🚨 BUG CRÍTICO: Generación Duplicada de Videos

## Problema Identificado

**Síntoma:** Un solo comando `/create` genera múltiples videos (7 en este caso)

**Causa Raíz:** El OpenAI Assistant está llamando `generate_video_sora2` múltiples veces en el mismo run

**Línea problemática:** `agent/agent.py` líneas 241-274

```python
while run.status in ["queued", "in_progress", "requires_action"] and iteration < max_iterations:
    # ...
    if run.status == "requires_action":
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            # ❌ PROBLEMA: No hay verificación de llamadas duplicadas
            output = await self._execute_tool(function_name, arguments, tg_user_id)
```

## Por Qué Ocurre

1. El Assistant puede decidir llamar la misma función múltiples veces
2. No hay cache/deduplicación de tool calls
3. Sora 2 API es **idempotente** pero crea un nuevo video cada vez
4. Cada video cuesta ~$3 USD

## Costos del Bug

- **7 videos** × **$3** = **~$21 USD** por un solo comando
- Si 100 usuarios hacen esto = **$2,100 USD**
- **CRÍTICO para producción**

---

## SOLUCIÓN 1: Cache de Tool Calls (Rápido - 5 min)

### Implementar deduplicación en `agent.py`

```python
# agent/agent.py - línea 200
async def create_video(
    self,
    tg_user_id: int,
    username: str,
    prompt: str
) -> Dict[str, Any]:
    """Main workflow with deduplication"""
    if not self.assistant_id:
        await self.initialize()

    try:
        # ✅ ADD: Cache para evitar llamadas duplicadas
        tool_call_cache = {}  # {function_name+args_hash: result}

        thread = await client.beta.threads.create()

        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"""User @{username} (ID: {tg_user_id}) wants to create a video.

Prompt: "{prompt}"

⚠️ IMPORTANT: Only call generate_video_sora2 ONCE. Each call costs money.

Please:
1. Check if user can create videos (limits/cooldown)
2. Validate the prompt
3. If approved, generate the video (ONCE ONLY)
4. Generate caption + hashtags
5. Save to database
6. Return the complete package"""
        )

        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id
        )

        max_iterations = 60
        iteration = 0

        while run.status in ["queued", "in_progress", "requires_action"] and iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}/{max_iterations}, status: {run.status}")
            await asyncio.sleep(2)

            run = await client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            if run.status == "requires_action":
                tool_outputs = []

                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # ✅ ADD: Create cache key
                    import hashlib
                    args_str = json.dumps(arguments, sort_keys=True)
                    cache_key = f"{function_name}:{hashlib.md5(args_str.encode()).hexdigest()}"

                    # ✅ ADD: Check cache first
                    if cache_key in tool_call_cache:
                        logger.warning(f"⚠️ Duplicate call detected: {function_name} - using cached result")
                        output = tool_call_cache[cache_key]
                    else:
                        logger.info(f"Executing tool: {function_name}")
                        output = await self._execute_tool(function_name, arguments, tg_user_id)

                        # ✅ ADD: Cache expensive operations only
                        if function_name in ["generate_video_sora2", "generate_caption"]:
                            tool_call_cache[cache_key] = output

                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(output)
                    })

                run = await client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

        # ... rest of code
```

---

## SOLUCIÓN 2: Video Generation Lock (Medio - 15 min)

### Añadir lock por usuario para prevenir concurrencia

```python
# agent/agent.py - al inicio del archivo
from asyncio import Lock
from collections import defaultdict

# Global locks por usuario
user_video_locks = defaultdict(Lock)

# En la clase
async def create_video(self, tg_user_id: int, username: str, prompt: str):
    """Main workflow with user lock"""

    # ✅ Acquire lock para este usuario
    async with user_video_locks[tg_user_id]:
        # Check si ya hay un video siendo generado para este prompt
        recent_video = db.client.table("videos") \
            .select("id, created_at, status") \
            .eq("tg_user_id", tg_user_id) \
            .eq("prompt", prompt) \
            .gte("created_at", (datetime.utcnow() - timedelta(minutes=5)).isoformat()) \
            .execute()

        if recent_video.data:
            logger.warning(f"⚠️ Duplicate video creation prevented for user {tg_user_id}")
            return {
                "success": False,
                "error": "duplicate_request",
                "message": "Video already being generated for this prompt"
            }

        # Continue with normal flow...
```

---

## SOLUCIÓN 3: Idempotency Key (Mejor - 20 min)

### Implementar idempotency key en Sora 2 generator

```python
# agent/tools/sora2.py

class Sora2Generator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.active_generations = {}  # {idempotency_key: video_id}

    async def generate(
        self,
        prompt: str,
        duration: int,
        category: str,
        idempotency_key: str = None
    ) -> Dict:
        """Generate video with idempotency"""

        # ✅ Generate or use provided idempotency key
        if not idempotency_key:
            import hashlib
            idempotency_key = hashlib.sha256(
                f"{prompt}:{duration}:{category}".encode()
            ).hexdigest()[:16]

        # ✅ Check if already generating
        if idempotency_key in self.active_generations:
            video_id = self.active_generations[idempotency_key]
            logger.warning(f"⚠️ Duplicate generation prevented: {idempotency_key}")

            # Return existing video
            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://api.openai.com/v1/videos/{video_id}/content",
                "cached": True
            }

        # ✅ Generate new video
        try:
            logger.info(f"🎬 Generating video with key: {idempotency_key}")

            response = await self.client.video.generate(
                model=settings.sora2_model,
                prompt=prompt,
                duration=duration,
                resolution="1080x1920"
            )

            video_id = response.id

            # ✅ Cache result
            self.active_generations[idempotency_key] = video_id

            # ✅ Clean up cache after 5 minutes
            asyncio.create_task(self._cleanup_cache(idempotency_key, delay=300))

            return {
                "success": True,
                "video_id": video_id,
                "video_url": f"https://api.openai.com/v1/videos/{video_id}/content",
                "duration": duration,
                "cached": False
            }

        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return {"success": False, "error": str(e)}

    async def _cleanup_cache(self, key: str, delay: int):
        """Clean up cache after delay"""
        await asyncio.sleep(delay)
        if key in self.active_generations:
            del self.active_generations[key]
            logger.info(f"🗑️ Cleaned up cache for key: {key}")
```

---

## SOLUCIÓN 4: Rate Limiting en DB (Complementario)

### Añadir constraint en Supabase

```sql
-- migrations/add_video_creation_constraint.sql

-- Prevent duplicate videos with same prompt in short time
CREATE UNIQUE INDEX idx_unique_recent_video
ON videos (tg_user_id, prompt, (date_trunc('minute', created_at)))
WHERE created_at > NOW() - INTERVAL '5 minutes';

-- Explanation:
-- - Same user
-- - Same prompt
-- - Within same minute
-- = Reject as duplicate
```

---

## IMPLEMENTACIÓN INMEDIATA (Ahora)

### Paso 1: Fix Rápido - Añadir cache en agent.py

```bash
# Editar agent/agent.py
```

### Paso 2: Añadir logging de tool calls

```python
# En _execute_tool, añadir al inicio:
logger.warning(f"🔧 Tool call: {function_name} with args: {json.dumps(arguments)[:100]}")
```

### Paso 3: Limitar max_iterations

```python
# Cambiar línea 238
max_iterations = 20  # Reducir de 60 a 20
```

### Paso 4: Añadir timeout por video

```python
# Añadir timeout para operaciones costosas
async def _generate_video(self, prompt: str, duration: int, category: str) -> Dict:
    try:
        # ✅ Timeout de 3 minutos
        return await asyncio.wait_for(
            self._generate_video_internal(prompt, duration, category),
            timeout=180
        )
    except asyncio.TimeoutError:
        logger.error("Video generation timed out after 3 minutes")
        return {"success": False, "error": "timeout"}
```

---

## Testing del Fix

### Test 1: Verificar cache funciona

```bash
# En terminal Python
from agent.agent import agent
import asyncio

async def test():
    result = await agent.create_video(
        tg_user_id=123,
        username="test",
        prompt="Test video"
    )
    print(f"Result: {result}")

asyncio.run(test())

# Verificar en logs que no hay llamadas duplicadas
```

### Test 2: Verificar solo 1 video se crea

```bash
# Antes del test
python3 check_db.py | grep "Total videos"

# Después del test
python3 check_db.py | grep "Total videos"

# Debe incrementar en 1, no en 7
```

---

## Monitoring Post-Fix

### Añadir métricas de tool calls

```python
# agent/agent.py
class UniswapCreatorAgent:
    def __init__(self):
        # ...
        self.metrics = {
            "total_runs": 0,
            "tool_calls": defaultdict(int),
            "cached_calls": defaultdict(int),
            "duplicate_calls": 0
        }

    async def _execute_tool(self, function_name, arguments, tg_user_id):
        self.metrics["tool_calls"][function_name] += 1
        # ...

    def get_metrics(self):
        return self.metrics

# Endpoint para ver métricas
@app.get("/api/admin/agent/metrics")
async def get_agent_metrics():
    return {
        "success": True,
        "metrics": agent.get_metrics()
    }
```

---

## Prevención Futura

### 1. Tests Automatizados

```python
# tests/test_agent_deduplication.py

async def test_no_duplicate_video_generation():
    """Ensure only 1 video is generated per request"""

    initial_count = get_video_count()

    await agent.create_video(
        tg_user_id=999,
        username="testuser",
        prompt="Test duplicate prevention"
    )

    final_count = get_video_count()

    assert final_count == initial_count + 1, f"Expected 1 new video, got {final_count - initial_count}"
```

### 2. Circuit Breaker

```python
# Si detectas > 3 llamadas a generate_video en 1 minuto, aborta
class CircuitBreaker:
    def __init__(self, threshold=3, window=60):
        self.threshold = threshold
        self.window = window
        self.calls = []

    def allow_call(self, function_name):
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.window]

        if len(self.calls) >= self.threshold:
            return False

        self.calls.append(now)
        return True
```

---

## Rollback Plan

### Si el fix causa problemas:

```bash
# 1. Revertir cambios
git diff agent/agent.py
git checkout agent/agent.py

# 2. Implementar fix mínimo
# Solo añadir timeout y reducir max_iterations

# 3. Deploy gradualmente
# Test con 1 usuario → 10 usuarios → todos
```

---

## Estimación de Costos Ahorrados

**Sin fix:**
- 100 usuarios × 7 videos duplicados × $3 = **$2,100 USD/día**

**Con fix:**
- 100 usuarios × 1 video × $3 = **$300 USD/día**

**Ahorro:** **$1,800 USD/día** = **$54,000 USD/mes**

---

## Prioridad

🔴 **CRÍTICO - IMPLEMENTAR AHORA**

Tiempo de implementación: **20 minutos**
Impacto: **Alto (ahorro de miles de USD)**
Riesgo sin fix: **Muy alto (costos incontrolables)**

---

## Siguiente Acción

1. ✅ **Detener servidor** (Ya hecho)
2. ⏳ **Implementar Solución 1** (Cache de tool calls)
3. ⏳ **Testing local**
4. ⏳ **Deploy con monitoreo**
5. ⏳ **Verificar 24h sin duplicados**

---

**Última actualización:** 2025-10-12 18:25 UTC
