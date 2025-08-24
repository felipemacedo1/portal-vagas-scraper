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
from datetime import datetime
from loguru import logger
import os

app = FastAPI(title="Portal Vagas Scraper API", version="1.0.0")
add_web_routes(app)

# Inicializar componentes inteligentes
smart_scheduler = SmartScheduler()
search_manager = AutoSearchManager()

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
            
            # Save jobs to database
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