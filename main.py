import uvicorn
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv('API_PORT', 8081))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    logger.info(f"Starting Portal Vagas Scraper API on {host}:{port}")
    
    uvicorn.run(
        "src.api:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )