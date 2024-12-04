#GUI Functions

from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
from Custom_Widgets.QCustomLoadingIndicators import QCustomLoadingIndicators

from Pyside6.QtCore import QSettings, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import QGraphicsDropShadowEffect




class GuiFunctions():
    def__init__(sef,MainWindow):
        self.main = MainWindow
        self.ui = MainWindow.ui
    
    
    #initialize app theme
    