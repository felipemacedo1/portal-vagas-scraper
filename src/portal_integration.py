import requests
import os
from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime

class PortalIntegration:
    def __init__(self):
        self.portal_api_url = os.getenv('PORTAL_API_URL', 'http://localhost:8080/api')
        self.portal_admin_token = os.getenv('PORTAL_ADMIN_TOKEN', '')
        self.ong_employer_id = os.getenv('ONG_EMPLOYER_ID', '1')  # ID do empregador ONG
        
    def send_jobs_to_portal(self, jobs: List[Dict], auto_approve: bool = False) -> Dict:
        """Envia vagas para o portal principal"""
        if not jobs:
            return {"status": "no_jobs", "sent": 0}
            
        sent_count = 0
        failed_jobs = []
        
        for job in jobs:
            try:
                job_data = self._format_job_for_portal(job)
                
                # Criar vaga no portal
                response = self._create_job_in_portal(job_data)
                
                if response.get('success'):
                    job_id = response.get('job_id')
                    
                    # Auto-aprovar se configurado
                    if auto_approve and job_id:
                        self._approve_job_in_portal(job_id)
                    
                    sent_count += 1
                    logger.info(f"Vaga enviada: {job['title']} -> ID: {job_id}")
                else:
                    failed_jobs.append(job['title'])
                    
            except Exception as e:
                logger.error(f"Erro enviando vaga {job['title']}: {e}")
                failed_jobs.append(job['title'])
        
        return {
            "status": "completed",
            "sent": sent_count,
            "failed": len(failed_jobs),
            "failed_jobs": failed_jobs
        }
    
    def _format_job_for_portal(self, job: Dict) -> Dict:
        """Formata vaga para o formato do portal"""
        return {
            "title": job['title'],
            "description": self._generate_description(job),
            "requirements": self._extract_requirements(job),
            "benefits": self._extract_benefits(job),
            "salary": self._extract_salary(job),
            "location": job.get('location', 'Não informado'),
            "workType": self._determine_work_type(job),
            "contractType": self._determine_contract_type(job),
            "seniorityLevel": self._determine_seniority(job),
            "externalUrl": job['link'],
            "source": job['source'],
            "companyId": self.ong_employer_id
        }
    
    def _create_job_in_portal(self, job_data: Dict) -> Dict:
        """Cria vaga no portal via API"""
        headers = {
            'Authorization': f'Bearer {self.portal_admin_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f"{self.portal_api_url}/jobs",
                json=job_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                return {"success": True, "job_id": response.json().get('id')}
            else:
                logger.error(f"Portal API error: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except requests.RequestException as e:
            logger.error(f"Portal API request failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _approve_job_in_portal(self, job_id: int) -> bool:
        """Aprova vaga automaticamente no portal"""
        headers = {
            'Authorization': f'Bearer {self.portal_admin_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f"{self.portal_api_url}/admin/jobs/{job_id}/approve",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Vaga {job_id} aprovada automaticamente")
                return True
            else:
                logger.error(f"Erro aprovando vaga {job_id}: {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Erro na aprovação automática: {e}")
            return False
    
    def _generate_description(self, job: Dict) -> str:
        """Gera descrição formatada da vaga"""
        description = f"**Vaga coletada automaticamente de {job['source']}**\n\n"
        description += f"**Título:** {job['title']}\n\n"
        
        if job.get('company'):
            description += f"**Empresa:** {job['company']}\n\n"
            
        if job.get('location'):
            description += f"**Localização:** {job['location']}\n\n"
            
        description += f"**Fonte:** {job['source']}\n"
        description += f"**Data de coleta:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        description += f"**Link original:** {job['link']}\n\n"
        description += "Esta vaga foi coletada automaticamente. Para mais detalhes, acesse o link original."
        
        return description
    
    def _extract_requirements(self, job: Dict) -> str:
        """Extrai requisitos da vaga"""
        title = job['title'].lower()
        
        # Requisitos baseados no título
        if 'desenvolvedor' in title or 'programador' in title:
            return "Conhecimento em programação, lógica de programação, trabalho em equipe"
        elif 'vendedor' in title or 'vendas' in title:
            return "Experiência em vendas, boa comunicação, orientação para resultados"
        elif 'administrativo' in title:
            return "Conhecimento em pacote Office, organização, atenção aos detalhes"
        elif 'estagio' in title or 'trainee' in title:
            return "Cursando ensino superior, proatividade, vontade de aprender"
        else:
            return "Requisitos conforme descrição da vaga original"
    
    def _extract_benefits(self, job: Dict) -> str:
        """Extrai benefícios da vaga"""
        return "Benefícios conforme política da empresa (verificar na vaga original)"
    
    def _extract_salary(self, job: Dict) -> Optional[float]:
        """Extrai salário da vaga"""
        # Implementar extração de salário do título/descrição
        return None
    
    def _determine_work_type(self, job: Dict) -> str:
        """Determina tipo de trabalho"""
        title_desc = (job['title'] + ' ' + job.get('location', '')).lower()
        
        if 'remoto' in title_desc or 'home office' in title_desc:
            return 'REMOTE'
        elif 'hibrido' in title_desc:
            return 'HYBRID'
        else:
            return 'ON_SITE'
    
    def _determine_contract_type(self, job: Dict) -> str:
        """Determina tipo de contrato"""
        title = job['title'].lower()
        
        if 'estagio' in title:
            return 'INTERNSHIP'
        elif 'freelancer' in title or 'autonomo' in title:
            return 'FREELANCE'
        else:
            return 'CLT'
    
    def _determine_seniority(self, job: Dict) -> str:
        """Determina nível de senioridade"""
        title = job['title'].lower()
        
        if 'junior' in title or 'jr' in title or 'estagio' in title:
            return 'JUNIOR'
        elif 'senior' in title or 'sr' in title:
            return 'SENIOR'
        elif 'pleno' in title or 'pl' in title:
            return 'MID_LEVEL'
        else:
            return 'MID_LEVEL'  # Default