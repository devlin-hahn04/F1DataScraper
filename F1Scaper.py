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
# COORDINATES UPDATED: Canadian GP now at Montreal (45.5, -73.5228)

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

    # Geographic coordinates for each circuit - using full Grand Prix names
    circuit_coordinates = {
        "Bahrain Grand Prix": {"lat": 26.0325, "lng": 50.5106, "circuit": "Bahrain International Circuit", "location": "Sakhir, Bahrain"},
        "Saudi Arabian Grand Prix": {"lat": 21.6319, "lng": 39.1044, "circuit": "Jeddah Corniche Circuit", "location": "Jeddah, Saudi Arabia"},
        "Australian Grand Prix": {"lat": -37.8497, "lng": 144.968, "circuit": "Albert Park Circuit", "location": "Melbourne, Australia"},
        "Japanese Grand Prix": {"lat": 34.8433, "lng": 136.5333, "circuit": "Suzuka International Racing Course", "location": "Suzuka, Japan"},
        "Chinese Grand Prix": {"lat": 31.3389, "lng": 121.22, "circuit": "Shanghai International Circuit", "location": "Shanghai, China"},
        "Miami Grand Prix": {"lat": 25.9581, "lng": -80.2389, "circuit": "Miami International Autodrome", "location": "Miami, Florida"},
        "Emilia Romagna Grand Prix": {"lat": 44.3439, "lng": 11.7167, "circuit": "Imola Circuit", "location": "Imola, Italy"},
        "Monaco Grand Prix": {"lat": 43.7347, "lng": 7.4206, "circuit": "Circuit de Monaco", "location": "Monte Carlo, Monaco"},
        "Spanish Grand Prix": {"lat": 41.57, "lng": 2.26, "circuit": "Circuit de Barcelona-Catalunya", "location": "Barcelona, Spain"},
        "Barcelona Grand Prix": {"lat": 41.57, "lng": 2.26, "circuit": "Circuit de Barcelona-Catalunya", "location": "Barcelona, Spain"},
        "Canadian Grand Prix": {"lat": 45.5, "lng": -73.5228, "circuit": "Circuit Gilles Villeneuve", "location": "Montréal, Canada"},
        "Austrian Grand Prix": {"lat": 47.2197, "lng": 14.7647, "circuit": "Red Bull Ring", "location": "Spielberg, Austria"},
        "British Grand Prix": {"lat": 52.0786, "lng": -1.0169, "circuit": "Silverstone Circuit", "location": "Silverstone, England"},
        "Hungarian Grand Prix": {"lat": 47.5789, "lng": 19.2486, "circuit": "Hungaroring", "location": "Budapest, Hungary"},
        "Belgian Grand Prix": {"lat": 50.4372, "lng": 5.9714, "circuit": "Circuit de Spa-Francorchamps", "location": "Spa, Belgium"},
        "Dutch Grand Prix": {"lat": 52.3885, "lng": 4.5409, "circuit": "Circuit Zandvoort", "location": "Zandvoort, Netherlands"},
        "Italian Grand Prix": {"lat": 45.6156, "lng": 9.2811, "circuit": "Monza Circuit", "location": "Monza, Italy"},
        "Azerbaijan Grand Prix": {"lat": 40.3725, "lng": 49.8533, "circuit": "Baku City Circuit", "location": "Baku, Azerbaijan"},
        "Singapore Grand Prix": {"lat": 1.2914, "lng": 103.864, "circuit": "Marina Bay Street Circuit", "location": "Singapore"},
        "United States Grand Prix": {"lat": 30.1328, "lng": -97.6411, "circuit": "Circuit of the Americas", "location": "Austin, Texas"},
        "Mexico City Grand Prix": {"lat": 19.4042, "lng": -99.0908, "circuit": "Autodromo Hermanos Rodriguez", "location": "Mexico City, Mexico"},
        "São Paulo Grand Prix": {"lat": -23.7036, "lng": -46.6997, "circuit": "Interlagos Circuit", "location": "Sao Paulo, Brazil"},
        "Las Vegas Grand Prix": {"lat": 36.1147, "lng": -115.1728, "circuit": "Las Vegas Strip Circuit", "location": "Las Vegas, Nevada"},
        "Qatar Grand Prix": {"lat": 25.497, "lng": 51.524, "circuit": "Lusail International Circuit", "location": "Lusail, Qatar"},
        "Abu Dhabi Grand Prix": {"lat": 24.4672, "lng": 54.6031, "circuit": "Yas Marina Circuit", "location": "Abu Dhabi, UAE"},
    }

    for _, row in schedule.iterrows():
        gp_name = row['EventName']
        round_number = row['RoundNumber']
        location = row['Location']
        country = row['Country']
        
        # Build full location string
        full_location = f"{location}, {country}" if location != country else location

        try:
            race = fastf1.get_session(year, round_number, 'R')
            race_date = race.date
            if race_date > now:
                # Look up coordinates by the exact Grand Prix name
                coords = circuit_coordinates.get(gp_name)
                
                if not coords:
                    # Fallback: try to find by partial match
                    for key in circuit_coordinates:
                        if key.lower() in gp_name.lower():
                            coords = circuit_coordinates[key]
                            break
                
                if not coords:
                    # Final fallback to Miami
                    print(f"Warning: No coordinates found for {gp_name}, using Miami as fallback")
                    coords = circuit_coordinates.get("Miami Grand Prix")
                
                return {
                    "name": gp_name,
                    "circuit": coords["circuit"],
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


def get_track_layout(season, round_number, race_date, circuit_name):
    """Get track layout coordinates for a specific race from FastF1"""
    # Try to get layout from current or previous seasons
    for try_season in range(season, season - 3, -1):  # Try 2026, 2025, 2024
        try:
            # Try to find the same circuit in this season
            schedule = fastf1.get_event_schedule(try_season)
            
            # Find the round number for this circuit in the target season
            target_round = None
            for _, row in schedule.iterrows():
                if circuit_name.lower() in row['EventName'].lower():
                    target_round = row['RoundNumber']
                    break
            
            if target_round is None:
                continue
                
            # Get the session WITHOUT loading full data
            session = fastf1.get_session(try_season, target_round, 'R')
            circuit_info = session.get_circuit_info()
            
            corners = []
            if hasattr(circuit_info, 'corners') and circuit_info.corners is not None:
                for _, corner in circuit_info.corners.iterrows():
                    corner_data = {
                        "x": float(corner['X']),
                        "y": float(corner['Y']),
                    }
                    if 'Number' in corner and corner['Number'] is not None:
                        corner_data["number"] = int(corner['Number'])
                    if 'Letter' in corner and corner['Letter'] is not None:
                        corner_data["letter"] = corner['Letter']
                    corners.append(corner_data)
            
            print(f"✅ Got track layout for {circuit_name} from {try_season} season")
            return {
                "corners": corners,
                "rotation": circuit_info.rotation if hasattr(circuit_info, 'rotation') else 0
            }
        except Exception as e:
            continue
    
    # If all fails, return empty layout
    print(f"⚠️ No track layout found for {circuit_name} (will show placeholder)")
    return {"corners": [], "rotation": 0}

def get_full_schedule():
    # Set up cache
    if not os.path.exists('cache'):
        os.makedirs('cache')

    fastf1.Cache.enable_cache('cache')

    year = datetime.utcnow().year
    schedule = fastf1.get_event_schedule(year)
    
    # Geographic coordinates for each circuit (same as above)
    circuit_coordinates = {
        "Bahrain Grand Prix": {"lat": 26.0325, "lng": 50.5106, "circuit": "Bahrain International Circuit", "location": "Sakhir, Bahrain"},
        "Saudi Arabian Grand Prix": {"lat": 21.6319, "lng": 39.1044, "circuit": "Jeddah Corniche Circuit", "location": "Jeddah, Saudi Arabia"},
        "Australian Grand Prix": {"lat": -37.8497, "lng": 144.968, "circuit": "Albert Park Circuit", "location": "Melbourne, Australia"},
        "Japanese Grand Prix": {"lat": 34.8433, "lng": 136.5333, "circuit": "Suzuka International Racing Course", "location": "Suzuka, Japan"},
        "Chinese Grand Prix": {"lat": 31.3389, "lng": 121.22, "circuit": "Shanghai International Circuit", "location": "Shanghai, China"},
        "Miami Grand Prix": {"lat": 25.9581, "lng": -80.2389, "circuit": "Miami International Autodrome", "location": "Miami, Florida"},
        "Emilia Romagna Grand Prix": {"lat": 44.3439, "lng": 11.7167, "circuit": "Imola Circuit", "location": "Imola, Italy"},
        "Monaco Grand Prix": {"lat": 43.7347, "lng": 7.4206, "circuit": "Circuit de Monaco", "location": "Monte Carlo, Monaco"},
        "Spanish Grand Prix": {"lat": 41.57, "lng": 2.26, "circuit": "Circuit de Barcelona-Catalunya", "location": "Barcelona, Spain"},
        "Barcelona Grand Prix": {"lat": 41.57, "lng": 2.26, "circuit": "Circuit de Barcelona-Catalunya", "location": "Barcelona, Spain"},
        "Canadian Grand Prix": {"lat": 45.5, "lng": -73.5228, "circuit": "Circuit Gilles Villeneuve", "location": "Montreal, Canada"},
        "Austrian Grand Prix": {"lat": 47.2197, "lng": 14.7647, "circuit": "Red Bull Ring", "location": "Spielberg, Austria"},
        "British Grand Prix": {"lat": 52.0786, "lng": -1.0169, "circuit": "Silverstone Circuit", "location": "Silverstone, England"},
        "Hungarian Grand Prix": {"lat": 47.5789, "lng": 19.2486, "circuit": "Hungaroring", "location": "Budapest, Hungary"},
        "Belgian Grand Prix": {"lat": 50.4372, "lng": 5.9714, "circuit": "Circuit de Spa-Francorchamps", "location": "Spa, Belgium"},
        "Dutch Grand Prix": {"lat": 52.3885, "lng": 4.5409, "circuit": "Circuit Zandvoort", "location": "Zandvoort, Netherlands"},
        "Italian Grand Prix": {"lat": 45.6156, "lng": 9.2811, "circuit": "Monza Circuit", "location": "Monza, Italy"},
        "Azerbaijan Grand Prix": {"lat": 40.3725, "lng": 49.8533, "circuit": "Baku City Circuit", "location": "Baku, Azerbaijan"},
        "Singapore Grand Prix": {"lat": 1.2914, "lng": 103.864, "circuit": "Marina Bay Street Circuit", "location": "Singapore"},
        "United States Grand Prix": {"lat": 30.1328, "lng": -97.6411, "circuit": "Circuit of the Americas", "location": "Austin, Texas"},
        "Mexico City Grand Prix": {"lat": 19.4042, "lng": -99.0908, "circuit": "Autodromo Hermanos Rodriguez", "location": "Mexico City, Mexico"},
        "Sao Paulo Grand Prix": {"lat": -23.7036, "lng": -46.6997, "circuit": "Interlagos Circuit", "location": "Sao Paulo, Brazil"},
        "Las Vegas Grand Prix": {"lat": 36.1147, "lng": -115.1728, "circuit": "Las Vegas Strip Circuit", "location": "Las Vegas, Nevada"},
        "Qatar Grand Prix": {"lat": 25.497, "lng": 51.524, "circuit": "Lusail International Circuit", "location": "Lusail, Qatar"},
        "Abu Dhabi Grand Prix": {"lat": 24.4672, "lng": 54.6031, "circuit": "Yas Marina Circuit", "location": "Abu Dhabi, UAE"},
    }
    
    all_races = []
    
    for _, row in schedule.iterrows():
        gp_name = row['EventName']
        round_number = row['RoundNumber']
        
        # Only include Grand Prix events
        if 'Grand Prix' not in gp_name:
            continue
            
        try:
            race = fastf1.get_session(year, round_number, 'R')
            race_date = race.date
            
            # Get track layout for this race
            track_layout = get_track_layout(year, round_number, race_date, gp_name)
            
            # Look up coordinates
            coords = circuit_coordinates.get(gp_name)
            
            if not coords:
                # Fallback partial match
                for key in circuit_coordinates:
                    if key.lower() in gp_name.lower():
                        coords = circuit_coordinates[key]
                        break
            
            if not coords:
                coords = circuit_coordinates.get("Miami Grand Prix")
            
            all_races.append({
                "round": round_number,
                "name": gp_name,
                "circuit": coords["circuit"],
                "location": coords["location"],
                "date": race_date.strftime("%B %d, %Y"),
                "time": race_date.strftime("%H:%M CET"),
                "lat": coords["lat"],
                "lng": coords["lng"],
                "track_layout": track_layout  # NEW: Add track layout data
            })
        except Exception as e:
            print(f"Error getting session for {gp_name}: {e}")
            continue
    
    return all_races

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

