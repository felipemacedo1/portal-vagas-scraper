from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .auto_search_manager import AutoSearchManager
from .scraper import JobScraper
from .telegram_bot import TelegramNotifier
from loguru import logger
import asyncio

class SmartScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.search_manager = AutoSearchManager()
        self.scraper = JobScraper()
        self.notifier = TelegramNotifier()
        
    def setup_automated_searches(self):
        """Configura todas as buscas automatizadas"""
        search_matrix = self.search_manager.get_search_matrix()
        
        # Agrupar por horário para otimizar
        schedule_groups = {}
        for search in search_matrix:
            schedule = search['schedule']
            if schedule not in schedule_groups:
                schedule_groups[schedule] = []
            schedule_groups[schedule].append(search)
        
        # Criar jobs agrupados
        for schedule, searches in schedule_groups.items():
            job_id = f"auto_search_{schedule.replace(' ', '_').replace('*', 'x')}"
            
            self.scheduler.add_job(
                func=self._execute_batch_search,
                trigger='cron',
                **self._parse_cron(schedule),
                args=[searches],
                id=job_id,
                max_instances=1
            )
            
        logger.info(f"Configuradas {len(schedule_groups)} buscas automatizadas")
    
    def _parse_cron(self, cron_expr: str) -> dict:
        """Converte cron expression para parâmetros do scheduler"""
        parts = cron_expr.split()
        return {
            'minute': parts[0],
            'hour': parts[1], 
            'day': parts[2],
            'month': parts[3],
            'day_of_week': parts[4]
        }
    
    async def _execute_batch_search(self, searches: list):
        """Executa lote de buscas em paralelo"""
        logger.info(f"Executando {len(searches)} buscas automatizadas")
        
        # Agrupar por prioridade
        high_priority = [s for s in searches if s['priority'] >= 4]
        normal_priority = [s for s in searches if s['priority'] < 4]
        
        # Executar alta prioridade primeiro
        if high_priority:
            await self._run_searches(high_priority)
            
        # Executar prioridade normal com delay
        if normal_priority:
            await asyncio.sleep(30)  # Evitar sobrecarga
            await self._run_searches(normal_priority)
    
    async def _run_searches(self, searches: list):
        """Executa grupo de buscas"""
        tasks = []
        
        for search in searches:
            task = asyncio.create_task(
                self._single_search(search['keyword'], search['region'])
            )
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        all_jobs = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Erro na busca {searches[i]}: {result}")
            else:
                all_jobs.extend(result)
        
        # Enviar melhores vagas para Telegram
        if all_jobs:
            best_jobs = sorted(all_jobs, key=lambda x: x.get('quality_score', 0), reverse=True)[:10]
            await self._send_batch_notification(best_jobs)
    
    async def _single_search(self, keyword: str, region: str) -> list:
        """Executa busca única"""
        try:
            filters = {'location': region, 'min_salary': 2000}
            jobs = self.scraper.scrape_all_sites(keyword, filters=filters)
            logger.info(f"'{keyword}' em '{region}': {len(jobs)} vagas")
            return jobs
        except Exception as e:
            logger.error(f"Erro buscando '{keyword}' em '{region}': {e}")
            return []
    
    async def _send_batch_notification(self, jobs: list):
        """Envia notificação consolidada"""
        if len(jobs) >= 5:  # Só enviar se tiver vagas suficientes
            message = f"🎯 **BUSCA AUTOMATIZADA - {len(jobs)} VAGAS SELECIONADAS**\n\n"
            
            for i, job in enumerate(jobs[:5], 1):
                message += f"{i}. **{job['title']}**\n"
                message += f"📍 {job.get('location', 'N/A')} | 🏢 {job.get('company', 'N/A')}\n"
                message += f"⭐ Score: {job.get('quality_score', 0)} | 🌐 {job['source']}\n"
                message += f"🔗 {job['link']}\n\n"
            
            self.notifier._send_message(message)
    
    def start(self):
        """Inicia scheduler inteligente"""
        self.setup_automated_searches()
        self.scheduler.start()
        logger.info("Smart Scheduler iniciado")
    
    def get_next_searches(self) -> list:
        """Próximas buscas agendadas"""
        jobs = self.scheduler.get_jobs()
        return [
            {
                'id': job.id,
                'next_run': job.next_run_time,
                'searches_count': len(job.args[0]) if job.args else 0
            }
            for job in jobs
        ]