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
        self.favorites = []
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

    def add_favorite(self, station_data):
        """
        Add a station to the favorites list.
        Args:
            station_data (dict): A dictionary containing 'name' and 'country' keys.
        """
        if station_data not in self.favorites:
            self.favorites.append(station_data)

            # Add the station name to the QListWidget for display
            station_name = station_data["name"]
            self.favorites_list.addItem(station_name)

            # Update the UI
            self.update_favorites_list()

    def remove_favorite(self, station_name):
        """
        Remove a station from the favorites list.
        Args:
            station_name (str): The name of the station to remove.
        """
        self.favorites = [f for f in self.favorites if f["name"] != station_name]

        # Remove the station from the QListWidget
        items = self.favorites_list.findItems(station_name, Qt.MatchFlag.MatchExactly)
        for item in items:
            self.favorites_list.takeItem(self.favorites_list.row(item))

        # Update the UI
        self.update_favorites_list()

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

    def get_favorite_data(self, station_name):
        """
        Get the favorite data (dict) for the given station name.
        Args:
            station_name (str): The name of the station.
        Returns:
            dict or None: The favorite data or None if not found.
        """
        return next((f for f in self.favorites if f["name"] == station_name), None)
    
    def update_favorites_list(self):
        """
        Refresh the favorites list display in the QListWidget.
        This ensures the UI reflects the current state of the favorites.
        """
        self.favorites_list.clear()  # Clear the current display

        # Add all favorites back to the QListWidget
        for favorite in self.favorites:
            self.favorites_list.addItem(favorite["name"])