from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver1 = webdriver.Chrome()
driver1.get("https://www.formula1.com/en/results/2025/drivers")

driver2= webdriver.Chrome()
driver2.get("https://www.formula1.com/en/results/2025/team")


def getWDC(driver1):
    # Wait until at least one driver row is visible
    rows = WebDriverWait(driver1, 20).until(
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
        

    driver1.quit()
    return driver_map


def getWCC(driver2):
    # Wait until at least one driver row is visible
    rows = WebDriverWait(driver2, 20).until(
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

    driver2.quit()
    return team_map
    

print("Drivers Champ")

drivers= getWDC(driver1)
print(drivers)

print()

print("Constructors Champ")

teams= getWCC(driver2)
print(teams)