#!/bin/bash

# ========================================
# SCRIPT DE REINICIALIZAÇÃO DA API CRM APOLLO
# ========================================

echo "🔄 Iniciando processo de reinicialização da API..."

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
    print_message "❌ Erro: Arquivo main.py não encontrado. Execute este script no diretório do projeto." $RED
    exit 1
fi

print_message "📍 Diretório atual: $(pwd)" $BLUE

# 1. Parar processos na porta 8000
print_message "🛑 Parando processos na porta 8000..." $YELLOW

# Encontrar PIDs dos processos na porta 8000
PIDS=$(lsof -ti:8000)

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
    
    # Verificar se ainda há processos na porta
    REMAINING_PIDS=$(lsof -ti:8000)
    if [ -z "$REMAINING_PIDS" ]; then
        print_message "✅ Todos os processos na porta 8000 foram finalizados" $GREEN
    else
        print_message "⚠️  Ainda há processos na porta 8000: $REMAINING_PIDS" $YELLOW
    fi
fi

# 2. Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    print_message "❌ Erro: Ambiente virtual 'venv' não encontrado" $RED
    print_message "💡 Execute: python -m venv venv" $BLUE
    exit 1
fi

# 3. Ativar ambiente virtual
print_message "🐍 Ativando ambiente virtual..." $BLUE
source venv/bin/activate

if [ $? -eq 0 ]; then
    print_message "✅ Ambiente virtual ativado" $GREEN
else
    print_message "❌ Erro ao ativar ambiente virtual" $RED
    exit 1
fi

# 4. Verificar se as dependências estão instaladas
print_message "📦 Verificando dependências..." $BLUE

# Verificar se o uvicorn está instalado
if ! python -c "import uvicorn" 2>/dev/null; then
    print_message "⚠️  Uvicorn não encontrado. Instalando dependências..." $YELLOW
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_message "✅ Dependências instaladas com sucesso" $GREEN
    else
        print_message "❌ Erro ao instalar dependências" $RED
        exit 1
    fi
else
    print_message "✅ Dependências verificadas" $GREEN
fi

# 5. Iniciar a aplicação
print_message "🚀 Iniciando aplicação FastAPI..." $GREEN
print_message "🌐 A API estará disponível em: http://localhost:8000" $BLUE
print_message "📚 Documentação: http://localhost:8000/docs" $BLUE
print_message "💚 Health Check: http://localhost:8000/health" $BLUE
print_message "" $NC
print_message "⏹️  Para parar a aplicação, pressione Ctrl+C" $YELLOW
print_message "===========================================" $BLUE

# Iniciar a aplicação com uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Verificar se houve erro ao iniciar
if [ $? -ne 0 ]; then
    print_message "❌ Erro ao iniciar a aplicação" $RED
    exit 1
fi
