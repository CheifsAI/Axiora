from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QWidget, QSizePolicy, QFrame,
                            QPushButton, QScrollArea)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QResizeEvent
from uiEXT.StaticsCharts import skwness, boxBlot, col_desc, col_corrBlot
from uiEXT.CleanDataDialog import CleanDataDialog
import pandas as pd
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ColDialog(QDialog):
    def __init__(self, parent=None, df=None, column_name=None):
        super().__init__(parent)
        self.df = df
        self.column_name = column_name
        self.setWindowTitle(f"Column Analysis - {column_name}")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        # Store references to canvases for resizing
        self.dist_canvas = None
        self.box_canvas = None
        self.corr_canvas = None
        
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
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QWidget#scrollContent {
                background-color: transparent;
            }
        """)
        
        # Enable window features
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowCloseButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowMinimizeButtonHint
        )
        
        # Create and setup UI
        self.setup_ui()
    
    def setup_ui(self):
        # Create scroll area for the entire content
        main_scroll = QScrollArea(self)
        main_scroll.setWidgetResizable(True)
        main_scroll.setStyleSheet("background-color: transparent;")
        
        # Create main container widget
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Upper section with statistics and plots
        upper_section = QHBoxLayout()
        
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
        
        # Add layouts to upper section
        upper_section.addLayout(left_layout, 1)
        upper_section.addLayout(right_layout, 2)
        
        # Add upper section to main layout
        main_layout.addLayout(upper_section)
        
        # Create and add correlation section
        corr_section = self.create_correlation_section()
        main_layout.addWidget(corr_section)
        
        # Set the container as the scroll area widget
        main_scroll.setWidget(container)
        
        # Create layout for the dialog and add the scroll area
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(main_scroll)

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
            fig = skwness(self.column_name, self.df)
            self.dist_canvas = FigureCanvas(fig)
            self.dist_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.dist_canvas.setStyleSheet("background-color: transparent;")
            layout.addWidget(self.dist_canvas)
        
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
            fig = boxBlot(self.column_name, self.df)
            self.box_canvas = FigureCanvas(fig)
            self.box_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.box_canvas.setStyleSheet("background-color: transparent;")
            layout.addWidget(self.box_canvas)
        
        return section
    
    def create_correlation_section(self):
        section = QFrame()
        section.setFrameShape(QFrame.StyledPanel)
        section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        section.setStyleSheet("""
            QFrame {
                background-color: #1b1e23;
                border: 2px solid #2c313c;
                border-radius: 15px;
                padding: 10px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2c313c;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #00a6fb;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("🔗 Correlations")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #00a6fb; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        if self.df is not None and self.column_name is not None:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("background-color: transparent;")
            
            plot_container = QWidget()
            plot_container.setObjectName("scrollContent")
            plot_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            container_layout = QVBoxLayout(plot_container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            fig = col_corrBlot(self.column_name, self.df)
            self.corr_canvas = FigureCanvas(fig)
            self.corr_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.corr_canvas.setStyleSheet("background-color: transparent;")
            container_layout.addWidget(self.corr_canvas)
            
            scroll.setWidget(plot_container)
            layout.addWidget(scroll)
        
        return section

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        # Update canvas sizes if they exist
        if self.dist_canvas:
            self.dist_canvas.draw()
        if self.box_canvas:
            self.box_canvas.draw()
        if self.corr_canvas:
            self.corr_canvas.draw()
    
