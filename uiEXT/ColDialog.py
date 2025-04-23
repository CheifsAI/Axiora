from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QWidget, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from uiEXT.StaticsCharts import skwness, boxBlot

class ColDialog(QDialog):
    def __init__(self, parent=None, df=None, column_name=None):
        super().__init__(parent)
        self.df = df
        self.column_name = column_name
        self.setWindowTitle(f"Column Options - {column_name}")
        # Set a moderate default size
        self.resize(900, 500)
        self.setMinimumSize(600, 300)
        
        # Enable window features
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowCloseButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowMinimizeButtonHint
        )
        
        # Create main layout as horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # First section for numerical statistics
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
        
        # Stats Label
        stats_label = QLabel("Statistics")
        stats_label.setStyleSheet("font-size: 12pt; font-weight: bold; border: none;")
        stats_label.setAlignment(Qt.AlignCenter)
        numerical_layout.addWidget(stats_label)
        
        # Add statistics if we have data
        if df is not None and column_name is not None:
            stats_text = f"""
            Mean: {df[column_name].mean():.2f}
            Median: {df[column_name].median():.2f}
            Std Dev: {df[column_name].std():.2f}
            Min: {df[column_name].min():.2f}
            Max: {df[column_name].max():.2f}
            """
            stats_details = QLabel(stats_text)
            stats_details.setStyleSheet("font-size: 10pt; border: none;")
            stats_details.setAlignment(Qt.AlignLeft)
            numerical_layout.addWidget(stats_details)
        
        # Second section for Skewness Plot
        skewness_section = QWidget()
        skewness_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        skewness_section.setStyleSheet("""
            QWidget {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin: 2px;
            }
        """)
        skewness_layout = QVBoxLayout(skewness_section)
        skewness_layout.setContentsMargins(10, 10, 10, 10)
        
        skewness_label = QLabel("Distribution Plot")
        skewness_label.setStyleSheet("font-size: 12pt; font-weight: bold; border: none;")
        skewness_label.setAlignment(Qt.AlignCenter)
        skewness_layout.addWidget(skewness_label)
        
        # Add skewness plot
        if df is not None and column_name is not None:
            skwness(column_name, df)
            skewness_plot = QLabel()
            skewness_pixmap = QPixmap(f'{column_name}_skewness.png')
            skewness_plot.setPixmap(skewness_pixmap.scaled(
                300, 300, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
            skewness_plot.setAlignment(Qt.AlignCenter)
            skewness_layout.addWidget(skewness_plot)
        
        # Third section for Box Plot
        boxplot_section = QWidget()
        boxplot_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        boxplot_section.setStyleSheet("""
            QWidget {
                background-color: #d0d0d0;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin: 2px;
            }
        """)
        boxplot_layout = QVBoxLayout(boxplot_section)
        boxplot_layout.setContentsMargins(10, 10, 10, 10)
        
        boxplot_label = QLabel("Box Plot")
        boxplot_label.setStyleSheet("font-size: 12pt; font-weight: bold; border: none;")
        boxplot_label.setAlignment(Qt.AlignCenter)
        boxplot_layout.addWidget(boxplot_label)
        
        # Add box plot
        if df is not None and column_name is not None:
            boxBlot(column_name, df)
            boxplot_plot = QLabel()
            boxplot_pixmap = QPixmap(f'{column_name}_boxplot.png')
            boxplot_plot.setPixmap(boxplot_pixmap.scaled(
                300, 300, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
            boxplot_plot.setAlignment(Qt.AlignCenter)
            boxplot_layout.addWidget(boxplot_plot)
        
        # Add sections to main layout horizontally
        main_layout.addWidget(numerical_section)
        main_layout.addWidget(skewness_section)
        main_layout.addWidget(boxplot_section)
        
        # Set equal stretch for all sections
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)
        main_layout.setStretch(2, 1) 