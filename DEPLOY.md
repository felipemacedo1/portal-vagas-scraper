# 🚀 Deploy Guide

## GitHub Repository

Para fazer o deploy no GitHub:

```bash
# 1. Criar repositório no GitHub
# Acesse: https://github.com/new
# Nome: portal-vagas-scraper
# Descrição: 🚀 Sistema avançado de scraping de vagas com interface web, filtros inteligentes e notificações Telegram

# 2. Configurar remote
git remote set-url origin https://github.com/felipemacedo1/portal-vagas-scraper.git

# 3. Push inicial
git push -u origin main
```

## 🐳 Deploy com Docker

### Produção
```bash
# 1. Clone o repositório
git clone https://github.com/felipemacedo1/portal-vagas-scraper.git
cd portal-vagas-scraper

# 2. Configure produção
cp .env.example .env.prod
# Edite .env.prod com configurações de produção

# 3. Execute
docker-compose -f docker-compose.yml --env-file .env.prod up -d
```

### Desenvolvimento
```bash
# Execute localmente
docker-compose up -d
```

## ☁️ Deploy na Nuvem

### AWS EC2
```bash
# 1. Instalar Docker
sudo apt update
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker $USER

# 2. Clone e execute
git clone https://github.com/felipemacedo1/portal-vagas-scraper.git
cd portal-vagas-scraper
cp .env.example .env
# Configure .env
docker-compose up -d

# 3. Configurar nginx (opcional)
sudo apt install nginx -y
# Configure proxy reverso para porta 8082
```

### DigitalOcean Droplet
```bash
# Mesmo processo do AWS EC2
# Recomendado: Droplet com 2GB RAM mínimo
```

### Heroku
```bash
# 1. Instalar Heroku CLI
# 2. Login
heroku login

# 3. Criar app
heroku create portal-vagas-scraper

# 4. Configurar variáveis
heroku config:set DATABASE_URL=postgres://...
heroku config:set TELEGRAM_BOT_TOKEN=...

# 5. Deploy
git push heroku main
```

## 🔧 Configurações de Produção

### .env.prod
```env
# Database (PostgreSQL recomendado)
DATABASE_URL=postgresql://user:pass@db:5432/portal_vagas

# Telegram
TELEGRAM_BOT_TOKEN=your_production_token
TELEGRAM_CHAT_ID=your_production_chat

# Security
API_SECRET_KEY=your_super_secret_key_here

# Performance
CHROME_HEADLESS=true
SCRAPING_DELAY=3
MAX_JOBS_PER_RUN=50

# Monitoring
LOG_LEVEL=INFO
```

### docker-compose.prod.yml
```yaml
version: '3.8'
services:
  scraper-api:
    build: .
    ports:
      - "80:8082"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    restart: unless-stopped
    
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: portal_vagas
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASS}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## 📊 Monitoramento

### Logs
```bash
# Ver logs em tempo real
docker-compose logs -f scraper-api

# Logs específicos
docker logs portal-vagas-scraper --tail 100
```

### Health Check
```bash
# Verificar saúde da aplicação
curl http://localhost:8082/health

# Métricas
curl http://localhost:8082/api/stats
```

## 🔒 Segurança

### Firewall
```bash
# Permitir apenas portas necessárias
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### SSL/HTTPS
```bash
# Certbot para SSL gratuito
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

## 🚀 CI/CD

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          # Script de deploy automático
```

## 📈 Escalabilidade

### Load Balancer
- Nginx como proxy reverso
- Múltiplas instâncias da aplicação
- Redis para cache compartilhado

### Database
- PostgreSQL com replicação
- Backup automático
- Índices otimizados

## 🆘 Troubleshooting

### Problemas Comuns
```bash
# Container não inicia
docker-compose logs scraper-api

# Selenium não conecta
docker-compose restart chrome

# Banco não conecta
docker-compose restart postgres

# Limpar tudo e reiniciar
docker-compose down -v
docker-compose up -d
```