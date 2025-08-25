from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from .database import Base, get_db
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger

class PendingJob(Base):
    __tablename__ = "pending_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String)
    location = Column(String)
    source = Column(String, nullable=False)
    link = Column(String, nullable=False)
    quality_score = Column(Float, default=0)
    status = Column(String, default="pending")  # pending, approved, rejected
    rejection_reason = Column(Text)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String)
    auto_approved = Column(Boolean, default=False)

class ApprovalSystem:
    def __init__(self):
        self.auto_approval_threshold = 7  # Score mínimo para aprovação automática
        
    def add_jobs_for_review(self, jobs: List[Dict], db: Session) -> Dict:
        """Adiciona vagas para revisão manual"""
        added_count = 0
        auto_approved_count = 0
        
        for job in jobs:
            # Verificar se já existe
            existing = db.query(PendingJob).filter(PendingJob.link == job['link']).first()
            if existing:
                continue
                
            quality_score = job.get('quality_score', 0)
            
            pending_job = PendingJob(
                title=job['title'],
                company=job.get('company', ''),
                location=job.get('location', ''),
                source=job['source'],
                link=job['link'],
                quality_score=quality_score
            )
            
            # Auto-aprovação para vagas de alta qualidade
            if quality_score >= self.auto_approval_threshold:
                pending_job.status = "approved"
                pending_job.auto_approved = True
                pending_job.reviewed_at = datetime.utcnow()
                pending_job.reviewed_by = "system"
                auto_approved_count += 1
            
            db.add(pending_job)
            added_count += 1
        
        db.commit()
        
        return {
            "added": added_count,
            "auto_approved": auto_approved_count,
            "pending_review": added_count - auto_approved_count
        }
    
    def get_pending_jobs(self, db: Session, limit: int = 50) -> List[PendingJob]:
        """Retorna vagas pendentes de aprovação"""
        return db.query(PendingJob).filter(
            PendingJob.status == "pending"
        ).order_by(
            PendingJob.quality_score.desc(),
            PendingJob.scraped_at.desc()
        ).limit(limit).all()
    
    def approve_jobs(self, job_ids: List[int], reviewer: str, db: Session) -> Dict:
        """Aprova vagas em lote"""
        approved_count = 0
        
        for job_id in job_ids:
            job = db.query(PendingJob).filter(PendingJob.id == job_id).first()
            if job and job.status == "pending":
                job.status = "approved"
                job.reviewed_at = datetime.utcnow()
                job.reviewed_by = reviewer
                approved_count += 1
        
        db.commit()
        logger.info(f"{approved_count} vagas aprovadas por {reviewer}")
        
        return {"approved": approved_count}
    
    def reject_jobs(self, job_ids: List[int], reason: str, reviewer: str, db: Session) -> Dict:
        """Rejeita vagas em lote"""
        rejected_count = 0
        
        for job_id in job_ids:
            job = db.query(PendingJob).filter(PendingJob.id == job_id).first()
            if job and job.status == "pending":
                job.status = "rejected"
                job.rejection_reason = reason
                job.reviewed_at = datetime.utcnow()
                job.reviewed_by = reviewer
                rejected_count += 1
        
        db.commit()
        logger.info(f"{rejected_count} vagas rejeitadas por {reviewer}")
        
        return {"rejected": rejected_count}
    
    def get_approved_jobs(self, db: Session, limit: int = 100) -> List[PendingJob]:
        """Retorna vagas aprovadas para envio ao portal"""
        return db.query(PendingJob).filter(
            PendingJob.status == "approved"
        ).order_by(PendingJob.reviewed_at.desc()).limit(limit).all()
    
    def get_approval_stats(self, db: Session) -> Dict:
        """Estatísticas do sistema de aprovação"""
        total = db.query(PendingJob).count()
        pending = db.query(PendingJob).filter(PendingJob.status == "pending").count()
        approved = db.query(PendingJob).filter(PendingJob.status == "approved").count()
        rejected = db.query(PendingJob).filter(PendingJob.status == "rejected").count()
        auto_approved = db.query(PendingJob).filter(PendingJob.auto_approved == True).count()
        
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "auto_approved": auto_approved,
            "approval_rate": round((approved / total * 100) if total > 0 else 0, 2)
        }