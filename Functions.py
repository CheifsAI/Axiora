from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import QGraphicsDropShadowEffect
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLabel
from PyQt5 import uic
from OprFuncs import read_file
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
from src.DataFrameDialog import DataFrameDialog
#from modules.ui_main import Ui_MainWindow

class GuiFunctions():
    def __init__(self,MainWindow):
        self.main_window = MainWindow
        self.ui = MainWindow.ui
        self.setup_connections()
        #init Apptheme
        #self.initializeAppTheme()
        
    #initialize app theme
    #def initializeAppTheme(self):
     #   """initialize the application theme from setting"""
      #  setting = QSettings()
       # current_theme = setting.value("THEME")
        # print("Current theme is", current_theme)
        
        # Add theme to the theme list
        #self.populateThemeList(current_theme)

    #def populateThemeList(self, current_theme):
     #       """Populate the list from available app themes"""
      #      theme_count = -1  # Initialize the theme counter
       #     for theme in self.ui.themes:
        #        self.ui.comboBox.addItem(theme.name, theme.name)
                
                # Check default theme/current theme
         #       if theme.defaultTheme or theme.name == current_theme:
          #          self.ui.comboBox.setCurrentIndex(theme_count)  # Select the theme        
    def setup_connections(self):
         self.main_window.ui.openfile_btn.clicked.connect(self.handle_data_button)
    def handle_data_button(self):
         fpath, _ = QFileDialog.getOpenFileName(self.main_window, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)") # Second parameter is default location
         if fpath:
            df = read_file(fpath)
            print(fpath)
            self.table = self.main_window.ui.tableData
            self.table.setRowCount(df.shape[0])  # Set number of rows
            self.table.setColumnCount(df.shape[1])  # Set number of columns
            self.table.setHorizontalHeaderLabels(df.columns)  # Set column headers
            header = self.table.horizontalHeader()
            header.setStyleSheet("QHeaderView::section { background-color: lightgray; }")
            # Populate the table with data
            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    self.table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
        # Open a new window to display the DataFrame
            #self.data_frame_dialog = DataFrameDialog(df, self.main_window)
            #self.data_frame_dialog.show()
