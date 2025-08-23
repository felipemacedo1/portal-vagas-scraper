from apscheduler.schedulers.blocking import BlockingScheduler
from src.scraper import JobScraper
from src.telegram_bot import TelegramNotifier
from src.database import SessionLocal, ScrapingRun, ScrapedJob, init_db
from datetime import datetime
from loguru import logger
import os

def scheduled_scrape():
    """Execução agendada de scraping"""
    logger.info("Starting scheduled scrape")
    
    scraper = JobScraper()
    notifier = TelegramNotifier()
    db = SessionLocal()
    
    keywords = ["desenvolvedor java", "python developer", "react developer"]
    
    try:
        for keyword in keywords:
            run = ScrapingRun(
                keyword=keyword,
                source="infojobs",
                status="running"
            )
            db.add(run)
            db.commit()
            db.refresh(run)
            
            try:
                jobs = scraper.scrape_infojobs(keyword, days_back=1)
                
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
                
                if new_jobs:
                    notifier.send_jobs(new_jobs, keyword)
                    logger.info(f"Found {len(new_jobs)} new jobs for '{keyword}'")
                
            except Exception as e:
                run.status = "failed"
                run.error_message = str(e)
                run.completed_at = datetime.utcnow()
                db.commit()
                logger.error(f"Scraping failed for '{keyword}': {e}")
                
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    
    scheduler = BlockingScheduler()
    
    # Executar todos os dias às 9h
    scheduler.add_job(
        scheduled_scrape,
        'cron',
        hour=9,
        minute=0,
        id='daily_scrape'
    )
    
    logger.info("Scheduler started - Daily scraping at 9:00 AM")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped")
        scheduler.shutdown()