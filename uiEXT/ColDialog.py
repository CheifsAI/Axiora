from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QWidget, QSizePolicy, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from uiEXT.StaticsCharts import skwness, boxBlot, col_desc

class ColDialog(QDialog):
    def __init__(self, parent=None, df=None, column_name=None):
        super().__init__(parent)
        self.df = df
        self.column_name = column_name
        self.setWindowTitle(f"Column Analysis - {column_name}")
        self.resize(1000, 600)
        self.setMinimumSize(800, 500)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #2c313c;
                border: 1px solid #2c313c;
                border-radius: 10px;
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
        
        # First section for numerical statistics
        numerical_section = QFrame()
        numerical_section.setFrameShape(QFrame.StyledPanel)
        numerical_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        numerical_section.setStyleSheet("""
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
        numerical_layout = QVBoxLayout(numerical_section)
        numerical_layout.setContentsMargins(15, 15, 15, 15)
        numerical_layout.setSpacing(10)
        
        # Stats Title with icon
        stats_title = QLabel("📊 Statistics")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        stats_title.setFont(title_font)
        stats_title.setStyleSheet("color: #00a6fb; padding: 5px;")
        stats_title.setAlignment(Qt.AlignCenter)
        numerical_layout.addWidget(stats_title)
        
        # Add statistics if we have data
        if df is not None and column_name is not None:
            desc = col_desc(column_name, df)
            stats_text = f"""
            Count: {desc.loc['count', column_name]:.0f}
            Mean: {desc.loc['mean', column_name]:.2f}
            Std Dev: {desc.loc['std', column_name]:.2f}
            Min: {desc.loc['min', column_name]:.2f}
            25%: {desc.loc['25%', column_name]:.2f}
            50%: {desc.loc['50%', column_name]:.2f}
            75%: {desc.loc['75%', column_name]:.2f}
            Max: {desc.loc['max', column_name]:.2f}
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
            numerical_layout.addWidget(stats_details)
        
        # Second section for Distribution Plot
        dist_section = QFrame()
        dist_section.setFrameShape(QFrame.StyledPanel)
        dist_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        dist_section.setStyleSheet("""
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
        dist_layout = QVBoxLayout(dist_section)
        dist_layout.setContentsMargins(15, 15, 15, 15)
        
        dist_title = QLabel("📈 Distribution")
        dist_title.setFont(title_font)
        dist_title.setStyleSheet("color: #00a6fb; padding: 5px;")
        dist_title.setAlignment(Qt.AlignCenter)
        dist_layout.addWidget(dist_title)
        
        # Add distribution plot
        if df is not None and column_name is not None:
            skwness(column_name, df)
            dist_plot = QLabel()
            dist_pixmap = QPixmap(f'{column_name}_skewness.png')
            dist_plot.setPixmap(dist_pixmap.scaled(
                350, 350, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
            dist_plot.setAlignment(Qt.AlignCenter)
            dist_layout.addWidget(dist_plot)
        
        # Third section for Box Plot
        boxplot_section = QFrame()
        boxplot_section.setFrameShape(QFrame.StyledPanel)
        boxplot_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        boxplot_section.setStyleSheet("""
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
        boxplot_layout = QVBoxLayout(boxplot_section)
        boxplot_layout.setContentsMargins(15, 15, 15, 15)
        
        boxplot_title = QLabel("📦 Box Plot")
        boxplot_title.setFont(title_font)
        boxplot_title.setStyleSheet("color: #00a6fb; padding: 5px;")
        boxplot_title.setAlignment(Qt.AlignCenter)
        boxplot_layout.addWidget(boxplot_title)
        
        # Add box plot
        if df is not None and column_name is not None:
            boxBlot(column_name, df)
            boxplot_plot = QLabel()
            boxplot_pixmap = QPixmap(f'{column_name}_boxplot.png')
            boxplot_plot.setPixmap(boxplot_pixmap.scaled(
                350, 350, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
            boxplot_plot.setAlignment(Qt.AlignCenter)
            boxplot_layout.addWidget(boxplot_plot)
        
        # Add sections to main layout horizontally
        main_layout.addWidget(numerical_section)
        main_layout.addWidget(dist_section)
        main_layout.addWidget(boxplot_section)
        
        # Set equal stretch for all sections
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)
        main_layout.setStretch(2, 1) 