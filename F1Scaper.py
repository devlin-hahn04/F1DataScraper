from httpcore import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import fastf1
import os
from datetime import datetime
import pandas as pd

import requests


# Setup Selenium Chrome options
def get_chrome_options():
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return chrome_options


# Get World Drivers' Championship standings (with team)
def getWDC():
    driver = webdriver.Chrome(options=get_chrome_options())
    driver.get("https://www.formula1.com/en/results/2025/drivers")

    rows = WebDriverWait(driver, 20).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
    )

    driver_map: dict[str, dict[str, str]] = {}

    for row in rows:
        tds = row.find_elements(By.TAG_NAME, "td")
        if len(tds) < 4:  # Make sure enough columns exist
            continue

        name = tds[1].text.strip()   # Driver column
        team = tds[3].text.strip()   # Team/Car column
        points = int(tds[-1].text.strip())  # Last column is always points

        driver_map[name] = {
            "team": team,
            "points": points
        }

        print(f"{name} | Team: {team} | Points: {points}")

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


def getDriverPhotos():
    url = "https://api.openf1.org/v1/drivers?session_key=latest"
    drivers = requests.get(url).json()

    driverPhoto_map: dict[str, str] = {}

    if isinstance(drivers, dict):
        print("Unexpected response:", drivers)
        return driverPhoto_map

    for d in drivers:
        if isinstance(d, dict) and d.get("headshot_url") and d.get("full_name"):
            last_name = d["full_name"].split()[-1].capitalize()
            driverPhoto_map[last_name] = d["headshot_url"]

    return driverPhoto_map


def getTeamLogos():
    driver = webdriver.Chrome(options=get_chrome_options())
    driver.get("https://www.formula1.com/en/teams")

    logos_map = {}
    try:
        # Wait for team containers (flex elements containing team info)
        team_containers = WebDriverWait(driver, 20).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "span.flex.flex-col.lg\\:flex-row"))
        )
        print(f"Found {len(team_containers)} team containers")

        for container in team_containers:
            try:
                # Extract team name (from the <p> or <span> with typography class)
                team_name = container.find_element(By.CSS_SELECTOR, "p.typography-module_display-1-bold").text.strip()
                # Extract logo image
                logo = container.find_element(By.CSS_SELECTOR, "span.Teamlogo-module_teamlogo__1A3j1 img")
                logo_url = logo.get_attribute("src")

                if team_name and logo_url:
                    logos_map[team_name] = logo_url
                    print(f"Team: {team_name}, Logo: {logo_url}")
            except Exception as e:
                print(f"Error processing team container: {e}")
                continue

    except TimeoutException as e:
        print("Timeout waiting for team containers. Page source:", driver.page_source[:1000])
        driver.save_screenshot("debug_screenshot.png")
    finally:
        driver.quit()
    return logos_map


