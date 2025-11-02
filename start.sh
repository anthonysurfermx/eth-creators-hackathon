#!/bin/bash

# 🚀 Start Script para Uniswap Creator Bot
# Este script activa el entorno virtual y arranca el bot

echo "🦄 Uniswap Creator Bot - Starting..."
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: app.py not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Verificar que existe el venv
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
    echo ""
fi

# Activar venv
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Verificar dependencias
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dependencies not installed${NC}"
    echo "Installing dependencies..."
    python -m pip install -r requirements.txt
    echo ""
fi

# Verificar .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create .env file with your credentials"
    echo "See CREDENTIALS_GUIDE.md for instructions"
    exit 1
fi

# Verificar credenciales críticas
if grep -q "your-openai-api-key-here" .env; then
    echo -e "${YELLOW}⚠️  Warning: OpenAI API key not configured${NC}"
    echo "Edit .env and add your OpenAI API key"
    echo ""
fi

if grep -q "your-telegram-bot-token-here" .env; then
    echo -e "${YELLOW}⚠️  Warning: Telegram bot token not configured${NC}"
    echo "Edit .env and add your Telegram bot token"
    echo ""
fi

# Exportar PATH para PostgreSQL (necesario para psycopg2)
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"

echo -e "${GREEN}✅ Environment ready${NC}"
echo ""
echo "🚀 Starting Uniswap Creator Bot..."
echo "📍 Server will run on: http://localhost:8000"
echo "📖 API docs: http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop"
echo ""
echo "============================================"
echo ""

# Arrancar el bot
uvicorn app:app --reload --host 0.0.0.0 --port 8000
