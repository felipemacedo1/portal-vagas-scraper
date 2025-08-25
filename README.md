# 🚀 Portal Vagas Scraper

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema avançado de scraping automatizado para coleta de vagas de emprego, integrado ao Portal de Vagas. Desenvolvido para admins coletarem vagas e enviarem para grupos com interface web amigável.

## ✨ Funcionalidades

### 🎯 **Core Features**
- ✅ **Scraping Inteligente** - InfoJobs, Gupy com seletores auto-adaptativos
- ✅ **Interface Web Responsiva** - Dashboard completo para pessoas leigas
- ✅ **Filtros Avançados** - Localização, salário, tipo de contrato, senioridade
- ✅ **Cache Inteligente** - Evita duplicatas e spam
- ✅ **Notificações Telegram** - Apenas vagas relevantes (máx 5 por envio)

### 📊 **Analytics & Monitoring**
- ✅ **Dashboard em Tempo Real** - Estatísticas e gráficos interativos
- ✅ **Auto-refresh** - Interface atualizada automaticamente (30s)
- ✅ **Métricas Avançadas** - Vagas por dia/semana, sites mais produtivos
- ✅ **Histórico Completo** - Todas as execuções e resultados

### 📥 **Export Múltiplo**
- ✅ **CSV** - Formato padrão para análise
- ✅ **Excel** - Planilha formatada com estilos
- ✅ **JSON** - Para integração com outros sistemas

### ⚡ **Performance & UX**
- ✅ **Loading Spinners** - Feedback visual durante scraping
- ✅ **Toast Notifications** - Alertas de sucesso/erro
- ✅ **Blacklist Automática** - Filtra empresas/vagas indesejadas
- ✅ **Timeout Configurável** - Evita travamentos
- ✅ **Retry Automático** - Recuperação de falhas

## 🌐 Links

🔗 **Repositório**: [github.com/felipemacedo1/portal-vagas-scraper](https://github.com/felipemacedo1/portal-vagas-scraper)
📚 **Documentação**:
  - **API Interativa**: `http://localhost:8081/docs` (Swagger UI)
  - **API Reference**: [docs/API.md](docs/API.md)
  - **Screenshots**: [docs/SCREENSHOTS.md](docs/SCREENSHOTS.md)
  - **Deploy Guide**: [DEPLOY.md](DEPLOY.md)
📊 **Dashboard**: `http://localhost:8081` (interface principal)

## 🐳 Instalação Rápida (Docker)

```bash
# Clone o repositório
git clone https://github.com/felipemacedo1/portal-vagas-scraper.git
cd portal-vagas-scraper

# Configure variáveis
cp .env.example .env
# Edite o .env com suas configurações

# Execute com Docker
docker-compose up -d

# Acesse a interface
open http://localhost:8081
```

## 🐧 Instalação Ubuntu/Linux

```bash
# Execute o script de setup
./run.sh

# Configure o .env
nano .env

# Execute manualmente
python main.py
```

## ⚙️ Configuração

### 📋 Variáveis de Ambiente (.env)

```env
# Database
DATABASE_URL=sqlite:///data/scraper.db

# Telegram Bot (Opcional)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Scraping Config
CHROME_HEADLESS=true
SCRAPING_DELAY=2
MAX_JOBS_PER_RUN=20
SELENIUM_HUB_URL=http://chrome:4444/wd/hub

# API Config
API_PORT=8081
API_HOST=0.0.0.0
API_SECRET_KEY=your_secret_key_here
```

### 🤖 Configurar Telegram Bot

1. **Criar Bot**: Fale com [@BotFather](https://t.me/botfather)
2. **Obter Token**: `/newbot` → nome do bot → username
3. **Obter Chat ID**: Adicione bot ao grupo → `/start`
4. **Configurar**: Adicione token e chat_id no `.env`

## 🎯 Como Usar

### 🌐 Interface Web (Recomendado)

1. **Acesse**: http://localhost:8081
2. **Digite** palavra-chave (ex: "desenvolvedor java")
3. **Configure** filtros (localização, salário, etc.)
4. **Clique** "🔍 Buscar"
5. **Baixe** resultados em CSV/Excel
6. **Monitore** estatísticas em tempo real

### 📡 API REST

```bash
# Executar scraping
curl -X POST "http://localhost:8081/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["desenvolvedor java"],
    "sites": ["infojobs"],
    "location": "sao-paulo",
    "send_telegram": true
  }'

# Listar vagas
curl "http://localhost:8081/api/jobs"

# Exportar CSV
curl "http://localhost:8081/export/csv" -o vagas.csv

# Documentação completa
open http://localhost:8081/docs
```

## 🏗️ Arquitetura

```
portal-vagas-scraper/
├── src/
│   ├── scraper.py          # Engine de scraping otimizado
│   ├── telegram_bot.py     # Notificações inteligentes
│   ├── database.py         # Modelos SQLAlchemy
│   ├── api.py             # FastAPI endpoints
│   ├── web.py             # Interface web
│   ├── cache.py           # Sistema de cache
│   └── exports.py         # Múltiplos formatos
├── templates/
│   └── dashboard.html     # Interface responsiva
├── docker-compose.yml     # Orquestração completa
├── Dockerfile            # Container otimizado
└── requirements.txt      # Dependências Python
```

## 🔧 Tecnologias

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Scraping**: Selenium WebDriver, Chrome Headless
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Containerização**: Docker, Docker Compose
- **Notificações**: Telegram Bot API
- **Exports**: CSV, Excel (openpyxl), JSON

## 📈 Melhorias Implementadas

### 🎯 **Filtros Avançados**
- Localização (São Paulo, Rio, Remoto)
- Salário mínimo (R$ 3k, 5k, 8k+)
- Tipo de contrato (CLT, PJ, Estágio)
- Dias de busca (1, 3, 7 dias)

### 🧠 **Inteligência Artificial**
- **Cache Inteligente**: Evita vagas duplicadas (24h)
- **Blacklist Automática**: Filtra empresas indesejadas
- **Relevância**: Prioriza vagas com palavra-chave no título
- **Limite Inteligente**: Máximo 5 vagas por notificação

### 📊 **Analytics Avançadas**
- Gráfico de vagas por dia (Chart.js)
- Estatísticas em tempo real
- Métricas de performance
- Histórico completo de execuções

### ⚡ **Performance**
- Timeout configurável (10s)
- Retry automático em falhas
- Scraping paralelo (ThreadPoolExecutor)
- Cache de elementos DOM

## 🚀 Roadmap

- [ ] **Multi-sites**: LinkedIn, Catho, Vagas.com
- [ ] **IA Avançada**: Classificação automática de vagas
- [ ] **Webhooks**: Integração com Slack, Discord
- [ ] **Mobile App**: React Native
- [ ] **Machine Learning**: Predição de relevância

## 🤝 Contribuição

1. **Fork** o projeto
2. **Crie** uma branch (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Felipe Macedo**
- GitHub: [@felipemacedo1](https://github.com/felipemacedo1)
- LinkedIn: [Felipe Macedo](https://linkedin.com/in/felipemacedo1)

## 🙏 Agradecimentos

- **Portal de Vagas** - Projeto base
- **Selenium** - Web scraping
- **FastAPI** - Framework web moderno
- **Chart.js** - Gráficos interativos

---

⭐ **Se este projeto te ajudou, deixe uma estrela!** ⭐