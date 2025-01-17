# api.py

import requests
from constants import API_URL
from PyQt6.QtCore import QThread, pyqtSignal

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
