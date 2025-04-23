from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QWidget, QSizePolicy)
from PySide6.QtCore import Qt

class ColDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Column Options")
        # Set a moderate default size
        self.resize(900, 500)  # Default size
        self.setMinimumSize(600, 300)  # Minimum size allowed
        
        # Enable window features (minimize, maximize, close buttons)
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowCloseButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowMinimizeButtonHint
        )
        
        # Create main layout as horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Reduced padding
        main_layout.setSpacing(10)  # Reduced spacing
        
        # First section for numerical
        numerical_section = QWidget()
        numerical_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        numerical_section.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin: 2px;
            }
        """)
        numerical_layout = QVBoxLayout(numerical_section)
        numerical_layout.setContentsMargins(10, 10, 10, 10)
        numerical_label = QLabel("Numerical Section")
        numerical_label.setStyleSheet("font-size: 12pt; font-weight: bold; border: none;")
        numerical_label.setAlignment(Qt.AlignCenter)
        numerical_layout.addWidget(numerical_label)
        
        # Second section for PNG
        png_section1 = QWidget()
        png_section1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        png_section1.setStyleSheet("""
            QWidget {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin: 2px;
            }
        """)
        png_layout1 = QVBoxLayout(png_section1)
        png_layout1.setContentsMargins(10, 10, 10, 10)
        png_label1 = QLabel("PNG Section 1")
        png_label1.setStyleSheet("font-size: 12pt; font-weight: bold; border: none;")
        png_label1.setAlignment(Qt.AlignCenter)
        png_layout1.addWidget(png_label1)
        
        # Third section for PNG
        png_section2 = QWidget()
        png_section2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        png_section2.setStyleSheet("""
            QWidget {
                background-color: #d0d0d0;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin: 2px;
            }
        """)
        png_layout2 = QVBoxLayout(png_section2)
        png_layout2.setContentsMargins(10, 10, 10, 10)
        png_label2 = QLabel("PNG Section 2")
        png_label2.setStyleSheet("font-size: 12pt; font-weight: bold; border: none;")
        png_label2.setAlignment(Qt.AlignCenter)
        png_layout2.addWidget(png_label2)
        
        # Add sections to main layout horizontally
        main_layout.addWidget(numerical_section)
        main_layout.addWidget(png_section1)
        main_layout.addWidget(png_section2)
        
        # Set equal stretch for all sections
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)
        main_layout.setStretch(2, 1) 