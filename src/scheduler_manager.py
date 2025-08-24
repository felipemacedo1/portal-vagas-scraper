from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from loguru import logger
from .scraper import JobScraper
from .telegram_bot import TelegramNotifier
import asyncio

class SchedulerManager:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scraper = JobScraper()
        self.notifier = TelegramNotifier()
        self.active_jobs = []
        
    def start(self):
        """Inicia o scheduler"""
        self.scheduler.start()
        logger.info("Scheduler iniciado")
    
    def stop(self):
        """Para o scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler parado")
    
    def add_recurring_job(self, keywords: list, schedule: str, sites: list = None):
        """Adiciona job recorrente
        
        Args:
            keywords: Lista de palavras-chave
            schedule: Cron expression (ex: '0 9 * * *' para 9h todo dia)
            sites: Lista de sites para buscar
        """
        if not sites:
            sites = ['infojobs', 'linkedin', 'catho']
            
        job_id = f"job_{len(self.active_jobs)}"
        
        self.scheduler.add_job(
            func=self._execute_scraping,
            trigger=CronTrigger.from_crontab(schedule),
            args=[keywords, sites],
            id=job_id,
            name=f"Scraping: {', '.join(keywords)}"
        )
        
        self.active_jobs.append({
            'id': job_id,
            'keywords': keywords,
            'schedule': schedule,
            'sites': sites,
            'created_at': datetime.now()
        })
        
        logger.info(f"Job agendado: {job_id} - {schedule}")
        return job_id
    
    def remove_job(self, job_id: str):
        """Remove job agendado"""
        try:
            self.scheduler.remove_job(job_id)
            self.active_jobs = [j for j in self.active_jobs if j['id'] != job_id]
            logger.info(f"Job removido: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover job {job_id}: {e}")
            return False
    
    def get_active_jobs(self):
        """Retorna jobs ativos"""
        return self.active_jobs
    
    async def _execute_scraping(self, keywords: list, sites: list):
        """Executa scraping agendado"""
        try:
            logger.info(f"Executando scraping agendado: {keywords}")
            
            all_jobs = []
            for keyword in keywords:
                for site in sites:
                    if site == 'infojobs':
                        jobs = self.scraper.scrape_infojobs(keyword)
                        all_jobs.extend(jobs)
            
            if all_jobs:
                # Enviar para Telegram
                for keyword in keywords:
                    keyword_jobs = [j for j in all_jobs if keyword.lower() in j['title'].lower()]
                    if keyword_jobs:
                        self.notifier.send_jobs(keyword_jobs[:5], keyword)
                
                logger.info(f"Scraping concluído: {len(all_jobs)} vagas encontradas")
            else:
                logger.info("Nenhuma vaga nova encontrada")
                
        except Exception as e:
            logger.error(f"Erro no scraping agendado: {e}")
    
    def add_preset_schedules(self):
        """Adiciona agendamentos pré-definidos para ONGs"""
        
        # Vagas de TI - 3x por dia
        self.add_recurring_job(
            keywords=['desenvolvedor', 'programador', 'analista sistemas'],
            schedule='0 9,14,18 * * *',  # 9h, 14h, 18h
            sites=['infojobs', 'linkedin']
        )
        
        # Vagas administrativas - 2x por dia  
        self.add_recurring_job(
            keywords=['assistente administrativo', 'auxiliar administrativo', 'recepcionista'],
            schedule='0 10,16 * * *',  # 10h, 16h
            sites=['infojobs', 'catho']
        )
        
        # Vagas de vendas - 1x por dia
        self.add_recurring_job(
            keywords=['vendedor', 'consultor vendas', 'representante comercial'],
            schedule='0 11 * * *',  # 11h
            sites=['infojobs']
        )
        
        logger.info("Agendamentos pré-definidos adicionados")