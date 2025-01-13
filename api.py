# api.py

import requests
from constants import API_URL

def fetch_stations_by_country(country):
    """
    Fetch radio stations by country using the Radio-Browser API.
    """
    try:
        response = requests.get(f"{API_URL}/bycountry/{country}")
        response.raise_for_status()
        stations = response.json()
        return stations
    except requests.RequestException as e:
        print(f"Error fetching stations for {country}: {e}")
        return []
