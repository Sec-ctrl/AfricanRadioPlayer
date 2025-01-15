import vlc  # for checking player state
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QRectF
from PyQt6.QtGui import QFont, QColor, QMovie, QIcon, QRegion, QPainterPath
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
    QApplication,
    QToolButton,
    QListWidgetItem
)

from title_bar import TitleBar
from favorites import Favorites
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
        self.apply_rounded_corners()

        # Create an instance of the RadioPlayer (the VLC logic part)
        self.radio_player = RadioPlayer()

        # Keep track of stations and currently selected item
        self.all_stations = []
        self.current_station_item = None

        # Build the UI
        self.init_ui()

        # (Optional) Fetch initial country's stations at startup
        self.load_country_stations("Nigeria")

    def apply_rounded_corners(self):
        """Set a mask to create rounded corners for the window."""
        radius = 20  # Corner radius
        rect = QRectF(self.rect())  # Convert QRect to QRectF for compatibility

        # Create a QPainterPath for rounded rectangle
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        # Convert the path to a QRegion
        rounded_region = QRegion(path.toFillPolygon().toPolygon())

        # Apply the mask
        self.setMask(rounded_region)

    def resizeEvent(self, event):
        """Reapply rounded corners on resize."""
        super().resizeEvent(event)
        self.apply_rounded_corners()
    
    def resource_path(self, relative_path):
        """ Get the absolute path to the resource, works for dev and PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def init_ui(self):
        """
        Initializes the UI with a collapsible sidebar.
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

        # ---- Body and Sidebar Container ----
        self.body_and_sidebar = QHBoxLayout()
        self.body_and_sidebar.setContentsMargins(20, 20, 20, 20)
        self.main_layout.addLayout(self.body_and_sidebar)

        # ---- Main Body ----
        self.body_container = QWidget()
        self.body_container.setObjectName("Container")
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_container.setLayout(self.body_layout)

        # Add the body container to the horizontal layout
        self.body_and_sidebar.addWidget(self.body_container, stretch=3)

        # ---- Sidebar Toggle Button ----
        self.toggle_button = QToolButton()
        # Default to "hide arrow" if the sidebar is shown by default
        self.toggle_button.setIcon(QIcon(self.resource_path("assets/left_arrow2.png")))
        self.toggle_button.setIconSize(QSize(24, 24))
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        self.toggle_button.setFixedSize(30, 30)
        self.toggle_button.setObjectName("ToggleButton")

        # Insert the toggle button between the main body and the Favorites widget
        self.body_and_sidebar.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignTop)

        # ---- Favorites Sidebar ----
        self.favorites_widget = Favorites(self)
        self.favorites_widget.station_selected.connect(self.play_favorite_station)  # Connect signal
        self.body_and_sidebar.addWidget(self.favorites_widget, stretch=1)

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

        # ---- Controls Layout ----
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

        # ---- Spinner ----
        self.spinner_label = QLabel()
        self.spinner_label.setObjectName("SpinnerLabel")
        self.spinner_label.setFixedSize(64, 64)
        self.spinner_label.setScaledContents(True)

        # Load spinner GIF
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        spinner_movie = QMovie(base_path + "/assets/spinner.gif")
        self.spinner_label.setMovie(spinner_movie)
        spinner_movie.start()

        # Hide spinner by default
        self.spinner_label.hide()
        self.body_layout.addWidget(self.spinner_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Set initial window size
        self.resize(800, 520)

    # -------------------- Favorites --------------------
    def toggle_sidebar(self):
        """
        Toggles the visibility of the Favorites sidebar.
        Changes the icon of the toggle button to indicate show/hide.
        """
        if self.toggle_button.isChecked():
            # Hide sidebar
            self.favorites_widget.setVisible(False)
            self.body_and_sidebar.setStretch(0, 4)
            # Switch icon to 'right arrow' (means user can expand again)
            self.toggle_button.setIcon(QIcon(self.resource_path("assets/right_arrow2.png")))
        else:
            # Show sidebar
            self.favorites_widget.setVisible(True)
            self.body_and_sidebar.setStretch(0, 3)
            self.body_and_sidebar.setStretch(1, 1)
            # Switch icon to 'left arrow' (means user can hide again)
            self.toggle_button.setIcon(QIcon(self.resource_path("assets/left_arrow2.png")))

    def populate_station_list(self, stations):
        """Populate the station list with favorite toggle icons."""
        self.station_list.clear()

        for station in stations:
            station_name = station.get("name", "Unknown Station")

            # Create a QWidget container for each station
            container_widget = QWidget()
            layout = QHBoxLayout(container_widget)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(10)

            # Add a star button
            star_button = QPushButton()
            star_button.setCheckable(True)
            star_button.setIcon(self._get_star_icon(station_name))
            star_button.clicked.connect(lambda _, s=station_name: self.toggle_favorite(s))
            star_button.setFixedSize(24, 24)  # Adjust size as needed
            layout.addWidget(star_button)

            # Add a label for the station name
            station_label = QLabel(station_name)
            layout.addWidget(station_label)

            # Adjust layout to prevent stretching
            layout.addStretch()

            # Add the station container to the QListWidget
            list_item = QListWidgetItem()
            list_item.setSizeHint(container_widget.sizeHint())

            # Add station name as data for easier selection handling
            list_item.setData(Qt.ItemDataRole.UserRole, station_name)

            self.station_list.addItem(list_item)
            self.station_list.setItemWidget(list_item, container_widget)

        # Allow item selection even with custom widgets
        self.station_list.itemClicked.connect(self.on_station_item_clicked)
    
    def on_station_item_clicked(self, item):
        """Handle station selection from the main station list."""
        station_name = item.data(Qt.ItemDataRole.UserRole)  # Get the station name
        if station_name:
            self.highlight_station(item)

    def toggle_favorite(self, station_name):
        """Toggle the favorite status of a station."""
        if self.favorites_widget.is_favorite(station_name):
            self.favorites_widget.remove_favorite(station_name)
        else:
            self.favorites_widget.add_favorite(station_name)

        # Update the star icon in the station list
        self.update_station_star_icon(station_name)
    
    def update_station_star_icon(self, station_name):
        """Update the star icon for a station based on favorite status."""
        for i in range(self.station_list.count()):
            list_item = self.station_list.item(i)
            container_widget = self.station_list.itemWidget(list_item)
            if container_widget:
                star_button = container_widget.findChild(QPushButton)
                station_label = container_widget.findChild(QLabel)

                # Match station name and update the star icon
                if station_label and star_button and station_label.text() == station_name:
                    star_button.setIcon(self._get_star_icon(station_name))
                    break
        
    def _get_star_icon(self, station_name):
        """Return the appropriate star icon based on favorite status."""
        if self.favorites_widget.is_favorite(station_name):
            return QIcon(self.resource_path("assets/star_full.png"))
        else:
            return QIcon(self.resource_path("assets/star_empty.png"))
    
    def play_favorite_station(self, station_name):
        """Play a station selected from the Favorites list."""
        # Unhighlight any station in the Main Station List
        self.unhighlight_previous_station()

        station_data = next((s for s in self.all_stations if s.get("name") == station_name), None)

        if station_data:
            url = station_data.get("url")
            if url:
                self.show_spinner()
                self.radio_player.play_station(url)
                self.now_playing_label.setText(f"Now playing: {station_name}")

                # Highlight the selected favorite
                self.highlight_favorite(station_name)

                self.wait_for_playing()
            else:
                QMessageBox.warning(self, "No Stream URL", f"Station {station_name} has no stream URL.")
        else:
            QMessageBox.warning(self, "Not Found", f"Station {station_name} not found in the main list.")
        
    
    def highlight_station_in_list(self, station_name):
        """Highlight the specified station in the main station list."""
        # Unhighlight any station in the Favorites List
        self.unhighlight_favorites()

        for i in range(self.station_list.count()):
            list_item = self.station_list.item(i)
            item_station_name = list_item.data(Qt.ItemDataRole.UserRole) or list_item.text()

            if item_station_name == station_name:
                self.station_list.setCurrentRow(i)  # Select the station
                self.highlight_station(list_item)  # Apply bold styling
                return

        print(f"Station not found: {station_name}")  # Debugging log

    def unhighlight_favorites(self):
        """Remove selection from the Favorites List."""
        selected_item = self.favorites_widget.favorites_list.currentItem()
        if selected_item:
            self.favorites_widget.favorites_list.setCurrentItem(None)  # Clear selection
            print(f"Unhighlighted favorite: {selected_item.text()}")  # Debugging log

    def highlight_favorite(self, station_name):
        """Highlight the specified station in the Favorites List."""
        for i in range(self.favorites_widget.favorites_list.count()):
            favorite_item = self.favorites_widget.favorites_list.item(i)
            if favorite_item.text() == station_name:
                self.favorites_widget.favorites_list.setCurrentRow(i)  # Highlight the station
                print(f"Highlighted favorite: {favorite_item.text()}")  # Debugging log
                return
            
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
        self.hide_spinner()  # Hide spinner after fetching

        # Clear the existing station list
        self.station_list.clear()

        # Update the internal list of stations
        self.all_stations = stations or []

        if not self.all_stations:
            # Show a placeholder if no stations are found
            self.station_list.addItem("[No stations found]")
        else:
            # Populate the station list with stations and favorite icons
            self.populate_station_list(self.all_stations)

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
        """Play the currently selected station, either from the main list or favorites."""
        selected_items = self.station_list.selectedItems()

        if not selected_items:
            selected_favorite = self.favorites_widget.favorites_list.currentItem()
            if selected_favorite:
                station_name = selected_favorite.text()
                self.play_favorite_station(station_name)
            else:
                QMessageBox.warning(self, "No selection", "Please select a station.")
            return

        station_name = selected_items[0].data(Qt.ItemDataRole.UserRole) or selected_items[0].text()
        if "[No" in station_name:
            self.hide_spinner()
            return

        station_data = next((s for s in self.all_stations if s.get("name") == station_name), None)
        if station_data:
            url = station_data.get("url")
            if url:
                self.show_spinner()
                self.radio_player.play_station(url)
                self.highlight_station_in_list(station_name)  # Ensure it's highlighted
                self.now_playing_label.setText(f"Now playing: {station_name}")
                self.wait_for_playing()
            else:
                QMessageBox.warning(self, "No Stream URL", f"Station {station_name} has no stream URL.")
        else:
            QMessageBox.warning(self, "Not Found", f"Could not find data for station: {station_name}.")

    def wait_for_playing(self):
        """
        Poll the VLC player's state every 100 ms.
        Hide the spinner as soon as it equals vlc.State.Playing.
        """
        state = self.radio_player.get_state()
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
        """Bold the newly playing station in the main list."""
        print(f"Highlighting item: {item.text()}")  # Debugging log

        self.unhighlight_previous_station()  # Remove bold from the previously highlighted item
        self.current_station_item = item

        container_widget = self.station_list.itemWidget(item)
        if container_widget:
            # Apply bold font to the QLabel in the custom widget
            station_label = container_widget.findChild(QLabel)
            if station_label:
                font = station_label.font()
                font.setBold(True)
                station_label.setFont(font)
                print(f"Bold applied to custom widget: {station_label.text()}")  # Debugging log
        else:
            # Fallback for plain QListWidgetItem
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            print(f"Bold applied to QListWidgetItem: {item.text()}")  # Debugging log

    def unhighlight_previous_station(self):
        """Remove bold formatting from the previously highlighted station."""
        if self.current_station_item:
            container_widget = self.station_list.itemWidget(self.current_station_item)
            if container_widget:
                # Reset the QLabel font in the custom widget
                station_label = container_widget.findChild(QLabel)
                if station_label:
                    font = station_label.font()
                    font.setBold(False)
                    station_label.setFont(font)
                    print(f"Unbolded custom widget: {station_label.text()}")  # Debugging log
            else:
                # Handle plain QListWidgetItem
                font = self.current_station_item.font()
                font.setBold(False)
                self.current_station_item.setFont(font)
                print(f"Unbolded QListWidgetItem: {self.current_station_item.text()}")  # Debugging log

            # Clear the current station reference
            self.current_station_item = None

        # Clear selection in the Favorites List
        self.favorites_widget.favorites_list.clearSelection()