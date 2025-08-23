from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')

driver = webdriver.Remote(
    command_executor='http://chrome:4444/wd/hub',
    options=options
)

try:
    url = "https://www.infojobs.com.br/empregos.aspx?palabra=desenvolvedor+java"
    driver.get(url)
    time.sleep(5)
    
    # Encontrar cards de vagas
    job_cards = driver.find_elements(By.CSS_SELECTOR, '[class*="js_rowCard"]')
    print(f"Encontrados {len(job_cards)} cards de vagas")
    
    if job_cards:
        first_card = job_cards[0]
        print("\n=== PRIMEIRO CARD ===")
        print(first_card.get_attribute('outerHTML')[:1000])
        
        # Testar seletores de título
        title_selectors = [
            '[class*="h3 font-weight-bold text-body mb-8"]',
            'h3',
            '.title',
            '[class*="title"]',
            'a[title]',
            '[data-testid*="title"]'
        ]
        
        print("\n=== TESTANDO SELETORES DE TÍTULO ===")
        for selector in title_selectors:
            try:
                title_elem = first_card.find_element(By.CSS_SELECTOR, selector)
                title_text = title_elem.get_attribute("textContent").strip()
                print(f"✅ {selector}: '{title_text}'")
                break
            except:
                print(f"❌ {selector}")
        
        # Testar seletores de data
        date_selectors = [
            '[class*="text-medium small"]',
            '.date',
            '[class*="date"]',
            'time',
            '[class*="time"]'
        ]
        
        print("\n=== TESTANDO SELETORES DE DATA ===")
        for selector in date_selectors:
            try:
                date_elem = first_card.find_element(By.CSS_SELECTOR, selector)
                date_text = date_elem.get_attribute("textContent").strip()
                print(f"✅ {selector}: '{date_text}'")
                break
            except:
                print(f"❌ {selector}")
        
        # Testar seletores de link
        link_selectors = [
            '[class*="py-16 pl-24 pr-16 cursor-pointer js_vacancyLoad js_cardLink"]',
            'a[href*="vaga"]',
            'a[href]',
            '[data-href]'
        ]
        
        print("\n=== TESTANDO SELETORES DE LINK ===")
        for selector in link_selectors:
            try:
                link_elem = first_card.find_element(By.CSS_SELECTOR, selector)
                link_href = link_elem.get_attribute("href") or link_elem.get_attribute("data-href")
                print(f"✅ {selector}: '{link_href}'")
                break
            except:
                print(f"❌ {selector}")

finally:
    driver.quit()