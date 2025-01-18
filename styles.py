def LOAD_STYLESHEET():
    return f"""
        /* Main window */
        QWidget {{
            background: 2C3440; 
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
            color: #ECEFF4;
        }}

        /* Title bar */
        #TitleBar {{
            background: qlineargradient(
                spread: pad,
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 rgba(45, 52, 61, 1),
                stop: 1 rgba(50, 60, 75, 1)
            );
            border-radius: 16px 16px 0 0;
            padding: 8px;
        }}

        /* Title label */
        #TitleLabel {{
            font-size: 14pt;
            font-weight: bold;
            color: #A3BE8C;
            padding-left: 10px;
            background: transparent;
        }}

        /* Sidebar toggle button */
        #ToggleButton {{
            background: transparent;
            border: none;
            border-radius: 8px;
            width: 30px;
            height: 30px;
        }}
        #ToggleButton:hover {{
            background-color: rgba(255, 255, 255, 0.1);
        }}

        /* Station list */
        QListWidget {{
            background-color: rgba(255, 255, 255, 0.07);
            border: 1px solid #4C566A;
            border-radius: 10px;
            padding: 4px;
        }}
        QListWidget::item {{
            padding: 2px 6px; /* Reduced padding for compactness */
            border-radius: 6px;
            color: #ECEFF4;
            font-size: 10pt; /* Smaller font size for compact view */
        }}
        QListWidget::item:hover {{
            background-color: rgba(88, 192, 208, 0.2); /* Subtle hover effect */
        }}
        QListWidget::item:selected {{
            background-color: rgba(88, 192, 208, 0.4);
            color: #ECEFF4;
            font-weight: bold;
        }}

        /* Buttons */
        QPushButton {{
            background-color: #4C566A;
            color: #ECEFF4;
            border: none;
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 9pt;
        }}
        QPushButton:hover {{
            background-color: #5E81AC;
        }}
        QPushButton:pressed {{
            background-color: #3B4252;
        }}

        /* Input fields (Search Bar, Combo Box, etc.) */
        QLineEdit, QComboBox {{
            background-color: rgba(255, 255, 255, 0.1);
            color: #ECEFF4;
            border: 1px solid #4C566A;
            border-radius: 10px;
            padding: 4px 8px;
        }}
        QLineEdit:focus, QComboBox:hover {{
            border: 1px solid #88C0D0;
        }}
        QComboBox QAbstractItemView {{
            background-color: #4C566A;
            selection-background-color: #5E81AC;
            border-radius: 6px;
            padding: 2px;
        }}

        /* Sliders */
        QSlider::groove:horizontal {{
            background: #4C566A; /* Flat background color */
            height: 6px;
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: #88C0D0;
            width: 14px; /* Compact handle size */
            height: 14px;
            border-radius: 7px;
            margin: -4px 0; /* Center handle in the groove */
        }}
        QSlider::handle:horizontal:hover {{
            background: #81A1C1;
        }}

        /* Labels */
        QLabel {{
            color: #ECEFF4;
            font-size: 9pt; /* Reduced size for compact styling */
        }}
        QLabel[role="volumeLabel"] {{
            font-size: 10pt;
            font-weight: bold;
            margin-right: 8px;
        }}

        /* Now Playing label */
        #NowPlayingLabel {{
            font-size: 11pt;
            color: #A3BE8C;
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid #4C566A;
            border-radius: 8px;
            padding: 6px;
        }}

        /* Spinner */
        #SpinnerLabel {{
            border: none;
            background: transparent;
        }}
    """
