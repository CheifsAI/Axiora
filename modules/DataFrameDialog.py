from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
import pandas as pd
from Models import llama3b
from DataAnalyzer import drop_nulls,analysis_data
class DataFrameDialog(QDialog):
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.df = df  # Store the DataFrame
        self.setWindowTitle("DataFrame Viewer")
        self.setGeometry(100, 100, 600, 400)
        self.model = llama3b
        # Create layout
        layout = QVBoxLayout()
        
        # Create a QTableWidget to display the DataFrame
        self.table = QTableWidget()
        self.table.setRowCount(self.df.shape[0])  # Set number of rows
        self.table.setColumnCount(self.df.shape[1])  # Set number of columns
        self.table.setHorizontalHeaderLabels(self.df.columns)  # Set column headers
        
        # Populate the table with data
        for i in range(self.df.shape[0]):
            for j in range(self.df.shape[1]):
                self.table.setItem(i, j, QTableWidgetItem(str(self.df.iat[i, j])))
        
        # Add the table to the layout
        layout.addWidget(self.table)


        button_layout = QHBoxLayout()
        
        # Create a "Summarize" button
        self.summarize_button = QPushButton("Summarize")
        self.summarize_button.clicked.connect(self.summarize_data_handler)
        self.clean_button = QPushButton("Clean Data")
        self.clean_button.clicked.connect(self.drop_nulls_handler)

        button_layout.addWidget(self.summarize_button)
        button_layout.addWidget(self.clean_button)        

        layout.addLayout(button_layout)

        self.setLayout(layout)
    
    def summarize_data_handler(self):
        data_summary = analysis_data(self.df,self.model)
        if hasattr(self.parent(), "summary_label"):
            self.parent().summary_label.setText(data_summary)
            print(data_summary)
        else :
            print("fuck you")

        # Close the current dialog
        self.close()

    def drop_nulls_handler(self):
        result = drop_nulls(self.df,self.model)
        self.cleaned_dialog = DataFrameDialog(result, self)
        self.cleaned_dialog.setWindowTitle("Data Cleaned")
        self.cleaned_dialog.show()


    def summarize_data(self):
        # Perform summarization (e.g., calculate mean, max, min, etc.)
        summary = self.df.describe()
        
        # Open a new dialog to display the summary
        self.summary_dialog = DataFrameDialog(summary, self)
        self.summary_dialog.setWindowTitle("Data Summary")
        self.summary_dialog.show()