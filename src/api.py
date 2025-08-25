from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from .scraper import JobScraper
from .telegram_bot import TelegramNotifier
from .database import get_db, ScrapingRun, ScrapedJob, init_db
from .web import add_web_routes
from .smart_scheduler import SmartScheduler
from .auto_search_manager import AutoSearchManager
from .portal_integration import PortalIntegration
from .approval_system import ApprovalSystem, PendingJob
from datetime import datetime
from loguru import logger
import os

app = FastAPI(title="Portal Vagas Scraper API", version="1.0.0")
add_web_routes(app)

# Inicializar componentes inteligentes
smart_scheduler = SmartScheduler()
search_manager = AutoSearchManager()
portal_integration = PortalIntegration()
approval_system = ApprovalSystem()

class ScrapeRequest(BaseModel):
    sites: List[str] = ["infojobs"]
    keywords: List[str]
    days_back: int = 1
    send_telegram: bool = True

class ScrapeResponse(BaseModel):
    run_id: int
    jobs_found: int
    status: str

@app.on_event("startup")
async def startup_event():
    init_db()
    smart_scheduler.start()  # Iniciar buscas automatizadas
    logger.info("API started with automated searches")

@app.post("/api/scrape", response_model=ScrapeResponse)
async def scrape_jobs(request: ScrapeRequest, db: Session = Depends(get_db)):
    scraper = JobScraper()
    notifier = TelegramNotifier()
    all_jobs = []
    
    for keyword in request.keywords:
        # Create run record
        run = ScrapingRun(
            keyword=keyword,
            source=",".join(request.sites),
            status="running"
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        
        try:
            jobs = []
            if "infojobs" in request.sites:
                jobs.extend(scraper.scrape_infojobs(keyword, request.days_back))
            
            # Save jobs to database and approval system
            new_jobs = []
            for job in jobs:
                existing = db.query(ScrapedJob).filter(ScrapedJob.link == job['link']).first()
                if not existing:
                    scraped_job = ScrapedJob(
                        title=job['title'],
                        link=job['link'],
                        source=job['source']
                    )
                    db.add(scraped_job)
                    new_jobs.append(job)
            
            db.commit()
            
            # Adicionar para sistema de aprovação
            if new_jobs:
                approval_result = approval_system.add_jobs_for_review(new_jobs, db)
                logger.info(f"Aprovação: {approval_result}")
            
            all_jobs.extend(new_jobs)
            
            # Update run status
            run.jobs_found = len(new_jobs)
            run.status = "completed"
            run.completed_at = datetime.utcnow()
            db.commit()
            
            # Send to Telegram
            if request.send_telegram and new_jobs:
                notifier.send_jobs(new_jobs, keyword)
                
        except Exception as e:
            run.status = "failed"
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            db.commit()
            logger.error(f"Scraping failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return ScrapeResponse(
        run_id=run.id,
        jobs_found=len(all_jobs),
        status="completed"
    )

@app.get("/api/runs")
async def get_runs(db: Session = Depends(get_db)):
    runs = db.query(ScrapingRun).order_by(ScrapingRun.created_at.desc()).limit(50).all()
    return runs

@app.get("/api/jobs")
async def get_jobs(limit: int = 50, db: Session = Depends(get_db)):
    jobs = db.query(ScrapedJob).order_by(ScrapedJob.scraped_at.desc()).limit(limit).all()
    return jobs

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/auto-searches")
async def get_automated_searches():
    """Ver matriz de buscas automatizadas"""
    return {
        "search_matrix": search_manager.get_search_matrix(),
        "regional_stats": search_manager.get_regional_stats(),
        "next_executions": smart_scheduler.get_next_searches()
    }

@app.post("/api/auto-searches/add")
async def add_custom_search(keywords: List[str], regions: List[str], schedule: str, priority: int = 3):
    """Adicionar busca personalizada"""
    profile_id = search_manager.add_custom_profile(keywords, regions, schedule, priority)
    smart_scheduler.setup_automated_searches()  # Reconfigurar
    return {"profile_id": profile_id, "status": "added"}

@app.post("/api/auto-searches/execute-now")
async def execute_high_priority_now():
    """Executar buscas de alta prioridade imediatamente"""
    searches = search_manager.get_high_priority_searches()
    await smart_scheduler._execute_batch_search(searches)
    return {"executed_searches": len(searches), "status": "completed"}

@app.post("/api/portal-integration/send-jobs")
async def send_jobs_to_portal(job_ids: List[int] = None, auto_approve: bool = False, db: Session = Depends(get_db)):
    """Enviar vagas aprovadas para o portal principal"""
    if job_ids:
        # Enviar vagas específicas
        jobs_data = []
        for job_id in job_ids:
            job = db.query(PendingJob).filter(PendingJob.id == job_id).first()
            if job and job.status == "approved":
                jobs_data.append({
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'source': job.source,
                    'link': job.link,
                    'quality_score': job.quality_score
                })
    else:
        # Enviar todas as vagas aprovadas
        approved_jobs = approval_system.get_approved_jobs(db)
        jobs_data = [{
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'source': job.source,
            'link': job.link,
            'quality_score': job.quality_score
        } for job in approved_jobs]
    
    result = portal_integration.send_jobs_to_portal(jobs_data, auto_approve)
    return result

@app.get("/api/approval/pending")
async def get_pending_jobs(limit: int = 50, db: Session = Depends(get_db)):
    """Listar vagas pendentes de aprovação"""
    jobs = approval_system.get_pending_jobs(db, limit)
    return [{
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'source': job.source,
        'link': job.link,
        'quality_score': job.quality_score,
        'scraped_at': job.scraped_at
    } for job in jobs]

@app.post("/api/approval/approve")
async def approve_jobs(job_ids: List[int], reviewer: str = "admin", db: Session = Depends(get_db)):
    """Aprovar vagas em lote"""
    result = approval_system.approve_jobs(job_ids, reviewer, db)
    return result

@app.post("/api/approval/reject")
async def reject_jobs(job_ids: List[int], reason: str, reviewer: str = "admin", db: Session = Depends(get_db)):
    """Rejeitar vagas em lote"""
    result = approval_system.reject_jobs(job_ids, reason, reviewer, db)
    return result

@app.get("/api/approval/stats")
async def get_approval_stats(db: Session = Depends(get_db)):
    """Estatísticas do sistema de aprovação"""
    return approval_system.get_approval_stats(db)