from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
from .database import get_db, ScrapingRun, ScrapedJob
from .scheduler_manager import SchedulerManager
from .ai_filter import AIJobFilter
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/admin", tags=["admin"])
scheduler = SchedulerManager()
ai_filter = AIJobFilter()

class ScheduleJobRequest(BaseModel):
    keywords: List[str]
    schedule: str  # Cron expression
    sites: List[str] = ["infojobs", "linkedin", "catho"]
    filters: Optional[Dict] = None

class BlacklistRequest(BaseModel):
    terms: List[str]

@router.post("/schedule-job")
async def schedule_recurring_job(request: ScheduleJobRequest):
    """Agendar scraping recorrente"""
    try:
        job_id = scheduler.add_recurring_job(
            keywords=request.keywords,
            schedule=request.schedule,
            sites=request.sites
        )
        return {"job_id": job_id, "status": "scheduled"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scheduled-jobs")
async def get_scheduled_jobs():
    """Listar jobs agendados"""
    return scheduler.get_active_jobs()

@router.delete("/scheduled-jobs/{job_id}")
async def remove_scheduled_job(job_id: str):
    """Remover job agendado"""
    success = scheduler.remove_job(job_id)
    if success:
        return {"status": "removed"}
    raise HTTPException(status_code=404, detail="Job not found")

@router.post("/blacklist")
async def add_to_blacklist(request: BlacklistRequest):
    """Adicionar termos à blacklist"""
    for term in request.terms:
        ai_filter.blacklist_companies.add(term.lower())
    return {"status": "added", "terms": request.terms}

@router.get("/blacklist")
async def get_blacklist():
    """Ver blacklist atual"""
    return {"blacklist": list(ai_filter.blacklist_companies)}

@router.get("/analytics")
async def get_analytics(db: Session = Depends(get_db)):
    """Analytics avançadas para admin"""
    
    # Estatísticas dos últimos 30 dias
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Jobs por site
    jobs_by_source = db.query(ScrapedJob.source, db.func.count(ScrapedJob.id)).filter(
        ScrapedJob.scraped_at >= thirty_days_ago
    ).group_by(ScrapedJob.source).all()
    
    # Jobs por dia (últimos 7 dias)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    jobs_by_day = db.query(
        db.func.date(ScrapedJob.scraped_at).label('date'),
        db.func.count(ScrapedJob.id).label('count')
    ).filter(
        ScrapedJob.scraped_at >= seven_days_ago
    ).group_by(db.func.date(ScrapedJob.scraped_at)).all()
    
    # Palavras-chave mais buscadas
    popular_keywords = db.query(
        ScrapingRun.keyword,
        db.func.count(ScrapingRun.id).label('searches'),
        db.func.sum(ScrapingRun.jobs_found).label('total_jobs')
    ).filter(
        ScrapingRun.created_at >= thirty_days_ago
    ).group_by(ScrapingRun.keyword).order_by(
        db.func.count(ScrapingRun.id).desc()
    ).limit(10).all()
    
    # Taxa de sucesso
    total_runs = db.query(ScrapingRun).filter(ScrapingRun.created_at >= thirty_days_ago).count()
    successful_runs = db.query(ScrapingRun).filter(
        ScrapingRun.created_at >= thirty_days_ago,
        ScrapingRun.status == 'completed'
    ).count()
    
    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
    
    return {
        "jobs_by_source": dict(jobs_by_source),
        "jobs_by_day": [{"date": str(date), "count": count} for date, count in jobs_by_day],
        "popular_keywords": [
            {"keyword": kw, "searches": searches, "total_jobs": total_jobs}
            for kw, searches, total_jobs in popular_keywords
        ],
        "success_rate": round(success_rate, 2),
        "total_runs": total_runs,
        "successful_runs": successful_runs
    }

@router.get("/quality-report")
async def get_quality_report(db: Session = Depends(get_db)):
    """Relatório de qualidade das vagas"""
    
    # Últimas 100 vagas para análise
    recent_jobs = db.query(ScrapedJob).order_by(
        ScrapedJob.scraped_at.desc()
    ).limit(100).all()
    
    # Simular scores de qualidade
    quality_scores = []
    for job in recent_jobs:
        score = ai_filter._calculate_quality_score({
            'title': job.title,
            'company': '',
            'description': ''
        })
        quality_scores.append({
            'job_id': job.id,
            'title': job.title,
            'source': job.source,
            'quality_score': score,
            'scraped_at': job.scraped_at
        })
    
    # Estatísticas de qualidade
    scores = [q['quality_score'] for q in quality_scores]
    avg_score = sum(scores) / len(scores) if scores else 0
    high_quality = len([s for s in scores if s >= 5])
    low_quality = len([s for s in scores if s <= 2])
    
    return {
        "average_quality_score": round(avg_score, 2),
        "high_quality_jobs": high_quality,
        "low_quality_jobs": low_quality,
        "total_analyzed": len(quality_scores),
        "quality_distribution": {
            "excellent": len([s for s in scores if s >= 8]),
            "good": len([s for s in scores if 5 <= s < 8]),
            "average": len([s for s in scores if 3 <= s < 5]),
            "poor": len([s for s in scores if s < 3])
        }
    }

@router.post("/preset-schedules")
async def setup_preset_schedules():
    """Configurar agendamentos pré-definidos para ONGs"""
    scheduler.add_preset_schedules()
    return {"status": "preset schedules added"}

@router.get("/system-health")
async def get_system_health():
    """Status de saúde do sistema"""
    return {
        "scheduler_running": scheduler.scheduler.running,
        "active_jobs": len(scheduler.get_active_jobs()),
        "cache_stats": ai_filter.blacklist_companies.__len__(),
        "timestamp": datetime.utcnow()
    }