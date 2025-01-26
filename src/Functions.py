from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
#from Custom_Widgets.QCustomLoadingIndicators import QCustomLoadingIndicators

from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import QGraphicsDropShadowEffect
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLabel
from PyQt5 import uic


class GuiFunctions():
    def __init__(self,MainWindow):
        self.main_window = MainWindow
        self.ui = MainWindow.ui
        self.setup_connections()
        #init Apptheme
        self.initializeAppTheme()
        
    #initialize app theme
    def initializeAppTheme(self):
        """initialize the application theme from setting"""
        setting = QSettings()
        current_theme = setting.value("THEME")
        # print("Current theme is", current_theme)
        
        # Add theme to the theme list
        self.populateThemeList(current_theme)

    def populateThemeList(self, current_theme):
            """Populate the list from available app themes"""
            theme_count = -1  # Initialize the theme counter
            for theme in self.ui.themes:
                self.ui.comboBox.addItem(theme.name, theme.name)
                
                # Check default theme/current theme
                if theme.defaultTheme or theme.name == current_theme:
                    self.ui.comboBox.setCurrentIndex(theme_count)  # Select the theme        
    def setup_connections(self):
         self.main_window.ui.Data.clicked.connect(self.handle_data_button)
    def handle_data_button(self):
         fname, _ = QFileDialog.getOpenFileName(self.main_window, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)") # Second parameter is default location
         if fname:
            print(fname)