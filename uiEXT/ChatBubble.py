from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit,
                             QPushButton,QVBoxLayout, QWidget, QLabel,
                             QScrollArea, QSizePolicy, QHBoxLayout)

class ChatBubble(QWidget):
    def __init__(self, text, is_user, title):
        super().__init__()
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)

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
            label.setStyleSheet(f"""
                QLabel#user-bubble {{
                    background-color: white; 
                    color: #333333; 
                    border: 1px solid #FFFFFF;
                    border-radius: 15px; 
                    padding: 10px;
                }}
            """)
        else:
            label.setObjectName("bot-bubble")
            label.setStyleSheet(f"""
                QLabel#bot-bubble {{
                    background-color: #E8D8FF;
                    color: #5E2D91; 
                    border: 1px solid #E8D8FF; 
                    border-radius: 15px; 
                    padding: 10px;
                }}
            """)

        if is_user:
            title_label.setAlignment(Qt.AlignRight)
            outer_layout.addWidget(title_label)
            bubble_layout.addStretch()
            bubble_layout.addWidget(label)
        else:
            outer_layout.addWidget(title_label)
            bubble_layout.addWidget(label)
            bubble_layout.addStretch()

        outer_layout.addLayout(bubble_layout)
        self.setLayout(outer_layout)