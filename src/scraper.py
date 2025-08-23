from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from loguru import logger
from .cache import job_cache
from concurrent.futures import ThreadPoolExecutor
import os
import time

class JobScraper:
    def __init__(self, selenium_hub_url: str = None):
        self.selenium_hub_url = selenium_hub_url or os.getenv('SELENIUM_HUB_URL', 'http://localhost:4444/wd/hub')
        self.headless = os.getenv('CHROME_HEADLESS', 'true').lower() == 'true'
        self.delay = int(os.getenv('SCRAPING_DELAY', '2'))
        
    def _create_driver(self):
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        try:
            driver = webdriver.Remote(
                command_executor=self.selenium_hub_url,
                options=options
            )
            return driver
        except WebDriverException as e:
            logger.error(f"Failed to create driver: {e}")
            raise

    def scrape_infojobs(self, keyword: str, days_back: int = 1, location: str = "", filters: dict = None) -> list:
        driver = self._create_driver()
        jobs = []
        
        try:
            # URL com filtros
            url = f"https://www.infojobs.com.br/empregos.aspx?palabra={keyword.replace(' ', '+')}"
            if location:
                url += f"&provincia={location.replace(' ', '+')}"
            
            driver.get(url)
            
            # Wait com timeout
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="js_rowCard"]')))
            
            self._scroll_page(driver)
            
            job_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="js_rowCard"]')
            cutoff_date = datetime.now().date() - timedelta(days=days_back)
            
            for job_elem in job_elements:
                try:
                    title = job_elem.find_element(By.CSS_SELECTOR, 'h2').get_attribute("textContent").strip()
                    date_text = job_elem.find_element(By.CSS_SELECTOR, '[class*="text-medium small"]').get_attribute("textContent").strip()
                    link_elem = job_elem.find_element(By.CSS_SELECTOR, 'a[href*="vaga"]')
                    link = link_elem.get_attribute("href")
                    
                    # Verificar cache e blacklist
                    if job_cache.is_duplicate(title, link):
                        continue
                    
                    if job_cache.is_blacklisted(title):
                        logger.info(f"Vaga bloqueada: {title}")
                        continue
                    
                    job_date = self._parse_date(date_text)
                    if job_date and job_date >= cutoff_date:
                        job_cache.add_job(title, link)
                        jobs.append({
                            'title': title,
                            'date': job_date,
                            'link': link,
                            'source': 'InfoJobs'
                        })
                        
                        # Limite de vagas por execução
                        if len(jobs) >= 20:
                            break
                            
                except Exception as e:
                    logger.warning(f"Error parsing job: {e}")
                    continue
                    
        except TimeoutException:
            logger.error("Timeout waiting for job cards to load")
        except Exception as e:
            logger.error(f"Error scraping InfoJobs: {e}")
        finally:
            driver.quit()
            
        logger.info(f"Found {len(jobs)} new jobs for '{keyword}'")
        return jobs

    def _scroll_page(self, driver):
        last_height = driver.execute_script("return document.body.scrollHeight")
        attempts = 0
        
        while attempts < 10:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.delay)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
                
            last_height = new_height
            attempts += 1

    def _parse_date(self, date_text: str):
        try:
            if "hoje" in date_text.lower():
                return datetime.now().date()
            elif "ontem" in date_text.lower():
                return datetime.now().date() - timedelta(days=1)
            elif "/" in date_text:
                return datetime.strptime(date_text.split(": ")[-1], "%d/%m/%Y").date()
        except Exception as e:
            logger.warning(f"Error parsing date '{date_text}': {e}")
        return None