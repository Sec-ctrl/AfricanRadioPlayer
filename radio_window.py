import vlc  # for checking player state
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QMovie
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QLineEdit,
    QComboBox,
    QSlider,
    QMessageBox,
    QGraphicsDropShadowEffect,
    QApplication
)

from title_bar import TitleBar
from radio_player import RadioPlayer
from api import FetchStationsWorker  # If you have a worker thread class here
from constants import AFRICAN_COUNTRIES
from styles import LOAD_STYLESHEET  # We'll define LOAD_STYLESHEET in styles.py

import os
import sys

class RadioWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smooth African Radio Player")

        # We want a frameless window with rounded corners
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Create an instance of the RadioPlayer (the VLC logic part)
        self.radio_player = RadioPlayer()

        # Keep track of stations and currently selected item
        self.all_stations = []
        self.current_station_item = None

        # Build the UI
        self.init_ui()

        # (Optional) Fetch initial country's stations at startup
        self.load_country_stations("Nigeria")
    
    def resource_path(relative_path):
        """ Get the absolute path to the resource, works for dev and PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def init_ui(self):
        """
        Sets up the main layout, the title bar, the body container,
        plus the station list, controls, and the spinner.
        """
        # Apply external stylesheet
        self.setStyleSheet(LOAD_STYLESHEET())

        # Main layout for the entire window
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # ---- Title Bar ----
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)

        # ---- Body Container (with gradient, etc.) ----
        self.body_container = QWidget()
        self.body_container.setObjectName("Container")  # Matches "QWidget#Container" in the stylesheet
        self.main_layout.addWidget(self.body_container)

        # Layout inside the body container
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(20, 20, 20, 20)
        self.body_container.setLayout(self.body_layout)

        # Optional drop shadow on body_container
        shadow = QGraphicsDropShadowEffect(self.body_container)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.body_container.setGraphicsEffect(shadow)

        # ---- Station Selection Area ----
        station_layout = QHBoxLayout()
        self.body_layout.addLayout(station_layout)

        # Country combo
        self.country_combo = QComboBox()
        self.country_combo.addItems(AFRICAN_COUNTRIES)
        self.country_combo.currentIndexChanged.connect(self.on_country_changed)
        station_layout.addWidget(self.country_combo)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search station...")
        self.search_bar.textChanged.connect(self.on_search_text_changed)
        station_layout.addWidget(self.search_bar)

        # Random station button
        self.random_button = QPushButton("Random Station")
        self.random_button.clicked.connect(self.play_random_station)
        station_layout.addWidget(self.random_button)

        # ---- Station List ----
        self.station_list = QListWidget()
        self.station_list.itemDoubleClicked.connect(self.on_station_double_clicked)
        self.body_layout.addWidget(self.station_list)

        # ---- Controls Layout (Play, Stop, Volume) ----
        controls_layout = QHBoxLayout()
        self.body_layout.addLayout(controls_layout)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_selected_station)
        controls_layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_station)
        controls_layout.addWidget(self.stop_button)

        volume_label = QLabel("Volume")
        controls_layout.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(60)
        self.volume_slider.valueChanged.connect(self.set_volume)
        controls_layout.addWidget(self.volume_slider)

        # ---- Now Playing Label ----
        self.now_playing_label = QLabel("Now playing: Nothing")
        self.now_playing_label.setObjectName("NowPlayingLabel")
        self.body_layout.addWidget(self.now_playing_label)

        # ---- Spinner (Loading GIF) ----
        self.spinner_label = QLabel()
        self.spinner_label.setObjectName("SpinnerLabel")
        self.spinner_label.setFixedSize(64, 64)  # Adjust as needed
        self.spinner_label.setScaledContents(True)

        # Load the spinner GIF (place spinner.gif in your assets folder)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        spinner_movie = QMovie(base_path + "/assets/spinner.gif")
        self.spinner_label.setMovie(spinner_movie)
        spinner_movie.start()

        # Hide spinner by default
        self.spinner_label.hide()

        # Add spinner at the bottom of body_layout (or anywhere you like)
        self.body_layout.addWidget(self.spinner_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Initial window size
        self.resize(640, 520)

    # -------------------- Spinner Controls --------------------
    def show_spinner(self):
        """Show the spinner label while loading or playing."""
        self.spinner_label.show()
        QApplication.processEvents()  # Make sure the spinner can update immediately

    def hide_spinner(self):
        """Hide the spinner when done."""
        self.spinner_label.hide()

    # -------------------- Station Fetching --------------------
    def on_country_changed(self):
        """User changed the country combo—fetch new stations."""
        selected_country = self.country_combo.currentText()
        self.load_country_stations(selected_country)

    def load_country_stations(self, country):
        """
        Uses a background worker to fetch stations so the UI won't freeze.
        If you don't use threading, you can fetch directly (but UI might freeze).
        """
        self.station_list.clear()
        self.station_list.addItem("[Loading stations...]")

        # Show spinner while fetching
        self.show_spinner()

        # Create the worker
        self.fetch_stations_worker = FetchStationsWorker(country)
        self.fetch_stations_worker.finished.connect(self.on_stations_fetched)
        self.fetch_stations_worker.start()

    def on_stations_fetched(self, stations):
        """Called when FetchStationsWorker finishes: update the station list."""
        self.hide_spinner()

        self.station_list.clear()
        self.all_stations = stations or []

        if not self.all_stations:
            self.station_list.addItem("[No stations found]")
            return

        for station in self.all_stations:
            station_name = station.get("name", "Unknown Station")
            self.station_list.addItem(station_name)

    # -------------------- Search / Filter --------------------
    def on_search_text_changed(self, text):
        """Filter stations by search text (case-insensitive)."""
        self.station_list.clear()
        filtered = [s for s in self.all_stations if text.lower() in s.get("name", "").lower()]
        if not filtered:
            self.station_list.addItem("[No results found]")
            return

        for station in filtered:
            self.station_list.addItem(station.get("name", "Unknown Station"))

    # -------------------- Play / Stop Logic --------------------
    def on_station_double_clicked(self, item):
        """Double-click plays the selected station (unless placeholder)."""
        if "[No" in item.text():
            return
        self.play_selected_station()

    def play_selected_station(self):
        """Play whichever station is selected in the list and show the spinner until music starts."""
        selected_items = self.station_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No selection", "Please select a station.")
            return

        self.show_spinner()

        station_name = selected_items[0].text()
        if "[No" in station_name:
            self.hide_spinner()
            return

        # Find station data
        station_data = next((s for s in self.all_stations if s.get("name") == station_name), None)
        if station_data:
            url = station_data.get("url")
            if url:
                # Start playing
                self.radio_player.play_station(url)
                self.highlight_station(selected_items[0])
                self.now_playing_label.setText(f"Now playing: {station_name}")

                # Check if/when VLC is actually in the Playing state
                self.wait_for_playing()
            else:
                QMessageBox.warning(self, "No Stream URL", f"Station {station_name} has no stream URL.")
                self.hide_spinner()
        else:
            QMessageBox.warning(self, "Not Found", f"Could not find data for station: {station_name}.")
            self.hide_spinner()

    def wait_for_playing(self):
        """
        Poll the VLC player's state every 100 ms.
        Hide the spinner as soon as it equals vlc.State.Playing.
        """
        state = self.radio_player.get_state()  # e.g. self._player.get_state()
        if state == vlc.State.Playing:
            # Music should be audible now
            self.hide_spinner()
        else:
            # Try again in 100 ms
            QTimer.singleShot(100, self.wait_for_playing)

    def stop_station(self):
        """Stop playback."""
        self.radio_player.stop_station()
        self.now_playing_label.setText("Now playing: Nothing")
        self.unhighlight_previous_station()

    def play_random_station(self):
        """Pick a random station from the list (that has a valid URL)."""
        if not self.all_stations:
            QMessageBox.information(self, "No Stations", "No stations available.")
            return

        from random import choice
        valid_stations = [s for s in self.all_stations if s.get("url")]
        if not valid_stations:
            QMessageBox.warning(self, "No Valid Streams", "No station has a valid stream URL.")
            return

        self.show_spinner()
        station = choice(valid_stations)
        name = station.get("name", "Unknown Station")
        url = station["url"]  # guaranteed to exist from valid_stations

        self.radio_player.play_station(url)
        self.now_playing_label.setText(f"Now playing: {name}")

        # Highlight in the list
        matches = self.station_list.findItems(name, Qt.MatchFlag.MatchExactly)
        if matches:
            self.highlight_station(matches[0])
            self.station_list.setCurrentItem(matches[0])

        # Poll for playing state
        self.wait_for_playing()

    def set_volume(self, volume):
        """Adjust volume in the RadioPlayer."""
        self.radio_player.set_volume(volume)

    # -------------------- Highlighting Items --------------------
    def highlight_station(self, item):
        """Bold the newly playing station."""
        self.unhighlight_previous_station()
        self.current_station_item = item
        font = item.font()
        font.setBold(True)
        item.setFont(font)

    def unhighlight_previous_station(self):
        """Revert previously bold item to normal."""
        if self.current_station_item:
            font = self.current_station_item.font()
            font.setBold(False)
            self.current_station_item.setFont(font)
            self.current_station_item = None
