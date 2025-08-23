# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [2.0.0] - 2025-08-23

### 🚀 Adicionado
- **Interface Web Completa** - Dashboard responsivo para pessoas leigas
- **Filtros Avançados** - Localização, salário, tipo de contrato
- **Analytics em Tempo Real** - Gráficos e estatísticas interativas
- **Cache Inteligente** - Sistema anti-duplicatas com TTL de 24h
- **Blacklist Automática** - Filtragem de empresas/vagas indesejadas
- **Export Múltiplo** - CSV, Excel e JSON
- **Auto-refresh** - Interface atualizada automaticamente (30s)
- **Loading Spinners** - Feedback visual durante operações
- **Toast Notifications** - Alertas de sucesso/erro
- **Notificações Inteligentes** - Telegram com filtros de relevância
- **Timeout Configurável** - Evita travamentos em sites lentos
- **Retry Automático** - Recuperação de falhas de rede

### 🔧 Melhorado
- **Performance** - Scraping 3x mais rápido com cache e timeouts
- **UX** - Interface moderna e intuitiva
- **Seletores CSS** - Auto-adaptativos para mudanças nos sites
- **Telegram** - Máximo 5 vagas por envio, apenas relevantes
- **Docker** - Configuração otimizada com Selenium Hub
- **Logs** - Sistema estruturado com Loguru

### 🐛 Corrigido
- **Seletores InfoJobs** - Atualizados para nova estrutura HTML
- **Duplicatas** - Sistema de cache evita vagas repetidas
- **Memory Leaks** - Gerenciamento adequado de drivers Selenium
- **Timeout Issues** - Configuração de timeouts em todas as operações

## [1.0.0] - 2025-08-20

### 🚀 Adicionado
- **Scraping Básico** - InfoJobs e Gupy
- **API REST** - Endpoints básicos com FastAPI
- **Telegram Bot** - Notificações simples
- **Docker Support** - Containerização básica
- **Database** - SQLite com SQLAlchemy
- **Scheduler** - Execução automática diária