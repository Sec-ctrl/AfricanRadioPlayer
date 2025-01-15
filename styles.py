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
            /* Container with gradient background and rounded corners */
            #Container {{
                border-radius: 16px;
                background: qlineargradient(
                    spread:pad, 
                    x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(52, 59, 69, 1), 
                    stop:1 rgba(58, 69, 85, 1)
                );
            }}

            /* Title label at the top */
            #TitleLabel {{
                color: #ECEFF4;
            }}

            /* Basic push buttons */
            QPushButton {{
                background-color: #4C566A;
                color: #ECEFF4;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 10pt;
            }}
            /* Hover effect */
            QPushButton:hover {{
                background-color: #5E81AC;
            }}

            /* Minimize and close button icons */
            #MinButton {{
                background-image: url("{minimize_icon_path}");
                background-repeat: no-repeat;
                background-position: center;
                background-color: transparent;
                border: none;
                width: 32px;
                height: 32px;
            }}
            #MinButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            #CloseButton {{
                background-image: url("{close_icon_path}");
                background-repeat: no-repeat;
                background-position: center;
                background-color: transparent;
                border: none;
                width: 32px;
                height: 32px;
            }}
            #CloseButton:hover {{
                background-color: rgba(255, 0, 0, 0.3);
            }}

            /* QLineEdit (search bar) */
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

            /* QComboBox */
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

            /* QListWidget */
            QListWidget {{
                background-color: rgba(255,255,255,0.06);
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 10px;
            }}
            QListWidget::item:selected {{
                background-color: #5E81AC;
            }}

            /* Labels, e.g. "Volume" */
            QLabel {{
                color: #ECEFF4;
            }}

            /* Volume slider */
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
            /* Now Playing Label */
            #NowPlayingLabel {{
                font-size: 10pt;
                color: #A3BE8C;
                background-color: rgba(255,255,255,0.1);
                border: 1px solid #4C566A;
                border-radius: 8px;
                padding: 8px;
            }}
        """
