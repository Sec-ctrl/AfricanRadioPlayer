# radio_player.py
import random
import vlc

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QLineEdit, QComboBox, QSlider, QMessageBox,
    QGraphicsDropShadowEffect
)

from api import fetch_stations_by_country
from constants import AFRICAN_COUNTRIES


class RadioPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smooth African Radio Player")

        # We want a frameless window with rounded corners
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Apply a drop shadow effect to the main widget
        self.apply_drop_shadow()

        # Set up VLC player
        self.player = vlc.MediaPlayer()

        # Keep track of the last station played
        self.current_station_url = ""

        # Build the UI
        self.init_ui()

        # A variable to hold the station data
        self.all_stations = []

        # Fetch initial country’s stations (optional, set a default)
        self.load_country_stations("Nigeria")

        # For window dragging
        self.old_pos = None

    def apply_drop_shadow(self):
        """Apply a drop shadow to the entire window (for a modern 'floating' look)."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 180))  # semi-transparent black
        self.setGraphicsEffect(shadow)

    def init_ui(self):
        """
        Build the overall UI layout.
        """
        # Main layout
        self.main_layout = QVBoxLayout()
        # We add a little extra margin for the shadow
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # The container widget that has the rounded corners and gradient background
        self.container = QWidget(self)
        self.container.setObjectName("Container")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.addWidget(self.container)

        # Top bar (for dragging, close, minimize)
        self.title_bar = self.create_title_bar()
        self.container_layout.addLayout(self.title_bar)

        # Station selection layout
        station_layout = QHBoxLayout()
        station_layout.setSpacing(10)

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

        self.container_layout.addLayout(station_layout)

        # List of stations
        self.station_list = QListWidget()
        self.station_list.itemDoubleClicked.connect(self.on_station_double_clicked)
        self.container_layout.addWidget(self.station_list)

        # Play/Stop controls layout
        controls_layout = QHBoxLayout()

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_selected_station)
        controls_layout.addWidget(self.play_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_station)
        controls_layout.addWidget(self.stop_button)

        # Volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(60)  # Default volume
        self.volume_slider.valueChanged.connect(self.set_volume)

        # A small sub-layout for volume
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(5)
        volume_label = QLabel("Volume")
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)

        controls_layout.addLayout(volume_layout)
        self.container_layout.addLayout(controls_layout)

        # Apply styling
        self.apply_styles()

        # Set a reasonable size
        self.resize(640, 520)

    def create_title_bar(self):
        """
        Creates a custom title bar with 'Close' and 'Minimize' buttons.
        """
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)

        # The 'title' label
        self.title_label = QLabel("Smooth African Radio Player")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)
        self.title_label.setObjectName("TitleLabel")
        title_layout.addWidget(self.title_label)

        # Stretch so buttons go to the right
        title_layout.addStretch()

        # Minimize button
        self.minimize_button = QPushButton()
        self.minimize_button.setObjectName("MinButton")
        self.minimize_button.setToolTip("Minimize")
        self.minimize_button.setFixedSize(32, 16)
        self.minimize_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.minimize_button)

        # Close button
        self.close_button = QPushButton()
        self.close_button.setObjectName("CloseButton")
        self.close_button.setToolTip("Close")
        self.close_button.setFixedSize(32, 32)
        self.close_button.clicked.connect(self.close)
        title_layout.addWidget(self.close_button)

        return title_layout

    def apply_styles(self):
        """
        Apply the stylesheet to get a smooth, modern look, using
        inline SVG icons with forward slashes and removing transitions.
        """
        self.setStyleSheet("""
            /* Container with gradient background and rounded corners */
            #Container {
                border-radius: 16px;
                background: qlineargradient(
                    spread:pad, 
                    x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(52, 59, 69, 1), 
                    stop:1 rgba(58, 69, 85, 1)
                );
            }

            /* Title label at the top */
            #TitleLabel {
                color: #ECEFF4;
            }

            /* Basic push buttons */
            QPushButton {
                background-color: #4C566A;
                color: #ECEFF4;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 10pt;
            }
            /* Hover effect */
            QPushButton:hover {
                background-color: #5E81AC;
            }

            /* Minimize and close button icons (single-line, forward slashes) */
            #MinButton {
                background: url(assets/minimize_icon.svg) no-repeat center center;
                background-color: transparent;
                border: none;
                width: 32px;
                height: 32px;
            }
            #MinButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            #CloseButton {
                background: url(assets/close_icon.svg) no-repeat center center;
                background-color: transparent;
                border: 2px solid red;  /* Temporary border for debugging */
                width: 32px;
                height: 32px;
            }
            #CloseButton:hover {
                background-color: rgba(255, 0, 0, 0.3);
            }

            /* QLineEdit (search bar) */
            QLineEdit {
                background-color: rgba(255,255,255,0.1);
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 10px;
                padding: 6px 12px;
            }
            QLineEdit:focus {
                border: 1px solid #88C0D0;
            }

            /* QComboBox */
            QComboBox {
                background-color: rgba(255,255,255,0.1);
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 10px;
                padding: 6px 12px;
            }
            QComboBox:hover, QComboBox:focus {
                border: 1px solid #88C0D0;
            }
            QComboBox QAbstractItemView {
                background-color: #4C566A;
                selection-background-color: #5E81AC;
                border-radius: 4px;
            }

            /* QListWidget */
            QListWidget {
                background-color: rgba(255,255,255,0.06);
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 10px;
            }

            /* Labels, e.g. "Volume" */
            QLabel {
                color: #ECEFF4;
            }

            /* Volume slider */
            QSlider::groove:horizontal {
                background: #434C5E;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #88C0D0;
                width: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #81A1C1;
            }
        """)

    # Window dragging events
    def mousePressEvent(self, event):
        # Limit dragging to top ~60px (title bar area) to avoid confusion
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() < 60:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    # Event handlers
    def on_country_changed(self):
        selected_country = self.country_combo.currentText()
        self.load_country_stations(selected_country)

    def load_country_stations(self, country):
        self.station_list.clear()
        self.all_stations = fetch_stations_by_country(country)
        for station in self.all_stations:
            name = station.get("name", "Unknown Station")
            self.station_list.addItem(name)

    def on_search_text_changed(self, text):
        self.station_list.clear()
        filtered = [
            st for st in self.all_stations
            if text.lower() in st.get("name", "").lower()
        ]
        for station in filtered:
            name = station.get("name", "Unknown Station")
            self.station_list.addItem(name)

    def on_station_double_clicked(self, item):
        self.play_selected_station()

    def play_selected_station(self):
        selected_items = self.station_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No selection", "Please select a station.")
            return

        selected_station_name = selected_items[0].text()
        station_data = next(
            (s for s in self.all_stations if s.get("name") == selected_station_name),
            None
        )

        if station_data:
            stream_url = station_data.get("url", "")
            if stream_url:
                self.current_station_url = stream_url
                self.start_playback(stream_url, station_data.get("name", "Unknown"))
            else:
                QMessageBox.warning(
                    self,
                    "No Stream URL",
                    f"Station {selected_station_name} has no stream URL."
                )

    def stop_station(self):
        self.player.stop()

    def start_playback(self, stream_url, station_name=""):
        print(f"Now playing: {station_name} - {stream_url}")
        media = vlc.Media(stream_url)
        self.player.set_media(media)
        self.player.play()

    def play_random_station(self):
        if not self.all_stations:
            QMessageBox.information(self, "No Stations", "No stations available.")
            return

        random_station = random.choice(self.all_stations)
        name = random_station.get("name", "Unknown Station")
        stream_url = random_station.get("url", "")

        if not stream_url:
            QMessageBox.warning(self, "No Stream URL", f"Station {name} has no stream URL.")
            return

        self.current_station_url = stream_url
        self.start_playback(stream_url, name)

    def set_volume(self, value):
        self.player.audio_set_volume(value)
