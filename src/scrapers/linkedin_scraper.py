from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from loguru import logger
import time

class LinkedInScraper:
    def scrape_jobs(self, driver, keyword: str, location: str = "Brasil", days_back: int = 1) -> list:
        jobs = []
        try:
            url = f"https://www.linkedin.com/jobs/search/?keywords={keyword.replace(' ', '%20')}&location={location}"
            driver.get(url)
            
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.job-search-card')))
            
            self._scroll_and_load(driver)
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, '.job-search-card')
            
            for card in job_cards[:20]:
                try:
                    title = card.find_element(By.CSS_SELECTOR, '.base-search-card__title').text.strip()
                    company = card.find_element(By.CSS_SELECTOR, '.base-search-card__subtitle').text.strip()
                    link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'link': link,
                        'source': 'LinkedIn',
                        'date': datetime.now().date()
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing LinkedIn job: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"LinkedIn scraping failed: {e}")
            
        return jobs
    
    def _scroll_and_load(self, driver):
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)