#!/bin/bash

# ========================================
# SCRIPT DE REINICIALIZAÇÃO PARA DOCKER
# ========================================

echo "🔄 Iniciando aplicação CRM Apollo API no Docker..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    echo -e "${2}${1}${NC}"
}

# Verificar se estamos no diretório correto
if [ ! -f "main.py" ]; then
    print_message "❌ Erro: Arquivo main.py não encontrado." $RED
    exit 1
fi

print_message "📍 Diretório atual: $(pwd)" $BLUE

# 1. Parar processos na porta 8000 (se existirem)
print_message "🛑 Verificando processos na porta 8000..." $YELLOW

# Encontrar PIDs dos processos na porta 8000
PIDS=$(lsof -ti:8000 2>/dev/null || echo "")

if [ -z "$PIDS" ]; then
    print_message "ℹ️  Nenhum processo encontrado na porta 8000" $BLUE
else
    print_message "🔍 Processos encontrados na porta 8000: $PIDS" $BLUE
    
    # Matar os processos
    for PID in $PIDS; do
        print_message "💀 Matando processo $PID..." $YELLOW
        kill -9 $PID 2>/dev/null
    done
    
    # Aguardar um pouco para garantir que os processos foram finalizados
    sleep 2
fi

# 2. Verificar se as dependências estão disponíveis
print_message "📦 Verificando dependências Python..." $BLUE

# Verificar se o uvicorn está disponível
if ! python -c "import uvicorn" 2>/dev/null; then
    print_message "❌ Erro: uvicorn não encontrado" $RED
    exit 1
fi

print_message "✅ Dependências verificadas" $GREEN

# 3. Iniciar a aplicação
print_message "🚀 Iniciando aplicação FastAPI..." $GREEN
print_message "🌐 A API estará disponível em: http://localhost:8000" $BLUE
print_message "📚 Documentação: http://localhost:8000/docs" $BLUE
print_message "💚 Health Check: http://localhost:8000/health" $BLUE
print_message "" $NC
print_message "===========================================" $BLUE

# Iniciar a aplicação com uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
