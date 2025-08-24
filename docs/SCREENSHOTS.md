# 📸 Screenshots

## 🏠 Dashboard Principal

![Dashboard](https://raw.githubusercontent.com/felipemacedo1/portal-vagas-scraper/main/docs/images/dashboard.png)

**Funcionalidades:**
- ✅ Estatísticas em tempo real
- ✅ Gráfico de vagas por dia
- ✅ Auto-refresh automático
- ✅ Interface responsiva

## 🔍 Formulário de Busca

![Busca](https://raw.githubusercontent.com/felipemacedo1/portal-vagas-scraper/main/docs/images/search-form.png)

**Filtros Disponíveis:**
- 🎯 Palavra-chave
- 🌐 Site (InfoJobs, Gupy)
- 📅 Período (1, 3, 7 dias)
- 📍 Localização
- 💰 Salário mínimo
- 📋 Tipo de contrato

## 📊 Resultados e Tabelas

![Resultados](https://raw.githubusercontent.com/felipemacedo1/portal-vagas-scraper/main/docs/images/results.png)

**Informações Exibidas:**
- 📝 Título da vaga
- 🏢 Fonte (InfoJobs/Gupy)
- 📅 Data de coleta
- 🔗 Link direto para aplicação

## 📱 Versão Mobile

![Mobile](https://raw.githubusercontent.com/felipemacedo1/portal-vagas-scraper/main/docs/images/mobile.png)

**Características:**
- ✅ Layout adaptativo
- ✅ Formulário empilhado
- ✅ Tabelas responsivas
- ✅ Touch-friendly

## 🤖 Notificações Telegram

**Formato da Mensagem:**
```
🚀 3 NOVAS VAGAS - DESENVOLVEDOR JAVA

1. **Desenvolvedor Java Sênior**
📅 23/08/2025 | 🌐 InfoJobs
🔗 https://infojobs.com.br/vaga...

2. **Java Developer - Remoto**
📅 23/08/2025 | 🌐 InfoJobs
🔗 https://infojobs.com.br/vaga...
```

## 📥 Exports

### CSV Export
```csv
Título,Link,Fonte,Data Coleta
Desenvolvedor Java Sênior,https://...,InfoJobs,23/08/2025 14:30
Java Developer - Remoto,https://...,InfoJobs,23/08/2025 14:30
```

## 🔧 API Documentation

**Acesso:** `http://localhost:8082/docs`

**Endpoints Principais:**
- `POST /api/scrape` - Executar scraping
- `GET /api/jobs` - Listar vagas
- `GET /api/runs` - Histórico de execuções
- `GET /export/csv` - Download CSV