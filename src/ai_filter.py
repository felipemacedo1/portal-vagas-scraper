import re
from typing import List, Dict
from loguru import logger

class AIJobFilter:
    def __init__(self):
        self.salary_patterns = {
            'junior': (2000, 4000),
            'pleno': (4000, 8000), 
            'senior': (8000, 15000),
            'especialista': (10000, 20000)
        }
        
        self.blacklist_companies = {
            'empresa terceirizada', 'consultoria generica', 'rh terceirizado',
            'agencia de emprego', 'empresa fantasma'
        }
        
        self.quality_keywords = {
            'high': ['remoto', 'home office', 'beneficios', 'plr', 'vale refeicao'],
            'medium': ['hibrido', 'flexivel', 'convenio'],
            'low': ['presencial obrigatorio', 'sem beneficios']
        }
    
    def filter_jobs(self, jobs: List[Dict], filters: Dict = None) -> List[Dict]:
        """Filtra vagas usando IA básica"""
        if not filters:
            return jobs
            
        filtered = []
        
        for job in jobs:
            if self._passes_filters(job, filters):
                job['quality_score'] = self._calculate_quality_score(job)
                filtered.append(job)
        
        # Ordenar por qualidade
        return sorted(filtered, key=lambda x: x.get('quality_score', 0), reverse=True)
    
    def _passes_filters(self, job: Dict, filters: Dict) -> bool:
        """Verifica se vaga passa nos filtros"""
        
        # Filtro de salário
        if filters.get('min_salary'):
            salary = self._extract_salary(job.get('title', '') + ' ' + job.get('description', ''))
            if salary and salary < filters['min_salary']:
                return False
        
        # Filtro de localização
        if filters.get('location'):
            location_filter = filters['location'].lower()
            job_location = job.get('location', '').lower()
            if location_filter not in job_location and location_filter != 'remoto':
                return False
        
        # Filtro de senioridade
        if filters.get('seniority'):
            title_lower = job.get('title', '').lower()
            if filters['seniority'].lower() not in title_lower:
                return False
        
        # Blacklist de empresas
        company = job.get('company', '').lower()
        if any(blocked in company for blocked in self.blacklist_companies):
            return False
            
        return True
    
    def _extract_salary(self, text: str) -> int:
        """Extrai salário do texto"""
        text = text.lower()
        
        # Padrões de salário
        patterns = [
            r'r\$\s*(\d+\.?\d*)',
            r'(\d+)k',
            r'salário.*?(\d+\.?\d*)',
            r'até.*?(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1).replace('.', ''))
                if 'k' in pattern:
                    value *= 1000
                return int(value)
        
        # Inferir por senioridade
        for level, (min_sal, max_sal) in self.salary_patterns.items():
            if level in text:
                return min_sal
                
        return 0
    
    def _calculate_quality_score(self, job: Dict) -> int:
        """Calcula score de qualidade da vaga"""
        score = 0
        text = (job.get('title', '') + ' ' + job.get('description', '')).lower()
        
        # Pontos por palavras-chave de qualidade
        for quality, keywords in self.quality_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if quality == 'high':
                        score += 3
                    elif quality == 'medium':
                        score += 2
                    else:
                        score -= 1
        
        # Bonus por empresa conhecida
        company = job.get('company', '').lower()
        known_companies = ['google', 'microsoft', 'amazon', 'nubank', 'stone', 'ifood']
        if any(comp in company for comp in known_companies):
            score += 5
            
        return max(0, score)