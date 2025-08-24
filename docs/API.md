# 📡 API Documentation

Base URL: `http://localhost:8082`

## 🔍 Scraping Endpoints

### POST /api/scrape
Executa scraping de vagas com filtros avançados.

**Request Body:**
```json
{
  "keywords": ["desenvolvedor java", "python developer"],
  "sites": ["infojobs", "gupy"],
  "days_back": 1,
  "location": "sao-paulo",
  "min_salary": "5000",
  "contract_type": "clt",
  "send_telegram": true
}
```

**Response:**
```json
{
  "run_id": 123,
  "jobs_found": 15,
  "status": "completed"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8082/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["desenvolvedor java"],
    "sites": ["infojobs"],
    "send_telegram": false
  }'
```

## 📊 Data Endpoints

### GET /api/jobs
Lista vagas coletadas com paginação.

**Query Parameters:**
- `limit` (int): Número máximo de vagas (default: 50)
- `offset` (int): Offset para paginação (default: 0)
- `source` (str): Filtrar por fonte (infojobs, gupy)
- `keyword` (str): Filtrar por palavra-chave no título

**Response:**
```json
[
  {
    "id": 1,
    "title": "Desenvolvedor Java Sênior",
    "link": "https://infojobs.com.br/vaga...",
    "source": "InfoJobs",
    "scraped_at": "2025-08-23T22:24:24.293236",
    "sent_to_telegram": 0
  }
]
```

**cURL Example:**
```bash
curl "http://localhost:8082/api/jobs?limit=10&source=infojobs"
```

### GET /api/runs
Lista histórico de execuções de scraping.

**Response:**
```json
[
  {
    "id": 1,
    "keyword": "desenvolvedor java",
    "source": "infojobs",
    "jobs_found": 3,
    "status": "completed",
    "created_at": "2025-08-23T22:04:41.203597",
    "completed_at": "2025-08-23T22:05:01.471047",
    "error_message": null
  }
]
```

### GET /api/stats
Retorna estatísticas gerais do sistema.

**Response:**
```json
{
  "total_jobs": 150,
  "jobs_today": 25,
  "jobs_week": 89,
  "total_runs": 45,
  "successful_runs": 42,
  "cache_stats": {
    "cached_jobs": 120,
    "blacklist_terms": 8
  }
}
```

## 📥 Export Endpoints

### GET /export/csv
Baixa todas as vagas em formato CSV.

**Response:** Arquivo CSV
```csv
Título,Link,Fonte,Data Coleta
Desenvolvedor Java,https://...,InfoJobs,23/08/2025 22:24
```

**cURL Example:**
```bash
curl "http://localhost:8082/export/csv" -o vagas.csv
```

### GET /export/excel
Baixa todas as vagas em formato Excel.

**Response:** Arquivo .xlsx

**cURL Example:**
```bash
curl "http://localhost:8082/export/excel" -o vagas.xlsx
```

### GET /export/json
Baixa todas as vagas em formato JSON.

**Response:**
```json
[
  {
    "title": "Desenvolvedor Java",
    "link": "https://...",
    "source": "InfoJobs",
    "scraped_at": "2025-08-23T22:24:24.293236"
  }
]
```

## 🔧 Management Endpoints

### POST /api/cleanup
Remove dados antigos (mais de 7 dias).

**Response:**
```json
{
  "message": "Cleanup completed",
  "jobs_removed": 45,
  "runs_removed": 12
}
```

### POST /api/blacklist
Adiciona termo à blacklist.

**Request Body:**
```json
{
  "term": "empresa indesejada"
}
```

### GET /api/blacklist
Lista termos na blacklist.

**Response:**
```json
{
  "blacklist": [
    "terceirizada",
    "consultoria generica",
    "empresa fantasma"
  ]
}
```

## 🏥 Health Check

### GET /health
Verifica saúde da aplicação.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-23T22:04:25.704320",
  "version": "2.0.0",
  "database": "connected",
  "selenium": "available"
}
```

## 🔐 Authentication

Atualmente a API não requer autenticação. Para produção, recomenda-se implementar:

- JWT tokens
- API keys
- Rate limiting
- CORS configurado

## 📝 Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters",
  "errors": [
    {
      "field": "keywords",
      "message": "At least one keyword is required"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error": "Selenium driver failed to start"
}
```

## 🚀 Rate Limits

- **Scraping**: Máximo 1 execução por minuto
- **Export**: Máximo 10 downloads por minuto
- **API calls**: Máximo 100 requests por minuto

## 📊 WebSocket (Futuro)

Planejado para v3.0:
```javascript
const ws = new WebSocket('ws://localhost:8082/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'new_job') {
    updateJobsTable(data.job);
  }
};
```