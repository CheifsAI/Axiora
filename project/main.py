import os
import sys
from PySide6 import *
########################################################################
# IMPORT GUI FILE
from src.ui_z import *


########################################################################

########################################################################
# IMPORT Custom widgets
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
########################################################################

from src.Functions import GuiFunctions

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # This line should set the central widget correctly
        self.setCentralWidget(self.ui.centralwidget)  # Add this line


 

        # Use this to specify your json file(s) path/name
        loadJsonStyle(self, self.ui, jsonFiles = {
            "json-styles/style.json"
            }) 

        ########################################################################

        #######################################################################
        # SHOW WINDOW
        #######################################################################
        self.show() 


        # self = QMainWindow class
        QAppSettings.updateAppSettings(self)
        
        
        
        self.app_functions = GuiFunctions(self)
        
        

########################################################################
## EXECUTE APP
########################################################################
if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    ########################################################################
    ## 
    ########################################################################
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
########################################################################
## END===>
########################################################################  
