from fastapi import Request, Depends, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from .database import get_db, ScrapingRun, ScrapedJob
from .scraper import JobScraper
from .telegram_bot import TelegramNotifier
from datetime import datetime, timedelta
import csv
import io
import json
from concurrent.futures import ThreadPoolExecutor

templates = Jinja2Templates(directory="templates")

def add_web_routes(app):
    
    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request, db: Session = Depends(get_db)):
        recent_runs = db.query(ScrapingRun).order_by(ScrapingRun.created_at.desc()).limit(10).all()
        recent_jobs = db.query(ScrapedJob).order_by(ScrapedJob.scraped_at.desc()).limit(20).all()
        
        # Analytics avançadas
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        stats = {
            'total_jobs': db.query(ScrapedJob).count(),
            'total_runs': db.query(ScrapingRun).count(),
            'successful_runs': db.query(ScrapingRun).filter(ScrapingRun.status == 'completed').count(),
            'jobs_today': db.query(ScrapedJob).filter(func.date(ScrapedJob.scraped_at) == today).count(),
            'jobs_week': db.query(ScrapedJob).filter(func.date(ScrapedJob.scraped_at) >= week_ago).count()
        }
        
        # Dados para gráficos
        daily_stats = db.query(
            func.date(ScrapedJob.scraped_at).label('date'),
            func.count(ScrapedJob.id).label('count')
        ).filter(func.date(ScrapedJob.scraped_at) >= week_ago).group_by(func.date(ScrapedJob.scraped_at)).all()
        
        chart_data = {
            'labels': [str(stat.date) for stat in daily_stats],
            'data': [stat.count for stat in daily_stats]
        }
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "stats": stats,
            "recent_runs": recent_runs,
            "recent_jobs": recent_jobs,
            "chart_data": json.dumps(chart_data)
        })
    
    @app.post("/scrape", response_class=HTMLResponse)
    async def web_scrape(
        request: Request,
        keyword: str = Form(...),
        site: str = Form("infojobs"),
        days: int = Form(1),
        location: str = Form(""),
        min_salary: str = Form(""),
        contract_type: str = Form(""),
        send_telegram: bool = Form(False),
        db: Session = Depends(get_db)
    ):
        scraper = JobScraper()
        notifier = TelegramNotifier()
        
        run = ScrapingRun(keyword=keyword, source=site, status="running")
        db.add(run)
        db.commit()
        db.refresh(run)
        
        try:
            jobs = scraper.scrape_infojobs(keyword, days)
            
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
            
            run.jobs_found = len(new_jobs)
            run.status = "completed"
            run.completed_at = datetime.utcnow()
            db.commit()
            
            if send_telegram and new_jobs:
                notifier.send_jobs(new_jobs, keyword)
                
            message = f"✅ Encontradas {len(new_jobs)} vagas novas para '{keyword}'"
            
        except Exception as e:
            run.status = "failed"
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            db.commit()
            message = f"❌ Erro: {str(e)}"
        
        recent_runs = db.query(ScrapingRun).order_by(ScrapingRun.created_at.desc()).limit(10).all()
        recent_jobs = db.query(ScrapedJob).order_by(ScrapedJob.scraped_at.desc()).limit(20).all()
        
        stats = {
            'total_jobs': db.query(ScrapedJob).count(),
            'total_runs': db.query(ScrapingRun).count(),
            'successful_runs': db.query(ScrapingRun).filter(ScrapingRun.status == 'completed').count()
        }
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "stats": stats,
            "recent_runs": recent_runs,
            "recent_jobs": recent_jobs,
            "message": message
        })
    
    @app.get("/export/csv")
    async def export_csv(db: Session = Depends(get_db)):
        jobs = db.query(ScrapedJob).order_by(ScrapedJob.scraped_at.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Título', 'Link', 'Fonte', 'Data Coleta'])
        
        for job in jobs:
            writer.writerow([
                job.title,
                job.link,
                job.source,
                job.scraped_at.strftime('%d/%m/%Y %H:%M')
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        return Response(
            content=csv_content,
            media_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename=vagas.csv'}
        )