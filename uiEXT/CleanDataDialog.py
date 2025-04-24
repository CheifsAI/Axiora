from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QWidget, QSizePolicy, QFrame,
                            QPushButton, QComboBox, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import pandas as pd
import numpy as np

class CleanDataDialog(QDialog):
    def __init__(self, parent=None, df=None, column_name=None):
        super().__init__(parent)
        self.df = df
        self.column_name = column_name
        self.setWindowTitle(f"Data Cleaning - {column_name}")
        self.resize(800, 600)
        self.setMinimumSize(600, 400)
        
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
            QComboBox {
                background-color: #1b1e23;
                color: white;
                border: 1px solid #2c313c;
                border-radius: 5px;
                padding: 5px;
                min-width: 120px;
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
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create cleaning section
        cleaning_section = self.create_cleaning_section()
        main_layout.addWidget(cleaning_section)
        
        # Add clean all button at the bottom
        clean_all_btn = QPushButton("Clean All Data")
        clean_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #06d6a0;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #05c090;
            }
        """)
        clean_all_btn.clicked.connect(self.clean_all_data)
        main_layout.addWidget(clean_all_btn)
    
    def create_cleaning_section(self):
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
        
        title = QLabel("🧹 Data Cleaning")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #00a6fb; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        if self.df is not None and self.column_name is not None:
            # Null values info
            null_count = self.df[self.column_name].isnull().sum()
            null_percent = (null_count / len(self.df)) * 100
            null_info = QLabel(f"Null Values: {null_count} ({null_percent:.1f}%)")
            null_info.setStyleSheet("color: #ff6b6b;")
            layout.addWidget(null_info)
            
            # Cleaning operations
            operations_layout = QHBoxLayout()
            
            # Drop nulls button
            drop_nulls_btn = QPushButton("Drop Nulls")
            drop_nulls_btn.clicked.connect(self.drop_nulls)
            operations_layout.addWidget(drop_nulls_btn)
            
            # Fill nulls dropdown
            fill_methods = QComboBox()
            fill_methods.addItems(["Mean", "Median", "Mode", "Zero", "Custom"])
            operations_layout.addWidget(fill_methods)
            
            # Fill button
            fill_btn = QPushButton("Fill")
            fill_btn.clicked.connect(lambda: self.fill_nulls(fill_methods.currentText()))
            operations_layout.addWidget(fill_btn)
            
            layout.addLayout(operations_layout)
            
            # Outliers info
            Q1 = self.df[self.column_name].quantile(0.25)
            Q3 = self.df[self.column_name].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = self.df[(self.df[self.column_name] < lower_bound) | 
                             (self.df[self.column_name] > upper_bound)][self.column_name]
            outlier_count = len(outliers)
            outlier_percent = (outlier_count / len(self.df)) * 100
            
            outlier_info = QLabel(f"Outliers: {outlier_count} ({outlier_percent:.1f}%)")
            outlier_info.setStyleSheet("color: #ffd166;")
            layout.addWidget(outlier_info)
            
            # Outlier handling
            outlier_layout = QHBoxLayout()
            
            # Remove outliers button
            remove_outliers_btn = QPushButton("Remove Outliers")
            remove_outliers_btn.clicked.connect(self.remove_outliers)
            outlier_layout.addWidget(remove_outliers_btn)
            
            # Cap outliers button
            cap_outliers_btn = QPushButton("Cap Outliers")
            cap_outliers_btn.clicked.connect(self.cap_outliers)
            outlier_layout.addWidget(cap_outliers_btn)
            
            layout.addLayout(outlier_layout)
        
        return section
    
    def drop_nulls(self):
        """Drop null values from the column"""
        if self.df is not None and self.column_name is not None:
            initial_len = len(self.df)
            self.df.dropna(subset=[self.column_name], inplace=True)
            dropped = initial_len - len(self.df)
            QMessageBox.information(self, "Success", 
                                  f"Dropped {dropped} null values from {self.column_name}")
            self.update_display()
    
    def fill_nulls(self, method):
        """Fill null values using the specified method"""
        if self.df is not None and self.column_name is not None:
            if method == "Mean":
                self.df[self.column_name].fillna(self.df[self.column_name].mean(), inplace=True)
            elif method == "Median":
                self.df[self.column_name].fillna(self.df[self.column_name].median(), inplace=True)
            elif method == "Mode":
                self.df[self.column_name].fillna(self.df[self.column_name].mode()[0], inplace=True)
            elif method == "Zero":
                self.df[self.column_name].fillna(0, inplace=True)
            elif method == "Custom":
                # TODO: Implement custom value input dialog
                pass
            
            QMessageBox.information(self, "Success", 
                                  f"Filled null values using {method} method")
            self.update_display()
    
    def remove_outliers(self):
        """Remove outliers using IQR method"""
        if self.df is not None and self.column_name is not None:
            Q1 = self.df[self.column_name].quantile(0.25)
            Q3 = self.df[self.column_name].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            initial_len = len(self.df)
            self.df = self.df[(self.df[self.column_name] >= lower_bound) & 
                            (self.df[self.column_name] <= upper_bound)]
            removed = initial_len - len(self.df)
            
            QMessageBox.information(self, "Success", 
                                  f"Removed {removed} outliers from {self.column_name}")
            self.update_display()
    
    def cap_outliers(self):
        """Cap outliers using IQR method"""
        if self.df is not None and self.column_name is not None:
            Q1 = self.df[self.column_name].quantile(0.25)
            Q3 = self.df[self.column_name].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            self.df[self.column_name] = self.df[self.column_name].clip(lower_bound, upper_bound)
            
            QMessageBox.information(self, "Success", 
                                  f"Capped outliers in {self.column_name}")
            self.update_display()
    
    def clean_all_data(self):
        """Perform all cleaning steps in sequence"""
        if self.df is not None and self.column_name is not None:
            # Store initial state
            initial_len = len(self.df)
            initial_nulls = self.df[self.column_name].isnull().sum()
            
            # Step 1: Fill nulls with median
            self.fill_nulls("Median")
            
            # Step 2: Cap outliers
            self.cap_outliers()
            
            # Calculate changes
            final_nulls = self.df[self.column_name].isnull().sum()
            nulls_filled = initial_nulls - final_nulls
            
            # Show summary
            QMessageBox.information(self, "Cleaning Complete", 
                f"Data cleaning completed successfully!\n\n"
                f"Null values filled: {nulls_filled}\n"
                f"Outliers capped: Yes\n"
                f"Final row count: {len(self.df)}")
            
            # Update display
            self.update_display()
    
    def update_display(self):
        """Update all displays after data cleaning"""
        # Update cleaning section
        cleaning_section = self.create_cleaning_section()
        self.layout().itemAt(0).widget().deleteLater()
        self.layout().insertWidget(0, cleaning_section)
