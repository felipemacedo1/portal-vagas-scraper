from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost:5432/portal_vagas')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ScrapingRun(Base):
    __tablename__ = "scraping_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False)
    source = Column(String, nullable=False)
    jobs_found = Column(Integer, default=0)
    status = Column(String, default="running")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)

class ScrapedJob(Base):
    __tablename__ = "scraped_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    link = Column(String, nullable=False, unique=True)
    source = Column(String, nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    sent_to_telegram = Column(Integer, default=0)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)