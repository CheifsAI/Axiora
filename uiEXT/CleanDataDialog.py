from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFrame, QComboBox,
                            QSpinBox, QDoubleSpinBox, QCheckBox,
                            QScrollArea, QWidget, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import pandas as pd
import numpy as np
from scipy import stats

class CleanDataDialog(QDialog):
    def __init__(self, parent=None, df=None, column_name=None):
        super().__init__(parent)
        self.df = df
        self.column_name = column_name
        
        # Handle either single column or entire dataframe
        if column_name is not None:
            self.original_data = df[column_name].copy()
            self.cleaned_data = df[column_name].copy()
            self.setWindowTitle(f"Clean Data - {column_name}")
        else:
            self.original_data = df.copy()
            self.cleaned_data = df.copy()
            self.setWindowTitle("Clean Data - All Columns")
        
        self.resize(800, 600)
        self.setMinimumSize(600, 400)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #2c313c;
                border: 1px solid #2c313c;
                border-radius: 10px;
            }
            QFrame {
                background-color: #1b1e23;
                border: 2px solid #2c313c;
                border-radius: 15px;
                padding: 10px;
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
            QLabel {
                color: white;
            }
            QComboBox {
                background-color: #1b1e23;
                color: white;
                border: 1px solid #00a6fb;
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox:disabled {
                color: #666;
                border: 1px solid #666;
            }
            QComboBox QAbstractItemView {
                background-color: #1b1e23;
                color: white;
                selection-background-color: #00a6fb;
                selection-color: white;
                border: 1px solid #00a6fb;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #1b1e23;
                color: white;
                border: 1px solid #00a6fb;
                border-radius: 3px;
                padding: 5px;
            }
            QSpinBox:disabled, QDoubleSpinBox:disabled {
                color: #666;
                border: 1px solid #666;
            }
            QCheckBox {
                color: white;
            }
            QCheckBox:disabled {
                color: #666;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.setup_ui()
        self.analyze_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent;")
        
        # Create container for scroll area
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Data Analysis Section
        analysis_frame = QFrame()
        analysis_layout = QVBoxLayout(analysis_frame)
        
        title = QLabel("🔍 Data Analysis")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #00a6fb;")
        analysis_layout.addWidget(title)
        
        self.analysis_label = QLabel()
        self.analysis_label.setWordWrap(True)
        analysis_layout.addWidget(self.analysis_label)
        
        container_layout.addWidget(analysis_frame)
        
        # Cleaning Options Section
        cleaning_frame = QFrame()
        cleaning_layout = QVBoxLayout(cleaning_frame)
        
        title = QLabel("🧹 Cleaning Options")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #00a6fb;")
        cleaning_layout.addWidget(title)
        
        # Missing Values
        self.handle_missing_cb = QCheckBox("Handle Missing Values")
        self.missing_method = QComboBox()
        self.missing_method.addItems(["Drop", "Mean", "Median", "Mode", "Forward Fill", "Backward Fill"])
        cleaning_layout.addWidget(self.handle_missing_cb)
        cleaning_layout.addWidget(self.missing_method)
        
        # Outliers
        self.handle_outliers_cb = QCheckBox("Handle Outliers")
        self.outlier_method = QComboBox()
        self.outlier_method.addItems(["IQR Method", "Z-Score Method", "Winsorization"])
        self.outlier_threshold = QDoubleSpinBox()
        self.outlier_threshold.setRange(1.5, 5.0)
        self.outlier_threshold.setValue(1.5)
        self.outlier_threshold.setSingleStep(0.1)
        cleaning_layout.addWidget(self.handle_outliers_cb)
        cleaning_layout.addWidget(self.outlier_method)
        cleaning_layout.addWidget(self.outlier_threshold)
        
        # Duplicates
        self.handle_duplicates_cb = QCheckBox("Remove Duplicates")
        cleaning_layout.addWidget(self.handle_duplicates_cb)
        
        # Data Type Conversion
        self.convert_dtype_cb = QCheckBox("Convert Data Type")
        self.dtype_method = QComboBox()
        self.dtype_method.addItems(["Automatic", "Integer", "Float", "String", "DateTime"])
        cleaning_layout.addWidget(self.convert_dtype_cb)
        cleaning_layout.addWidget(self.dtype_method)
        
        container_layout.addWidget(cleaning_frame)
        
        # Set the container as the scroll area widget
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Preview Changes")
        self.preview_btn.clicked.connect(self.preview_changes)
        button_layout.addWidget(self.preview_btn)
        
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.apply_changes)
        button_layout.addWidget(self.apply_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
    def analyze_data(self):
        analysis = []
        
        if self.column_name is not None:
            # Single column analysis
            data = self.df[self.column_name]
            
            # Check data type
            dtype = data.dtype
            analysis.append(f"Data Type: {dtype}")
            
            # Check missing values
            missing_count = data.isnull().sum()
            if missing_count > 0:
                missing_pct = (missing_count / len(data)) * 100
                analysis.append(f"Missing Values: {missing_count} ({missing_pct:.1f}%)")
            
            # Check duplicates
            duplicate_count = data.duplicated().sum()
            if duplicate_count > 0:
                duplicate_pct = (duplicate_count / len(data)) * 100
                analysis.append(f"Duplicates: {duplicate_count} ({duplicate_pct:.1f}%)")
            
            # Check for outliers if numeric
            if np.issubdtype(dtype, np.number):
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))).sum()
                if outliers > 0:
                    outlier_pct = (outliers / len(data)) * 100
                    analysis.append(f"Potential Outliers: {outliers} ({outlier_pct:.1f}%)")
                
                # Check for skewness
                skewness = stats.skew(data.dropna())
                if abs(skewness) > 1:
                    analysis.append(f"High Skewness: {skewness:.2f}")
        else:
            # Full dataframe analysis
            analysis.append(f"Total Columns: {len(self.df.columns)}")
            analysis.append(f"Total Rows: {len(self.df)}")
            
            # Missing values analysis
            missing_cols = self.df.columns[self.df.isnull().any()].tolist()
            if missing_cols:
                analysis.append("\nColumns with missing values:")
                for col in missing_cols:
                    missing_count = self.df[col].isnull().sum()
                    missing_pct = (missing_count / len(self.df)) * 100
                    analysis.append(f"- {col}: {missing_count} ({missing_pct:.1f}%)")
            
            # Duplicate rows analysis
            duplicate_count = self.df.duplicated().sum()
            if duplicate_count > 0:
                duplicate_pct = (duplicate_count / len(self.df)) * 100
                analysis.append(f"\nDuplicate Rows: {duplicate_count} ({duplicate_pct:.1f}%)")
            
            # Data type analysis
            analysis.append("\nColumn Data Types:")
            for col, dtype in self.df.dtypes.items():
                analysis.append(f"- {col}: {dtype}")
        
        # Update analysis label
        self.analysis_label.setText("\n".join(analysis))
        
        # Enable/disable options based on context
        is_numeric = (self.column_name is not None and 
                     np.issubdtype(self.df[self.column_name].dtype, np.number))
        self.handle_outliers_cb.setEnabled(is_numeric)
        self.outlier_method.setEnabled(is_numeric)
        self.outlier_threshold.setEnabled(is_numeric)
    
    def clean_data(self):
        if self.column_name is not None:
            # Clean single column
            data = self.original_data.copy()
            cleaned = self._clean_series(data)
            return cleaned
        else:
            # Clean entire dataframe
            cleaned_df = self.original_data.copy()
            
            # Handle missing values for all columns
            if self.handle_missing_cb.isChecked():
                method = self.missing_method.currentText()
                if method == "Drop":
                    cleaned_df = cleaned_df.dropna()
                elif method == "Forward Fill":
                    cleaned_df = cleaned_df.fillna(method='ffill')
                elif method == "Backward Fill":
                    cleaned_df = cleaned_df.fillna(method='bfill')
                else:
                    # Handle numeric columns with mean/median/mode
                    numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
                    for col in numeric_cols:
                        if method == "Mean":
                            cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
                        elif method == "Median":
                            cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
                        elif method == "Mode":
                            cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mode()[0])
            
            # Handle outliers for numeric columns
            if self.handle_outliers_cb.isChecked():
                numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    cleaned_df[col] = self._handle_outliers(cleaned_df[col])
            
            # Handle duplicates
            if self.handle_duplicates_cb.isChecked():
                cleaned_df = cleaned_df.drop_duplicates()
            
            return cleaned_df
    
    def _clean_series(self, data):
        # Handle missing values
        if self.handle_missing_cb.isChecked():
            method = self.missing_method.currentText()
            if method == "Drop":
                data = data.dropna()
            elif method == "Mean":
                data = data.fillna(data.mean())
            elif method == "Median":
                data = data.fillna(data.median())
            elif method == "Mode":
                data = data.fillna(data.mode()[0])
            elif method == "Forward Fill":
                data = data.fillna(method='ffill')
            elif method == "Backward Fill":
                data = data.fillna(method='bfill')
        
        # Handle outliers for numeric data
        if self.handle_outliers_cb.isChecked() and np.issubdtype(data.dtype, np.number):
            data = self._handle_outliers(data)
        
        # Handle duplicates
        if self.handle_duplicates_cb.isChecked():
            data = data.drop_duplicates()
        
        # Convert data type
        if self.convert_dtype_cb.isChecked():
            data = self._convert_dtype(data)
        
        return data
    
    def _handle_outliers(self, data):
        method = self.outlier_method.currentText()
        threshold = self.outlier_threshold.value()
        
        if method == "IQR Method":
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            return data.clip(lower=lower_bound, upper=upper_bound)
        
        elif method == "Z-Score Method":
            z_scores = np.abs(stats.zscore(data, nan_policy='omit'))
            return data.mask(z_scores > threshold, data.median())
        
        elif method == "Winsorization":
            lower_percentile = stats.percentileofscore(data.dropna(), data.quantile(0.25) - threshold * (data.quantile(0.75) - data.quantile(0.25)))
            upper_percentile = stats.percentileofscore(data.dropna(), data.quantile(0.75) + threshold * (data.quantile(0.75) - data.quantile(0.25)))
            return data.clip(lower=np.percentile(data.dropna(), lower_percentile),
                           upper=np.percentile(data.dropna(), upper_percentile))
        
        return data
    
    def _convert_dtype(self, data):
        method = self.dtype_method.currentText()
        try:
            if method == "Automatic":
                # Try to infer the best data type
                if data.str.contains(r'^\d+$').all():
                    return data.astype(int)
                elif data.str.contains(r'^\d*\.?\d+$').all():
                    return data.astype(float)
                elif data.str.contains(r'\d{4}-\d{2}-\d{2}').all():
                    return pd.to_datetime(data)
            elif method == "Integer":
                return data.astype(int)
            elif method == "Float":
                return data.astype(float)
            elif method == "String":
                return data.astype(str)
            elif method == "DateTime":
                return pd.to_datetime(data)
        except Exception as e:
            QMessageBox.warning(self, "Data Type Conversion Error",
                              f"Could not convert to {method}: {str(e)}")
        return data
    
    def preview_changes(self):
        self.cleaned_data = self.clean_data()
        
        # Create preview dialog
        preview = QDialog(self)
        preview.setWindowTitle("Preview Changes")
        preview.resize(600, 400)
        preview.setStyleSheet(self.styleSheet())
        
        layout = QVBoxLayout(preview)
        
        # Add statistics comparison
        stats_label = QLabel()
        stats_text = []
        
        if self.column_name is not None:
            # Single column statistics
            stats_text.append("Statistics Comparison (Original → Cleaned):")
            stats_text.append(f"Count: {len(self.original_data)} → {len(self.cleaned_data)}")
            
            if np.issubdtype(self.original_data.dtype, np.number):
                stats_text.append(f"Mean: {self.original_data.mean():.2f} → {self.cleaned_data.mean():.2f}")
                stats_text.append(f"Std: {self.original_data.std():.2f} → {self.cleaned_data.std():.2f}")
                stats_text.append(f"Min: {self.original_data.min():.2f} → {self.cleaned_data.min():.2f}")
                stats_text.append(f"Max: {self.original_data.max():.2f} → {self.cleaned_data.max():.2f}")
        else:
            # Full dataframe statistics
            stats_text.append("Dataframe Changes:")
            stats_text.append(f"Original Rows: {len(self.original_data)} → Cleaned Rows: {len(self.cleaned_data)}")
            
            # Missing values comparison
            orig_missing = self.original_data.isnull().sum().sum()
            cleaned_missing = self.cleaned_data.isnull().sum().sum()
            stats_text.append(f"Total Missing Values: {orig_missing} → {cleaned_missing}")
            
            # Duplicates comparison
            orig_dupes = self.original_data.duplicated().sum()
            cleaned_dupes = self.cleaned_data.duplicated().sum()
            stats_text.append(f"Duplicate Rows: {orig_dupes} → {cleaned_dupes}")
        
        stats_label.setText("\n".join(stats_text))
        stats_label.setStyleSheet("color: white;")
        layout.addWidget(stats_label)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(preview.close)
        layout.addWidget(close_btn)
        
        preview.exec_()
    
    def apply_changes(self):
        self.cleaned_data = self.clean_data()
        if self.column_name is not None:
            self.df[self.column_name] = self.cleaned_data
        else:
            self.df = self.cleaned_data.copy()
        self.accept()
