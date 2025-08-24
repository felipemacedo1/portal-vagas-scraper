from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from loguru import logger

class CathoScraper:
    def scrape_jobs(self, driver, keyword: str, location: str = "", days_back: int = 1) -> list:
        jobs = []
        try:
            url = f"https://www.catho.com.br/vagas/?q={keyword.replace(' ', '+')}"
            if location:
                url += f"&cidade={location}"
                
            driver.get(url)
            
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="job-card"]')))
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, '[data-testid="job-card"]')
            
            for card in job_cards[:20]:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, 'h2 a')
                    title = title_elem.text.strip()
                    link = title_elem.get_attribute('href')
                    
                    try:
                        company = card.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]').text.strip()
                    except:
                        company = "Empresa não informada"
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'link': link,
                        'source': 'Catho',
                        'date': datetime.now().date()
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing Catho job: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Catho scraping failed: {e}")
            
        return jobs