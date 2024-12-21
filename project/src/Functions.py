#GUI Functions
import sys
sys.path.append(r"C:\Users\hasso\AppData\Local\Programs\Python\Python312\Lib")

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
        print("Current Theme is", current_theme)
        