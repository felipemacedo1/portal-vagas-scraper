#!/bin/bash

# Portal Vagas Scraper - Execução Local (Ubuntu)

echo "🚀 Portal Vagas Scraper - Setup"

# Verificar se Python 3.11+ está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instalando..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Verificar se Chrome está instalado
if ! command -v google-chrome &> /dev/null; then
    echo "🌐 Instalando Google Chrome..."
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt update
    sudo apt install -y google-chrome-stable
fi

# Instalar ChromeDriver
echo "🔧 Configurando ChromeDriver..."
pip install webdriver-manager

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Copiando exemplo..."
    cp .env.example .env
    echo "📝 Configure as variáveis em .env antes de continuar"
    exit 1
fi

# Criar diretórios necessários
mkdir -p logs data

echo "✅ Setup concluído!"
echo ""
echo "🔧 Próximos passos:"
echo "1. Configure as variáveis no arquivo .env"
echo "2. Execute: python main.py (API)"
echo "3. Execute: python scheduler.py (Agendador)"
echo ""
echo "🐳 Ou use Docker: docker-compose up -d"