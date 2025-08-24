from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, time
import json
import os

@dataclass
class SearchProfile:
    keywords: List[str]
    regions: List[str]
    schedule: str  # cron expression
    priority: int  # 1-5 (5 = highest)
    active: bool = True

class AutoSearchManager:
    def __init__(self):
        self.profiles = self._load_default_profiles()
        
    def _load_default_profiles(self) -> List[SearchProfile]:
        """Perfis pré-configurados para ONGs"""
        return [
            # TI - Alta demanda
            SearchProfile(
                keywords=['desenvolvedor python', 'programador java', 'analista sistemas', 'dev frontend', 'dev backend'],
                regions=['sao-paulo', 'rio-de-janeiro', 'belo-horizonte', 'remoto'],
                schedule='0 8,12,17 * * *',  # 3x/dia
                priority=5
            ),
            
            # Administrativo - Demanda média
            SearchProfile(
                keywords=['assistente administrativo', 'auxiliar administrativo', 'secretaria', 'recepcionista'],
                regions=['sao-paulo', 'rio-de-janeiro', 'brasilia'],
                schedule='0 9,15 * * *',  # 2x/dia
                priority=4
            ),
            
            # Vendas - Demanda alta
            SearchProfile(
                keywords=['vendedor', 'consultor vendas', 'representante comercial', 'inside sales'],
                regions=['sao-paulo', 'rio-de-janeiro', 'curitiba', 'porto-alegre'],
                schedule='0 10,16 * * *',  # 2x/dia
                priority=4
            ),
            
            # Estágio - Oportunidades para jovens
            SearchProfile(
                keywords=['estagio', 'trainee', 'jovem aprendiz', 'primeiro emprego'],
                regions=['sao-paulo', 'rio-de-janeiro', 'remoto'],
                schedule='0 14 * * *',  # 1x/dia
                priority=3
            ),
            
            # Operacional - Volume alto
            SearchProfile(
                keywords=['operador', 'auxiliar producao', 'almoxarife', 'motorista'],
                regions=['sao-paulo', 'rio-de-janeiro', 'campinas'],
                schedule='0 11 * * *',  # 1x/dia
                priority=3
            )
        ]
    
    def get_search_matrix(self) -> List[Dict]:
        """Gera matriz de buscas keyword x região"""
        searches = []
        
        for profile in self.profiles:
            if not profile.active:
                continue
                
            for keyword in profile.keywords:
                for region in profile.regions:
                    searches.append({
                        'keyword': keyword,
                        'region': region,
                        'schedule': profile.schedule,
                        'priority': profile.priority,
                        'profile_id': f"{keyword}_{region}".replace(' ', '_')
                    })
        
        return sorted(searches, key=lambda x: x['priority'], reverse=True)
    
    def get_high_priority_searches(self) -> List[Dict]:
        """Retorna buscas de alta prioridade para execução imediata"""
        matrix = self.get_search_matrix()
        return [s for s in matrix if s['priority'] >= 4]
    
    def add_custom_profile(self, keywords: List[str], regions: List[str], 
                          schedule: str, priority: int = 3) -> str:
        """Adiciona perfil personalizado"""
        profile = SearchProfile(
            keywords=keywords,
            regions=regions, 
            schedule=schedule,
            priority=priority
        )
        self.profiles.append(profile)
        return f"profile_{len(self.profiles)}"
    
    def get_regional_stats(self) -> Dict:
        """Estatísticas por região"""
        regions = {}
        for profile in self.profiles:
            for region in profile.regions:
                if region not in regions:
                    regions[region] = {'keywords': 0, 'priority_sum': 0}
                regions[region]['keywords'] += len(profile.keywords)
                regions[region]['priority_sum'] += profile.priority
        
        return regions