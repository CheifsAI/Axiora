from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit,
                               QPushButton, QVBoxLayout, QWidget, QLabel,
                               QScrollArea, QSizePolicy, QHBoxLayout)

class ChatBubble(QWidget):
    def __init__(self, text, is_user, title, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        self.initUI(text, is_user, title)

    def initUI(self, text, is_user, title):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setObjectName("title")

        bubble_layout = QHBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel()
        label.setText(text)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setTextFormat(Qt.RichText)  # Enable HTML formatting

        if is_user:
            label.setObjectName("user-bubble")
            label.setStyleSheet("""
                QLabel#user-bubble {
                    background-color: white;
                    color: #333333;
                    border: 1px solid #FFFFFF;
                    border-radius: 15px;
                    padding: 10px;
                }
            """)
            title_label.setAlignment(Qt.AlignRight)
        else:
            label.setObjectName("bot-bubble")
            label.setStyleSheet("""
                QLabel#bot-bubble {
                    background-color: #E8D8FF;
                    color: #5E2D91;
                    border: 1px solid #E8D8FF;
                    border-radius: 15px;
                    padding: 10px;
                }
            """)
            title_label.setAlignment(Qt.AlignLeft)

        if is_user:
            bubble_layout.addStretch()
            bubble_layout.addWidget(label)
        else:
            bubble_layout.addWidget(label)
            bubble_layout.addStretch()

        outer_layout.addWidget(title_label)
        outer_layout.addLayout(bubble_layout)
        self.setLayout(outer_layout)