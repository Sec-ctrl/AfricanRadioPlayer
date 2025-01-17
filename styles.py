import os
import sys

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def LOAD_STYLESHEET():
    assets_path = resource_path("assets")
    minimize_icon_path = os.path.join(assets_path, "minimize_icon.svg").replace("\\", "/")
    close_icon_path = os.path.join(assets_path, "close_icon.svg").replace("\\", "/")
    return f"""
            /* Main window container */
            QWidget {{
                background: qlineargradient(
                    spread: pad,
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 1 rgba(45, 52, 61, 1),
                    stop: 0 rgba(50, 60, 75, 1)
                );
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
                color: #ECEFF4;
            }}

            /* Container */
            #Container {{
                border-radius: 20px;
                background: transparent;
            }}

            /* Title label */
            #TitleLabel {{
                color: #ECEFF4;
                font-size: 12pt;
                font-weight: bold;
            }}

            /* Buttons */
            QPushButton {{
                background-color: #4C566A;
                color: #ECEFF4;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: #5E81AC;
            }}

            /* Toggle button */
            QToolButton#ToggleButton {{
                background: transparent;
                border: none;
                padding: 0;
            }}
            QToolButton#ToggleButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }}

            /* Minimize and close buttons */
            #MinButton, #CloseButton {{
                background-repeat: no-repeat;
                background-position: center;
                background-color: transparent;
                border: none;
                width: 16px;
                height: 16px;
            }}
            #MinButton {{
                width: 50px; /* Adjust size */
                height: 50px;
                
            }}
            #CloseButton {{
                width: 50px; /* Adjust size */
                height: 50px;
            }}
            #MinButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            #CloseButton:hover {{
                background-color: rgba(255, 0, 0, 0.3);
                border-radius: 8px;
            }}

            /* Search bar */
            QLineEdit {{
                background-color: rgba(255,255,255,0.1);
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 10px;
                padding: 6px 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid #88C0D0;
            }}

            /* Combo box */
            QComboBox {{
                background-color: rgba(255,255,255,0.1);
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 10px;
                padding: 6px 12px;
            }}
            QComboBox:hover, QComboBox:focus {{
                border: 1px solid #88C0D0;
            }}
            QComboBox QAbstractItemView {{
                background-color: #4C566A;
                selection-background-color: #5E81AC;
                border-radius: 4px;
            }}

           /* List widget */
            QListWidget {{
                border: 1px solid #4C566A;
                border-radius: 10px;
                padding: 8px;
            }}

            QListWidget::item:selected {{
                background-color: rgba(88, 192, 208, 0.5); /* Light transparent highlight */
                color: #ECEFF4; /* Ensure selected text remains visible */
            }}

            /* Labels */
            QLabel {{
                color: #ECEFF4;
                font-size: 10pt;
            }}

            /* Slider */
            QSlider::groove:horizontal {{
                background: #434C5E;
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: #88C0D0;
                width: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }}
            QSlider::handle:horizontal:hover {{
                background: #81A1C1;
            }}

            /* Now Playing label */
            #NowPlayingLabel {{
                font-size: 10pt;
                color: #A3BE8C;
                background-color: rgba(255,255,255,0.1);
                border: 1px solid #4C566A;
                border-radius: 8px;
                padding: 8px;
            }}
        """
