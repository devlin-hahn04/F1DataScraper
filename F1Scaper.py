from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import fastf1
import os
from datetime import datetime
import pandas as pd


# Setup Selenium Chrome options
def get_chrome_options():
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return chrome_options


# Get World Drivers' Championship standings
def getWDC():
    driver = webdriver.Chrome(options=get_chrome_options())
    driver.get("https://www.formula1.com/en/results/2025/drivers")

    rows = WebDriverWait(driver, 20).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
    )

    driver_map: dict[str, str] = {}

    for row in rows:
        tds = row.find_elements(By.TAG_NAME, "td")
        if len(tds) < 2:
            continue

        name = tds[1].text.strip()
        points = tds[-1].text.strip()
        driver_map[name] = points

    driver.quit()
    return driver_map


# Get World Constructors' Championship standings
def getWCC():
    driver = webdriver.Chrome(options=get_chrome_options())
    driver.get("https://www.formula1.com/en/results/2025/team")

    rows = WebDriverWait(driver, 20).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
    )

    team_map: dict[str, str] = {}

    for row in rows:
        tds = row.find_elements(By.TAG_NAME, "td")
        if len(tds) < 2:
            continue

        name = tds[1].text.strip()
        points = tds[-1].text.strip()
        team_map[name] = points

    driver.quit()
    return team_map


# Get next race using FastF1
def nextrace():
    # Set up cache
    if not os.path.exists('cache'):
        os.makedirs('cache')

    fastf1.Cache.enable_cache('cache')

    year = datetime.utcnow().year
    now = datetime.utcnow()
    schedule = fastf1.get_event_schedule(year)

    for _, row in schedule.iterrows():
        gp_name = row['EventName']
        round_number = row['RoundNumber']

        try:
            race = fastf1.get_session(year, round_number, 'R')  # 'R' = Race
            race_date = race.date
            if race_date > now:
                return gp_name
        except Exception:
            continue

    return "No upcoming races found."

