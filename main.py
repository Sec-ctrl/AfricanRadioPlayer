# main.py

import sys
from PyQt6.QtWidgets import QApplication
from radio_player import RadioPlayer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    radio_player = RadioPlayer()
    radio_player.show()
    sys.exit(app.exec())

# pyinstaller --onefile --windowed --add-data "assets;assets" --name "SmoothAfricanRadioPlayer" main.py --specpath . --icon=assets/icon.ico