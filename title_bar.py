from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

class TitleBar(QWidget):
    """
    A custom title bar widget with close/minimize buttons and drag support.
    This widget is placed at the top of RadioWindow's layout.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # The main window using this title bar

        self.old_pos = None  # For dragging
        self.init_ui()

        # Make sure it's drawn on top (useful if the parent has a gradient)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Title label
        self.title_label = QLabel("Smooth African Radio Player")
        self.layout.addWidget(self.title_label)

        # Push contents to the right
        self.layout.addStretch()

        # Minimize button
        self.min_button = QPushButton()
        self.min_button.setObjectName("MinButton")  # for styling via stylesheet
        self.min_button.setFixedSize(32, 16)
        self.min_button.setToolTip("Minimize")
        self.min_button.clicked.connect(self.on_minimize)
        self.layout.addWidget(self.min_button)

        # Close button
        self.close_button = QPushButton()
        self.close_button.setObjectName("CloseButton")
        self.close_button.setFixedSize(32, 32)
        self.close_button.setToolTip("Close")
        self.close_button.clicked.connect(self.on_close)
        self.layout.addWidget(self.close_button)

    # ------------ Dragging Logic ------------

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            # Move the parent window
            self.parent_window.move(self.parent_window.x() + delta.x(), self.parent_window.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    # ------------ Button Slots ------------

    def on_minimize(self):
        if self.parent_window:
            self.parent_window.showMinimized()

    def on_close(self):
        if self.parent_window:
            self.parent_window.close()
