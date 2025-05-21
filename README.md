# 🏎️ F1 Standings Scraper API 🏎️
This project scrapes the latest Formula 1 Drivers' and Constructors' Championship standings directly from the official Formula 1 website 
and exposes them via a simple Flask-based REST API. Built for integration into an F1 companion app using Flutter.

## Features

- 💨 Get current Drivers’ standings with names and points
- 🏁 Get current Constructors’ standings with team names and points
- 🔁 Uses Selenium WebDriver to scrape live data from the F1 site
- 🛠️ Built with Python and Flask

## Preview of JSON output 

> Sample JSON response from `/api/drivers`:

```json
{
  "Max Verstappen": "280",
  "Charles Leclerc": "210",
  "Lewis Hamilton": "190"
}
