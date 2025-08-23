from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Configurar Chrome
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')

# Conectar ao Selenium Hub
driver = webdriver.Remote(
    command_executor='http://chrome:4444/wd/hub',
    options=options
)

try:
    # Acessar InfoJobs
    url = "https://www.infojobs.com.br/empregos.aspx?palabra=desenvolvedor+java"
    print(f"Acessando: {url}")
    driver.get(url)
    
    # Aguardar carregamento
    time.sleep(5)
    
    # Tentar diferentes seletores
    selectors_to_test = [
        '[class*="js_rowCard"]',
        '.js_rowCard',
        '[data-testid="job-card"]',
        '.job-item',
        '.vacancy-item',
        'article',
        '[class*="card"]',
        '[class*="job"]'
    ]
    
    print("Testando seletores:")
    for selector in selectors_to_test:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"✅ {selector}: {len(elements)} elementos")
            if len(elements) > 0:
                # Pegar o primeiro elemento e ver sua estrutura
                first_elem = elements[0]
                print(f"   HTML: {first_elem.get_attribute('outerHTML')[:200]}...")
                break
        except Exception as e:
            print(f"❌ {selector}: {str(e)}")
    
    # Verificar se a página carregou
    print(f"\nTítulo da página: {driver.title}")
    print(f"URL atual: {driver.current_url}")
    
finally:
    driver.quit()