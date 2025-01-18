# api.py

import requests
from constants import API_URL
from PyQt6.QtCore import QThread, pyqtSignal
from tenacity import retry, stop_after_attempt, wait_exponential

class FetchStationsWorker(QThread):
    """
    A worker thread to fetch radio stations by country.
    This is useful to prevent the UI from freezing during network requests.
    """
    finished = pyqtSignal(list)  # emits the list of stations once done

    def __init__(self, country):
        super().__init__()
        self.country = country
        self._is_running = True

    def run(self):
        if self._is_running:
            stations = fetch_stations_by_country(self.country)
            if self._is_running:  # Check again before emitting
                self.finished.emit(stations)

    def stop(self):
        """Stop the thread."""
        self._is_running = False

@retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_stations_by_country(country):
    """
    Fetch radio stations by country using the Radio-Browser API.
    """
    try:
        response = requests.get(f"{API_URL}/bycountry/{country}", timeout=6)
        response.raise_for_status()
        stations = response.json()
        if isinstance(stations, list):  # Ensure the response is a list of stations
            return stations
        else:
            print(f"Unexpected response format for {country}")
            return []
    except requests.Timeout:
        print(f"Request timed out for {country}")
        return []
    except requests.RequestException as e:
        print(f"Error fetching stations for {country}: {e}")
        return []