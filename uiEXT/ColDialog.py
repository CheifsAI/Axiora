from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QWidget, QSizePolicy, QFrame,
                            QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from uiEXT.StaticsCharts import skwness, boxBlot, col_desc
from uiEXT.CleanDataDialog import CleanDataDialog
import pandas as pd
import numpy as np

class ColDialog(QDialog):
    def __init__(self, parent=None, df=None, column_name=None):
        super().__init__(parent)
        self.df = df
        self.column_name = column_name
        self.setWindowTitle(f"Column Analysis - {column_name}")
        self.resize(1200, 600)
        self.setMinimumSize(1000, 500)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #2c313c;
                border: 1px solid #2c313c;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #00a6fb;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0088cc;
            }
        """)
        
        # Enable window features
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowCloseButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowMinimizeButtonHint
        )
        
        # Create main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left side layout for statistics
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)
        
        # Statistics section
        stats_section = self.create_stats_section()
        left_layout.addWidget(stats_section)        
        # Right side layout for plots
        right_layout = QHBoxLayout()
        right_layout.setSpacing(20)
        
        # Distribution plot section
        dist_section = self.create_dist_section()
        right_layout.addWidget(dist_section)
        
        # Box plot section
        boxplot_section = self.create_boxplot_section()
        right_layout.addWidget(boxplot_section)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
    
    def create_stats_section(self):
        section = QFrame()
        section.setFrameShape(QFrame.StyledPanel)
        section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        section.setStyleSheet("""
            QFrame {
                background-color: #1b1e23;
                border: 2px solid #2c313c;
                border-radius: 15px;
                padding: 10px;
            }
            QLabel {
                color: #fff;
                background-color: transparent;
            }
        """)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title = QLabel("📊 Statistics")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #00a6fb; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        if self.df is not None and self.column_name is not None:
            desc = col_desc(self.column_name, self.df)
            stats_text = f"""
            Count: {desc.loc['count', self.column_name]:.0f}
            Mean: {desc.loc['mean', self.column_name]:.2f}
            Std Dev: {desc.loc['std', self.column_name]:.2f}
            Min: {desc.loc['min', self.column_name]:.2f}
            25%: {desc.loc['25%', self.column_name]:.2f}
            50%: {desc.loc['50%', self.column_name]:.2f}
            75%: {desc.loc['75%', self.column_name]:.2f}
            Max: {desc.loc['max', self.column_name]:.2f}
            """
            stats_details = QLabel(stats_text)
            stats_details.setFont(QFont("Segoe UI", 11))
            stats_details.setStyleSheet("""
                color: #ffffff;
                background-color: #2c313c;
                padding: 15px;
                border-radius: 10px;
            """)
            stats_details.setAlignment(Qt.AlignLeft)
            layout.addWidget(stats_details)
        
        return section
    
    def create_dist_section(self):
        section = QFrame()
        section.setFrameShape(QFrame.StyledPanel)
        section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        section.setStyleSheet("""
            QFrame {
                background-color: #1b1e23;
                border: 2px solid #2c313c;
                border-radius: 15px;
                padding: 10px;
            }
            QLabel {
                color: #fff;
                background-color: transparent;
            }
        """)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("📈 Distribution")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #00a6fb; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        if self.df is not None and self.column_name is not None:
            skwness(self.column_name, self.df)
            dist_plot = QLabel()
            dist_pixmap = QPixmap(f'{self.column_name}_skewness.png')
            dist_plot.setPixmap(dist_pixmap.scaled(
                350, 350, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
            dist_plot.setAlignment(Qt.AlignCenter)
            layout.addWidget(dist_plot)
        
        return section
    
    def create_boxplot_section(self):
        section = QFrame()
        section.setFrameShape(QFrame.StyledPanel)
        section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        section.setStyleSheet("""
            QFrame {
                background-color: #1b1e23;
                border: 2px solid #2c313c;
                border-radius: 15px;
                padding: 10px;
            }
            QLabel {
                color: #fff;
                background-color: transparent;
            }
        """)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("📦 Box Plot")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #00a6fb; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        if self.df is not None and self.column_name is not None:
            boxBlot(self.column_name, self.df)
            boxplot_plot = QLabel()
            boxplot_pixmap = QPixmap(f'{self.column_name}_boxplot.png')
            boxplot_plot.setPixmap(boxplot_pixmap.scaled(
                350, 350, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
            boxplot_plot.setAlignment(Qt.AlignCenter)
            layout.addWidget(boxplot_plot)
        
        return section
    
