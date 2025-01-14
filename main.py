import sys
from PyQt6.QtWidgets import QApplication
from radio_window import RadioWindow

def main():
    app = QApplication(sys.argv)
    window = RadioWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
