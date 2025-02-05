from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
import sys
#from PyQt5 import uic
from OprFuncs import read_file
from Main import DataAnalyzer
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
         self.main_window.ui.qu_btn.clicked.connect(self.handle_qu_btn)

    def handle_data_button(self):
        fpath, _ = QFileDialog.getOpenFileName(
            self.main_window, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)"
        )
        if fpath:
            self.location = self.main_window.ui.path_location
            self.location.setText(fpath)
            self.df = read_file(fpath)
            self.analyzer = DataAnalyzer(dataframe=self.df,llm=self.llm)

            print("Columns:", self.df.columns)  # Debugging

            # Convert index to a column
            self.df.insert(0, "Index", self.df.index)

            self.table = self.main_window.ui.tableData
            self.table.setRowCount(self.df.shape[0])  # Set number of rows
            self.table.setColumnCount(self.df.shape[1])  # Set number of columns (including index)

            # Ensure column headers are correctly applied
            self.table.setHorizontalHeaderLabels(self.df.columns.astype(str))

            # Ensure visibility and auto-resizing
            self.table.horizontalHeader().setVisible(True)
            self.table.resizeColumnsToContents()

            # Populate the table with data
            for i in range(self.df.shape[0]):
                for j in range(self.df.shape[1]):
                    self.table.setItem(i, j, QTableWidgetItem(str(self.df.iat[i, j])))


    def handle_sum_btn(self):
        self.summary = markdown(self.analyzer.analysis_data())
        self.summary_text = self.main_window.ui.summary_text
        self.summary_text.setMarkdown(self.summary)
        print(self.summary)

    def handle_btn_LLMs(self):
        #menu = QMenu()
        print("Clicked LLM")

    def handle_clean_data_btn(self):
        self.cleaned_df = self.analyzer.drop_nulls()
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
    
# result = quetions_gen(llm=llm,dataframe=df1,num=2)
# for i, question in enumerate(result, 1):
#    print(markdown(question))
    #def handle_qu_btn(self,self.num_qu):
     #   print("I'm Clicked")