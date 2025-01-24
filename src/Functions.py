from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
#from Custom_Widgets.QCustomLoadingIndicators import QCustomLoadingIndicators

from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import QGraphicsDropShadowEffect




class GuiFunctions():
    def __init__(self,MainWindow):
        self.main = MainWindow
        self.ui = MainWindow.ui
    
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