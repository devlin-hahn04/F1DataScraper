from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service




def getWDC():

    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium-browser"  
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service= Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service= service, options=chrome_options)
    driver.get("https://www.formula1.com/en/results/2025/drivers")

    # Wait until at least one driver row is visible
    rows = WebDriverWait(driver, 20).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
    )

    driver_map: dict[str, str]= {}

    for row in rows:
        tds = row.find_elements(By.TAG_NAME, "td")
        if len(tds) < 2:
            continue
        
        name = tds[1].text.strip()
        
        points = tds[-1].text.strip()
        driver_map[name]= points
        

    driver.quit()
    return driver_map


def getWCC():

    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium-browser"  
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service= Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service= service, options=chrome_options)
    driver.get("https://www.formula1.com/en/results/2025/team")


    # Wait until at least one driver row is visible
    rows = WebDriverWait(driver, 20).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
    )

    team_map: dict[str, str]= {}

    for row in rows:
        tds = row.find_elements(By.TAG_NAME, "td")
        if len(tds) < 2:
            continue
        
        name = tds[1].text.strip()
        
        points = tds[-1].text.strip()
        team_map[name]= points

    driver.quit()
    return team_map
    

# print("Drivers Champ")

# drivers= getWDC()
# print(drivers)

# print()

# print("Constructors Champ")

# teams= getWCC()
# print(teams)