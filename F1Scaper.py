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
    chrome_options.add_argument("--headless")  # Comment out to debug visually
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
    return chrome_options

# Get World Drivers' Championship standings (with team)
def getWDC():
    driver = webdriver.Chrome(options=get_chrome_options())
    driver.get("https://www.formula1.com/en/results/2026/drivers")

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
    driver.get("https://www.formula1.com/en/results/2026/team")

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

# Get next race using FastF1 (original - returns just name)
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

# Get next race with full details (name, circuit, location, date, time, lat, lng)
def get_next_race_details():
    # Set up cache
    if not os.path.exists('cache'):
        os.makedirs('cache')

    fastf1.Cache.enable_cache('cache')

    year = datetime.utcnow().year
    now = datetime.utcnow()
    schedule = fastf1.get_event_schedule(year)

    # Geographic coordinates for each circuit (for globe visualization)
    circuit_coordinates = {
        "Bahrain International Circuit": {"lat": 26.0325, "lng": 50.5106, "location": "Sakhir, Bahrain"},
        "Jeddah Corniche Circuit": {"lat": 21.6319, "lng": 39.1044, "location": "Jeddah, Saudi Arabia"},
        "Albert Park Circuit": {"lat": -37.8497, "lng": 144.968, "location": "Melbourne, Australia"},
        "Suzuka International Racing Course": {"lat": 34.8433, "lng": 136.5333, "location": "Suzuka, Japan"},
        "Shanghai International Circuit": {"lat": 31.3389, "lng": 121.22, "location": "Shanghai, China"},
        "Miami International Autodrome": {"lat": 25.9581, "lng": -80.2389, "location": "Miami, Florida"},
        "Imola Circuit": {"lat": 44.3439, "lng": 11.7167, "location": "Imola, Italy"},
        "Circuit de Monaco": {"lat": 43.7347, "lng": 7.4206, "location": "Monte Carlo, Monaco"},
        "Circuit de Barcelona-Catalunya": {"lat": 41.57, "lng": 2.26, "location": "Barcelona, Spain"},
        "Circuit Gilles Villeneuve": {"lat": 45.5, "lng": -73.5228, "location": "Montreal, Canada"},
        "Red Bull Ring": {"lat": 47.2197, "lng": 14.7647, "location": "Spielberg, Austria"},
        "Silverstone Circuit": {"lat": 52.0786, "lng": -1.0169, "location": "Silverstone, England"},
        "Hungaroring": {"lat": 47.5789, "lng": 19.2486, "location": "Budapest, Hungary"},
        "Circuit de Spa-Francorchamps": {"lat": 50.4372, "lng": 5.9714, "location": "Spa, Belgium"},
        "Circuit Zandvoort": {"lat": 52.3885, "lng": 4.5409, "location": "Zandvoort, Netherlands"},
        "Monza Circuit": {"lat": 45.6156, "lng": 9.2811, "location": "Monza, Italy"},
        "Baku City Circuit": {"lat": 40.3725, "lng": 49.8533, "location": "Baku, Azerbaijan"},
        "Marina Bay Street Circuit": {"lat": 1.2914, "lng": 103.864, "location": "Singapore"},
        "Circuit of the Americas": {"lat": 30.1328, "lng": -97.6411, "location": "Austin, Texas"},
        "Autodromo Hermanos Rodriguez": {"lat": 19.4042, "lng": -99.0908, "location": "Mexico City, Mexico"},
        "Interlagos Circuit": {"lat": -23.7036, "lng": -46.6997, "location": "Sao Paulo, Brazil"},
        "Las Vegas Strip Circuit": {"lat": 36.1147, "lng": -115.1728, "location": "Las Vegas, Nevada"},
        "Lusail International Circuit": {"lat": 25.497, "lng": 51.524, "location": "Lusail, Qatar"},
        "Yas Marina Circuit": {"lat": 24.4672, "lng": 54.6031, "location": "Abu Dhabi, UAE"},
    }

    for _, row in schedule.iterrows():
        gp_name = row['EventName']
        round_number = row['RoundNumber']
        circuit_name = row['EventLocation']
        event_date = row['EventDate']

        try:
            race = fastf1.get_session(year, round_number, 'R')  # 'R' = Race
            race_date = race.date
            if race_date > now:
                # Get circuit coordinates
                coords = circuit_coordinates.get(circuit_name, {
                    "lat": 0, 
                    "lng": 0, 
                    "location": circuit_name
                })
                
                return {
                    "name": gp_name,
                    "circuit": circuit_name,
                    "location": coords["location"],
                    "date": race_date.strftime("%B %d, %Y"),
                    "time": race_date.strftime("%H:%M CET"),
                    "lat": coords["lat"],
                    "lng": coords["lng"]
                }
        except Exception as e:
            print(f"Error getting session for {gp_name}: {e}")
            continue

    return {
        "name": "No upcoming races found",
        "circuit": "TBD",
        "location": "TBD",
        "date": "TBD",
        "time": "TBD",
        "lat": 0,
        "lng": 0
    }

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



