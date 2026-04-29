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
        "Bahrain": {"lat": 26.0325, "lng": 50.5106, "location": "Sakhir, Bahrain", "circuit": "Bahrain International Circuit"},
        "Jeddah": {"lat": 21.6319, "lng": 39.1044, "location": "Jeddah, Saudi Arabia", "circuit": "Jeddah Corniche Circuit"},
        "Melbourne": {"lat": -37.8497, "lng": 144.968, "location": "Melbourne, Australia", "circuit": "Albert Park Circuit"},
        "Suzuka": {"lat": 34.8433, "lng": 136.5333, "location": "Suzuka, Japan", "circuit": "Suzuka International Racing Course"},
        "Shanghai": {"lat": 31.3389, "lng": 121.22, "location": "Shanghai, China", "circuit": "Shanghai International Circuit"},
        "Miami": {"lat": 25.9581, "lng": -80.2389, "location": "Miami, Florida", "circuit": "Miami International Autodrome"},
        "Imola": {"lat": 44.3439, "lng": 11.7167, "location": "Imola, Italy", "circuit": "Imola Circuit"},
        "Monaco": {"lat": 43.7347, "lng": 7.4206, "location": "Monte Carlo, Monaco", "circuit": "Circuit de Monaco"},
        "Barcelona": {"lat": 41.57, "lng": 2.26, "location": "Barcelona, Spain", "circuit": "Circuit de Barcelona-Catalunya"},
        "Montreal": {"lat": 45.5, "lng": -73.5228, "location": "Montreal, Canada", "circuit": "Circuit Gilles Villeneuve"},
        "Spielberg": {"lat": 47.2197, "lng": 14.7647, "location": "Spielberg, Austria", "circuit": "Red Bull Ring"},
        "Silverstone": {"lat": 52.0786, "lng": -1.0169, "location": "Silverstone, England", "circuit": "Silverstone Circuit"},
        "Budapest": {"lat": 47.5789, "lng": 19.2486, "location": "Budapest, Hungary", "circuit": "Hungaroring"},
        "Spa": {"lat": 50.4372, "lng": 5.9714, "location": "Spa, Belgium", "circuit": "Circuit de Spa-Francorchamps"},
        "Zandvoort": {"lat": 52.3885, "lng": 4.5409, "location": "Zandvoort, Netherlands", "circuit": "Circuit Zandvoort"},
        "Monza": {"lat": 45.6156, "lng": 9.2811, "location": "Monza, Italy", "circuit": "Monza Circuit"},
        "Baku": {"lat": 40.3725, "lng": 49.8533, "location": "Baku, Azerbaijan", "circuit": "Baku City Circuit"},
        "Singapore": {"lat": 1.2914, "lng": 103.864, "location": "Singapore", "circuit": "Marina Bay Street Circuit"},
        "Austin": {"lat": 30.1328, "lng": -97.6411, "location": "Austin, Texas", "circuit": "Circuit of the Americas"},
        "Mexico City": {"lat": 19.4042, "lng": -99.0908, "location": "Mexico City, Mexico", "circuit": "Autodromo Hermanos Rodriguez"},
        "Sao Paulo": {"lat": -23.7036, "lng": -46.6997, "location": "Sao Paulo, Brazil", "circuit": "Interlagos Circuit"},
        "Las Vegas": {"lat": 36.1147, "lng": -115.1728, "location": "Las Vegas, Nevada", "circuit": "Las Vegas Strip Circuit"},
        "Lusail": {"lat": 25.497, "lng": 51.524, "location": "Lusail, Qatar", "circuit": "Lusail International Circuit"},
        "Yas Island": {"lat": 24.4672, "lng": 54.6031, "location": "Abu Dhabi, UAE", "circuit": "Yas Marina Circuit"},
    }

    for _, row in schedule.iterrows():
        gp_name = row['EventName']
        round_number = row['RoundNumber']
        # Use 'Location' from FastF1 (city/region)
        location = row['Location']
        country = row['Country']
        
        # Build full location string
        full_location = f"{location}, {country}" if location != country else location

        try:
            race = fastf1.get_session(year, round_number, 'R')
            race_date = race.date
            if race_date > now:
                # Try to match coordinates by name
                coords = None
                for key in circuit_coordinates:
                    if key.lower() in gp_name.lower() or key.lower() in location.lower():
                        coords = circuit_coordinates[key]
                        break
                
                if not coords:
                    coords = circuit_coordinates.get("Miami")
                
                return {
                    "name": gp_name,
                    "circuit": coords["circuit"],
                    "location": full_location,
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



