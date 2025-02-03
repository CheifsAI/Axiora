from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
import sys
#from PyQt5 import uic
from OprFuncs import read_file
from Main import *
#from PyQt5.QtWidgets import QMenu, QAction
from Models import *
from markdown import markdown

class GuiFunctions():
    def __init__(self,MainWindow):
        self.main_window = MainWindow
        self.ui = MainWindow.ui
        self.llm = llama3b
        self.setup_connections()
    def setup_connections(self):
         self.main_window.ui.openfile_btn.clicked.connect(self.handle_data_button)
         self.main_window.ui.sum_btn.clicked.connect(self.handle_sum_btn)
         self.main_window.ui.btn_LLMs.clicked.connect(self.handle_btn_LLMs)
         self.main_window.ui.clean_data_btn.clicked.connect(self.handle_clean_data_btn)
    def handle_data_button(self):
         fpath, _ = QFileDialog.getOpenFileName(self.main_window, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)") # Second parameter is default location
         if fpath:
            self.df = read_file(fpath)
            print(fpath)
            self.table = self.main_window.ui.tableData
            self.table.setRowCount(self.df.shape[0])  # Set number of rows
            self.table.setColumnCount(self.df.shape[1])  # Set number of columns
            self.table.setHorizontalHeaderLabels(self.df.columns)  # Set column headers
            header = self.table.horizontalHeader()
            #header.setStyleSheet("QHeaderView::section { background-color: lightgray; }")
            # Populate the table with data
            for i in range(self.df.shape[0]):
                for j in range(self.df.shape[1]):
                    self.table.setItem(i, j, QTableWidgetItem(str(self.df.iat[i, j])))
    def handle_sum_btn(self):
        self.summary = markdown(analysis_data(dataframe=self.df,llm=self.llm))
        self.summary_text = self.main_window.ui.summary_text
        self.summary_text.setMarkdown(self.summary)
        print(self.summary)
    def handle_btn_LLMs(self):
        #menu = QMenu()
        print("Clicked LLM")
    def handle_clean_data_btn(self):
        self.cleaned_df = drop_nulls(dataframe=self.df,llm=self.llm)
        self.table = self.main_window.ui.tableData
        self.table.setRowCount(self.cleaned_df.shape[0])  # Set number of rows
        self.table.setColumnCount(self.cleaned_df.shape[1])  # Set number of columns
        self.table.setHorizontalHeaderLabels(self.cleaned_df.columns)  # Set column headers
        header = self.table.horizontalHeader()
        #header.setStyleSheet("QHeaderView::section { background-color: lightgray; }")
        # Populate the table with data
        for i in range(self.cleaned_df.shape[0]):
            for j in range(self.cleaned_df.shape[1]):
                self.table.setItem(i, j, QTableWidgetItem(str(self.cleaned_df.iat[i, j])))
