from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton

class Favorites(QWidget):
    """
    Favorites class widget for the RadioWindow.
    This widget displays the list of favorite radio stations.
    """
    # Define the signal to emit the station name when double-clicked
    station_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Reference to the main window using this widget
        self.init_ui()

    def init_ui(self):
        """
        Sets up the UI for the Favorites section.
        """
        # Set the layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        # Favorites label
        self.favorites_label = QLabel("Favorites")
        self.favorites_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.favorites_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.favorites_label)

        # Favorites list
        self.favorites_list = QListWidget()
        self.favorites_list.itemDoubleClicked.connect(self.on_item_double_clicked)  # Connect double-click signal
        self.layout.addWidget(self.favorites_list)

        # Clear favorites button
        self.clear_button = QPushButton("Clear Favorites")
        self.clear_button.clicked.connect(self.clear_favorites)
        self.layout.addWidget(self.clear_button)

    def is_favorite(self, station_name):
        """Check if a station is in the favorites list."""
        return station_name in [self.favorites_list.item(i).text() for i in range(self.favorites_list.count())]

    def add_favorite(self, station_name):
        """
        Adds a station to the Favorites list.
        """
        existing_items = [self.favorites_list.item(i).text() for i in range(self.favorites_list.count())]
        if station_name not in existing_items:
            self.favorites_list.addItem(station_name)
        else:
            if self.parent_window:
                self.parent_window.show_message("Already Added", f"{station_name} is already in your Favorites.")

    def remove_favorite(self, station_name):
        """
        Removes a station from the Favorites list by name.
        """
        for i in range(self.favorites_list.count()):
            if self.favorites_list.item(i).text() == station_name:
                self.favorites_list.takeItem(i)
                break

    def clear_favorites(self):
        """
        Clears all items from the Favorites list.
        """
        self.favorites_list.clear()
        if self.parent_window:
            self.parent_window.show_message("Cleared", "All Favorites have been cleared.")

    def on_item_double_clicked(self, item):
        """Emit the station name when a favorite station is double-clicked."""
        station_name = item.text()
        self.station_selected.emit(station_name)  # Emit the signal with the selected station name
