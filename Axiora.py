import sys
import os
import platform
import ctypes
from Functions import GuiFunctions
from uiEXT.login.LoginWindow import LoginWindow
from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView, QLabel, QVBoxLayout
from PySide6.QtGui import QIcon, QFont, QPixmap

def resizeEvent(self, event):
    new_size = max(10, self.width() // 100)  
    self.adjust_font_size(new_size)
    event.accept()

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
os.environ["QT_FONT_DPI"] = "110" # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

class MainWindow(QMainWindow):
    def __init__(self, user_id):
        QMainWindow.__init__(self)
        self.user_id = user_id
        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        self.app_functions = GuiFunctions(self, self.user_id)
        
        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        if platform.system() == "Windows":
            Settings.ENABLE_CUSTOM_TITLE_BAR = True
        else:
            Settings.ENABLE_CUSTOM_TITLE_BAR = False

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "Axiora"
        description = "Axiora - Automated BI Analysis"
        # APPLY TEXTS
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # Set icons for buttons
        widgets.btn_home.setIcon(QIcon(r"images\icons\chat.png"))
        
        # Set the logo
        logo_path = os.path.join(os.path.dirname(__file__), "images", "images", "IMG_20250226_011441_442.jpg")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Create a QLabel for the logo in the topLogoInfo frame
            logo_label = QLabel()
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            # Add the label to the topLogoInfo frame
            layout = QVBoxLayout(widgets.topLogoInfo)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(logo_label)
            # Set the logo in the main label if it exists
            if hasattr(widgets, 'label'):
                widgets.label.setPixmap(scaled_pixmap)
        else:
            print(f"Could not load logo from {logo_path}")

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableData.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_data.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)
        widgets.pushButton.clicked.connect(self.buttonClick)
        widgets.pushButton_2.clicked.connect(self.buttonClick)
        
        
        # Set icons for buttons
        widgets.btn_home.setIcon(QIcon(r"images\icons\chat.png"))
        widgets.btn_data.setIcon(QIcon("path/to/data_icon.png"))
        widgets.btn_new.setIcon(QIcon("path/to/new_icon.png"))

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = True
        themeFile = r"themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            self.applyTheme(themeFile)

            # SET HACKS
            #AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

    def applyTheme(self, themeFile):
        with open(themeFile, "r") as file:
            self.setStyleSheet(file.read())

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        if btnName == "pushButton":
            widgets.stackedWidget.setCurrentWidget(widgets.home_2)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        if btnName == "pushButton_2":
            widgets.stackedWidget.setCurrentWidget(widgets.page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))



        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_data":
            widgets.stackedWidget.setCurrentWidget(widgets.data_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_new":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        if btnName == "btn_save":
            print("Save BTN clicked!")

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.scenePosition().toPoint()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set up the application ID for Windows
    if platform.system() == 'Windows':
        myappid = 'mycompany.axiora.version1'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    # Set the application icon that will appear in taskbar
    # Try multiple icon formats
    icon_paths = [
        "images/images/IMG_20250226_011441_442.ico",  # First try .ico
        "images/images/IMG_20250226_011441_442.jpg",  # Then try .jpg
        "images/IMG_20250226_011441_442.ico",         # Try alternate paths
        "images/IMG_20250226_011441_442.jpg",
    ]
    
    icon = None
    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            break
    
    if icon:
        app.setWindowIcon(icon)  # Set icon for the entire application
    else:
        print("Warning: Could not find icon file in any of the expected locations")
    
    # Set the font size for the entire application
    font = QFont("Segoe UI", 12)
    app.setFont(font)

    login_window = LoginWindow()
    if icon:
        login_window.setWindowIcon(icon)  # Set icon for login window

    def open_main(user_id):
        main_window = MainWindow(user_id)
        if icon:
            main_window.setWindowIcon(icon)  # Set icon for main window
        main_window.show()
        login_window.close()

    login_window.login_accepted.connect(open_main)

    login_window.show()
    sys.exit(app.exec())
