# 🎬 Uni Creator Bot v2 - Script de Demo

## Estado del Proyecto

**Todo está listo para la demo!** ✅

---

## 1. Infraestructura Verificada

### Base de Datos (Supabase)
- ✅ 3 Creadores registrados
- ✅ 9 Videos generados y listos
- ✅ Métricas funcionando
- ✅ Conexión estable

### API FastAPI
- ✅ Servidor corriendo en puerto 8000
- ✅ AgentKit inicializado correctamente
- ✅ Telegram bot conectado
- ✅ Scheduler de métricas activo (cada 6 horas)

### Endpoints API Funcionando
1. **Health Check**: `http://localhost:8000/health`
2. **Stats**: `http://localhost:8000/api/stats`
3. **Leaderboard**: `http://localhost:8000/api/leaderboard`
4. **Videos**: `http://localhost:8000/api/videos`
5. **Docs**: `http://localhost:8000/docs` (Swagger UI)

### Smart Contracts
- ✅ LeaderboardBetting.sol compilado
- ✅ Configurado para Unichain (chainId: 1301)
- ⚠️ Pendiente despliegue en testnet/mainnet

---

## 2. Datos Actuales

### Estadísticas del Sistema
```json
{
  "total_creators": 3,
  "total_videos": 9,
  "total_posts": 1,
  "top_creator_views": 322,
  "avg_videos_per_creator": 3.0
}
```

### Leaderboard
1. **anthonysurfermx** - 322 vistas, 9 videos, 3 engagements
2. **anawgmi** - 0 vistas, 0 videos
3. **Jardian** - 0 vistas, 0 videos

### Video Real en TikTok
- URL: https://vt.tiktok.com/ZSUkwsTbD/
- Vistas: 322
- Likes: 2
- Shares: 1

---

## 3. Script de Demo (10 minutos)

### PARTE 1: Introducción (2 min)

**"Bienvenidos a Uni Creator Bot v2 - La plataforma completa para campañas UGC con IA"**

**Características principales:**
- Generación de videos con OpenAI Sora 2
- Bot de Telegram con AgentKit (Assistants API)
- Sistema de moderación automática
- Tracking de métricas en redes sociales
- Leaderboard en tiempo real
- Sistema de apuestas en Unichain

---

### PARTE 2: Demo del Bot de Telegram (3 min)

**Abre Telegram y muestra:**

1. **Comando /start**
   ```
   ¡Bienvenido a Uniswap Creator Bot! 🦄
   Crea videos con IA sobre Uniswap
   ```

2. **Comando /create**
   ```
   /create Una persona haciendo swap de tokens en Uniswap
   con efectos futuristas y colores morados
   ```

   **El bot responde:**
   - "Validando tu prompt..." ✅
   - "Generando video con Sora 2..." 🎬
   - "Añadiendo watermark de Uniswap..." 🖼️
   - "Generando caption con GPT-4..." ✍️
   - Envía el video final

3. **Comando /posted**
   ```
   /posted https://tiktok.com/@usuario/video/123456
   ```

   **El bot responde:**
   - "Registrado! Empezaremos a trackear las métricas" 📊

4. **Comando /leaderboard**
   ```
   🏆 Top Creators:
   1. anthonysurfermx - 322 vistas
   2. anawgmi - 0 vistas
   3. Jardian - 0 vistas
   ```

5. **Comando /stats**
   ```
   Tus estadísticas:
   - Videos: 9
   - Vistas totales: 322
   - Engagement rate: 0.93%
   - Ranking: #1
   ```

---

### PARTE 3: API y Frontend Integration (2 min)

**Abre el navegador:**

1. **Swagger UI**
   ```
   http://localhost:8000/docs
   ```
   - Muestra todos los endpoints disponibles
   - Prueba GET /api/videos en vivo

2. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```
   ```json
   {
     "status": "healthy",
     "agent_ready": true,
     "version": "2.0.0"
   }
   ```

3. **Videos Endpoint**
   ```bash
   curl http://localhost:8000/api/videos?limit=3
   ```
   - Muestra los videos con metadata completa
   - URLs de Supabase Storage
   - Métricas de TikTok incluidas

4. **Leaderboard Endpoint**
   ```bash
   curl http://localhost:8000/api/leaderboard
   ```
   - Rankings actualizados
   - Stats por usuario

---

### PARTE 4: Smart Contracts en Unichain (2 min)

**Muestra el código:**

1. **LeaderboardBetting.sol**
   ```solidity
   // Sistema de apuestas semanales
   - Predice top 3 creadores
   - Entry fee: 0.001 ETH
   - Distribución: 55% exact match, 33% two match, 11% one match
   - Merkle proofs para escalabilidad
   ```

2. **Características:**
   - Pausable por el owner
   - ReentrancyGuard
   - Fee splitting (5% protocol, 5% creators)
   - Sistema de refunds si algo falla

3. **Flujo:**
   ```
   openPool() -> placeBet() -> freezePool() -> settlePool() -> claim()
   ```

**Para desplegar:**
```bash
cd betting-pool-contracts
npx hardhat compile
npx hardhat run scripts/deploy.ts --network unichain
```

---

### PARTE 5: Arquitectura y Monitoreo (1 min)

**Diagrama del flujo:**

```
Usuario (Telegram)
    ↓
FastAPI Webhook
    ↓
AgentKit Agent (OpenAI Assistants)
    ↓
┌─────────────────────────────┐
│ Tools (Function Calling)    │
├─────────────────────────────┤
│ • Content Validator (GPT-4) │
│ • Sora 2 Generator          │
│ • FFmpeg Watermarking       │
│ • Caption Generator         │
│ • Social Media Scraping     │
│ • Database Operations       │
└─────────────────────────────┘
    ↓
Supabase DB + Storage
    ↓
APScheduler (cada 6h)
    ↓
Actualizar métricas automáticamente
```

**Monitoreo:**
- Logs en tiempo real: `tail -f bot.log`
- Métricas se actualizan cada 6 horas
- Notificaciones push cuando cambias de ranking

---

## 4. Puntos Destacados para Mencionar

### Innovaciones Técnicas
1. **AgentKit Orchestration**: Uso real de OpenAI Assistants API (no simulado)
2. **Sora 2 Integration**: Generación de videos de 10-60 segundos en HD
3. **Social Scraping**: TikTok, Twitter/X, Instagram metrics tracking
4. **Smart Contracts**: Sistema de betting descentralizado en Unichain
5. **Auto-moderation**: 3-strike system + keyword filtering

### Métricas Reales
- 9 videos generados
- 1 post en TikTok con 322 vistas reales
- Sistema funcionando end-to-end
- API pública lista para frontend

### Escalabilidad
- Supabase: millones de usuarios
- APScheduler: background jobs eficientes
- Merkle proofs: gas-efficient payouts
- CDN-ready: videos en Supabase Storage

---

## 5. Próximos Pasos (Roadmap)

### Corto Plazo (1 semana)
- [ ] Desplegar contratos en Unichain Sepolia
- [ ] Conectar frontend de Lovable
- [ ] Añadir más categorías de contenido
- [ ] Sistema de badges/achievements

### Mediano Plazo (1 mes)
- [ ] Integrar más plataformas (YouTube Shorts, Instagram Reels)
- [ ] Sistema de referidos
- [ ] Challenges semanales temáticos
- [ ] Panel de admin completo

### Largo Plazo (3 meses)
- [ ] Token de gobernanza
- [ ] NFTs de los mejores videos
- [ ] Marketplace de prompts
- [ ] Partnerships con influencers

---

## 6. Comandos Útiles para la Demo

### Iniciar el sistema
```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Ver logs en tiempo real
tail -f bot.log
```

### Probar API
```bash
# Health check
curl http://localhost:8000/health | jq

# Stats
curl http://localhost:8000/api/stats | jq

# Leaderboard
curl http://localhost:8000/api/leaderboard | jq

# Videos
curl 'http://localhost:8000/api/videos?limit=5' | jq
```

### Verificar Base de Datos
```bash
python3 check_db.py
```

### Compilar Contratos
```bash
cd betting-pool-contracts
npx hardhat compile
npx hardhat test
```

---

## 7. FAQs de la Demo

**Q: ¿Los videos son reales o placeholders?**
A: Videos reales generados con Sora 2. Tenemos 9 videos en Supabase Storage.

**Q: ¿El bot funciona con usuarios reales?**
A: Sí, está conectado a Telegram Bot API y acepta comandos en tiempo real.

**Q: ¿Las métricas de TikTok son reales?**
A: Sí, tenemos 1 video con 322 vistas reales verificables en TikTok.

**Q: ¿Cuánto cuesta generar un video?**
A: Aproximadamente $2-5 por video con Sora 2 (dependiendo de duración).

**Q: ¿Puede escalar a miles de usuarios?**
A: Sí, usando Supabase + APScheduler + rate limiting configurables.

**Q: ¿Por qué Unichain para los contratos?**
A: Costos bajos, MEV protection, y alineación con el ecosistema Uniswap.

---

## 8. Contacto y Recursos

**Repositorio:** [GitHub link]
**Documentación:** Ver README.md, API_DOCS.md, QUICKSTART.md
**Demo Video:** [Por crear]
**Telegram Bot:** @UniCreatorBot (ejemplo)

**Equipo:**
- Backend: FastAPI + AgentKit + Sora
- Smart Contracts: Solidity + Hardhat
- Frontend: Lovable (React + TypeScript)

---

## ¡Listo para la Demo! 🚀

**Checklist final:**
- [x] Base de datos funcionando
- [x] API corriendo
- [x] Bot de Telegram activo
- [x] Contratos compilados
- [x] Videos reales en storage
- [x] Métricas de TikTok verificadas
- [x] Documentación completa

**Duración estimada:** 10 minutos
**Público objetivo:** Equipo de Uniswap Labs, stakeholders, inversores
**Impacto esperado:** Demostrar viabilidad técnica y tracción temprana

---

¡A romperla en la demo! 💜🦄
