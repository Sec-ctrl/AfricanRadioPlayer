from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
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
    QGraphicsDropShadowEffect
)

from title_bar import TitleBar
from radio_player import RadioPlayer
from api import fetch_stations_by_country
from constants import AFRICAN_COUNTRIES
from styles import LOAD_STYLESHEET  # We'll define LOAD_STYLESHEET in styles.py

class RadioWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smooth African Radio Player")

        # We want a frameless window with rounded corners (for the entire main widget)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Create an instance of the RadioPlayer (the logic part)
        self.radio_player = RadioPlayer()

        # Keep track of stations
        self.all_stations = []
        self.current_station_item = None

        # Build the UI
        self.init_ui()

        # Fetch initial country’s stations (optional default)
        self.load_country_stations("Nigeria")

    def init_ui(self):
        # Overall layout (we'll put everything in a QVBoxLayout)
        self.setStyleSheet(LOAD_STYLESHEET())  # Load external stylesheet

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # ---- Title bar ----
        # Our custom TitleBar handles window dragging + close/minimize
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)

        # ---- Body container (for search box, station list, controls, etc.) ----
        self.body_container = QWidget()
        # IMPORTANT: objectName must match your CSS selector in styles.py
        self.body_container.setObjectName("Container")  
        self.main_layout.addWidget(self.body_container)

        # Give the container its own layout
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(20, 20, 20, 20)
        self.body_container.setLayout(self.body_layout)

        # Optional: Add a drop shadow to the body_container for a floating look
        shadow = QGraphicsDropShadowEffect(self.body_container)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.body_container.setGraphicsEffect(shadow)

        # Station selection area
        station_layout = QHBoxLayout()
        self.body_layout.addLayout(station_layout)

        # Country combo box
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

        # Station list
        self.station_list = QListWidget()
        self.station_list.itemDoubleClicked.connect(self.on_station_double_clicked)
        self.body_layout.addWidget(self.station_list)

        # Controls layout (Play, Stop, Volume)
        controls_layout = QHBoxLayout()
        self.body_layout.addLayout(controls_layout)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_selected_station)
        controls_layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_station)
        controls_layout.addWidget(self.stop_button)

        # Volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(60)
        self.volume_slider.valueChanged.connect(self.set_volume)

        volume_label = QLabel("Volume")
        controls_layout.addWidget(volume_label)
        controls_layout.addWidget(self.volume_slider)

        # "Now Playing" label
        self.now_playing_label = QLabel("Now playing: Nothing")
        self.now_playing_label.setObjectName("NowPlayingLabel")
        self.body_layout.addWidget(self.now_playing_label)

        # A decent initial size
        self.resize(640, 520)

    # -------------------- Event Handlers & Logic --------------------

    def on_country_changed(self):
        selected_country = self.country_combo.currentText()
        self.load_country_stations(selected_country)

    def load_country_stations(self, country):
        self.station_list.clear()
        self.all_stations = fetch_stations_by_country(country)
        if not self.all_stations:
            self.station_list.addItem("[No stations found]")
            return
        for station in self.all_stations:
            self.station_list.addItem(station.get("name", "Unknown Station"))

    def on_search_text_changed(self, text):
        self.station_list.clear()
        filtered = [st for st in self.all_stations if text.lower() in st["name"].lower()]
        if not filtered:
            self.station_list.addItem("[No results found]")
            return
        for station in filtered:
            self.station_list.addItem(station.get("name", "Unknown Station"))

    def on_station_double_clicked(self, item):
        if "[No" in item.text():
            return
        self.play_selected_station()

    def play_selected_station(self):
        selected_items = self.station_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No selection", "Please select a station.")
            return

        station_name = selected_items[0].text()
        if "[No" in station_name:
            return

        # Find that station's data
        station_data = next((s for s in self.all_stations if s["name"] == station_name), None)
        if station_data:
            url = station_data.get("url", "")
            if url:
                self.radio_player.play_station(url)
                self.highlight_station(selected_items[0])
                self.now_playing_label.setText(f"Now playing: {station_name}")
            else:
                QMessageBox.warning(self, "No Stream URL", f"Station {station_name} has no stream URL.")

    def stop_station(self):
        self.radio_player.stop_station()
        self.now_playing_label.setText("Now playing: Nothing")
        self.unhighlight_previous_station()

    def play_random_station(self):
        if not self.all_stations:
            QMessageBox.information(self, "No Stations", "No stations available.")
            return
        from random import choice
        station = choice(self.all_stations)
        name = station.get("name", "Unknown Station")
        url = station.get("url", "")
        if not url:
            QMessageBox.warning(self, "No Stream URL", f"Station {name} has no stream URL.")
            return
        self.radio_player.play_station(url)
        self.now_playing_label.setText(f"Now playing: {name}")

        # Highlight in the list
        matches = self.station_list.findItems(name, Qt.MatchFlag.MatchExactly)
        if matches:
            self.highlight_station(matches[0])
            self.station_list.setCurrentItem(matches[0])

    def set_volume(self, volume):
        self.radio_player.set_volume(volume)

    # -------------------- Highlighting Items --------------------

    def highlight_station(self, item):
        self.unhighlight_previous_station()
        self.current_station_item = item
        font = item.font()
        font.setBold(True)
        item.setFont(font)

    def unhighlight_previous_station(self):
        if self.current_station_item:
            font = self.current_station_item.font()
            font.setBold(False)
            self.current_station_item.setFont(font)
            self.current_station_item = None
