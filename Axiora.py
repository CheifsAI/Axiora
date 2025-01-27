import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from src.design_ui import Ui_MainWindow  # Assuming this is the UI from Qt Designer
from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from src.Functions import GuiFunctions
from Models import llama3b

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.model = llama3b
        # Set the central widget
        self.setCentralWidget(self.ui.centralwidget)
        
        # Load JSON style
        loadJsonStyle(self, self.ui, jsonFiles={"json-styles/style.json"})
        
        # Show the window
        self.show()
        
        # Update app settings
        QAppSettings.updateAppSettings(self)
        
        # Set up custom functions
        self.app_functions = GuiFunctions(self)

# Main execution
if __name__ == "__main__":
    # Make sure QApplication is initialized before any UI elements are created
    app = QApplication(sys.argv)  # This must come first!
    
    # Now create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())
# End of file