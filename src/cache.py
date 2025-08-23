from typing import Set, Dict, Any
from datetime import datetime, timedelta
import hashlib

class JobCache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._blacklist: Set[str] = {
            'terceirizada', 'outsourcing', 'consultoria generica',
            'vaga falsa', 'empresa fantasma'
        }
    
    def _generate_key(self, title: str, link: str) -> str:
        """Gera chave única para a vaga"""
        content = f"{title.lower()}{link}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def is_duplicate(self, title: str, link: str) -> bool:
        """Verifica se a vaga já foi processada"""
        key = self._generate_key(title, link)
        
        if key in self._cache:
            # Verifica se ainda está válido (24h)
            cached_time = self._cache[key]['timestamp']
            if datetime.now() - cached_time < timedelta(hours=24):
                return True
            else:
                # Remove cache expirado
                del self._cache[key]
        
        return False
    
    def add_job(self, title: str, link: str):
        """Adiciona vaga ao cache"""
        key = self._generate_key(title, link)
        self._cache[key] = {
            'title': title,
            'link': link,
            'timestamp': datetime.now()
        }
    
    def is_blacklisted(self, title: str, company: str = "") -> bool:
        """Verifica se vaga está na blacklist"""
        text = f"{title.lower()} {company.lower()}"
        return any(blocked in text for blocked in self._blacklist)
    
    def add_to_blacklist(self, term: str):
        """Adiciona termo à blacklist"""
        self._blacklist.add(term.lower())
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Retorna estatísticas do cache"""
        return {
            'cached_jobs': len(self._cache),
            'blacklist_terms': len(self._blacklist)
        }

# Instância global
job_cache = JobCache()