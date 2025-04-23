import sys
import os
import platform
import ctypes

# Import Qt modules first
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QHeaderView, QLabel, 
    QVBoxLayout, QSizePolicy, QPushButton
)
from PySide6.QtGui import QIcon, QFont, QPixmap, QCursor
from PySide6.QtCore import Qt, QSize

# Import our modules
from modules.app_settings import Settings
from modules.ui_functions import UIFunctions
from Functions import GuiFunctions
from uiEXT.login.LoginWindow import LoginWindow
from langchain_core.messages import HumanMessage, AIMessage
from OprFuncs import read_file
from modules.ui_main import Ui_MainWindow


def resizeEvent(self, event):
    new_size = max(10, self.width() // 100)  
    self.adjust_font_size(new_size)
    event.accept()

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
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
        
        # Initialize app functions after UI setup
        self.app_functions = GuiFunctions(self, self.user_id)
        self.load_reports()
        
        # Fix path separators for Windows - use forward slashes
        self.report_logo = "images/icons/cil-report-colored-1.png"
        
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
        #widgets.btn_chat.setIcon(QIcon(r"images\icons\chat.png"))
        
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
        widgets.btn_chat.clicked.connect(self.buttonClick)
        widgets.btn_data.clicked.connect(self.buttonClick)
        widgets.btn_anlysis.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_dashboard.clicked.connect(self.buttonClick)
        
        
        # Set icons for buttons
        #widgets.btn_home.setIcon(QIcon("images/icons/chat.png"))
        widgets.btn_data.setIcon(QIcon("images/icons/data_icon.png"))
        widgets.btn_anlysis.setIcon(QIcon("images/icons/new_icon.png"))

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.optionsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = True
        themeFile = "themes/py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            self.applyTheme(themeFile)

            # SET HACKS
            #AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home_2)
        username = self.app_functions.db.get_user_name(self.user_id)
        welcome_label = QLabel(f"Welcome, {username}!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        widgets.home_2.layout().addWidget(welcome_label)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

    def load_reports(self):
        #self.report_list.clear()
        reports = self.app_functions.db.get_user_reports(self.user_id)
        for report in reports:
            report_btn = QPushButton(self.ui.topMenus)
            report_btn.setObjectName(report['name'])
            sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            sizePolicy1.setHeightForWidth(report_btn.sizePolicy().hasHeightForWidth())
            report_btn.setSizePolicy(sizePolicy1)
            report_btn.setMinimumSize(QSize(0, 45))
           # report_btn.setFont(Qfont)
            report_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            report_btn.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            report_btn.setText(report['name'])
            report_btn.setProperty("report_id", report['id'])
            report_btn.setProperty("report_name", report['name'])

            report_logo = "images/icons/cil-report-colored-1.png"
            pixmap_report_logo = QPixmap(report_logo)
            logo_icon = QIcon(pixmap_report_logo)
            report_btn.setIcon(logo_icon)

            report_btn.clicked.connect(self.report_button_clicked)
            self.ui.verticalLayout_14.addWidget(report_btn)

    def report_button_clicked(self):
        btn = self.sender()
        report_id = btn.property("report_id")
        report_name = btn.property("report_name")
        print(f"Report '{report_name}' (ID: {report_id}) clicked!")
        self.load_report(report_id)
    
    def load_report(self,report_id):
        self._clear_chat_display()
        self._clear_questions()
        self.app_functions.reportID = report_id
        report_dataset = self.app_functions.db.get_report_dataset(report_id)
        self.app_functions.dname = os.path.basename(report_dataset)
        self.app_functions.rname = os.path.splitext(os.path.basename(report_dataset))[0]
        self.app_functions.df = read_file(report_dataset)
        self.app_functions._analyzer_attributes()
        self.app_functions._show_df()
        summary = self.app_functions.db.get_report_summary(report_id)
        if summary:
            self.app_functions._update_summary_text(summary)
        else: 
            self.ui.summary_text.setText("")
        questions = self.app_functions.db.get_report_questions(report_id)
        if questions:
            self.app_functions.g_questions = questions
            self.app_functions._ques_add()
        chat_history = self.app_functions.db.get_report_chat(report_id)
        if chat_history:
            for prompt, response, _ in chat_history:
                if prompt:
                    self.app_functions._add_user_message(prompt)
                    if response:
                        self.app_functions._add_ai_message(response)
        report_memory = self.app_functions.db.get_report_memory(report_id)
        if report_memory:
            for prompt, response, _ in report_memory:
                if prompt:
                    self.app_functions.analyzer.memory.append(HumanMessage(content=prompt))
                    if response:
                        self.app_functions.analyzer.memory.append(AIMessage(content=response))
        
        # Get and display charts
        chart_paths = self.app_functions.db.get_report_charts(report_id)
        if chart_paths:
            self.app_functions.chart_paths = chart_paths
            self.app_functions.display_current_chart()

    def _clear_chat_display(self):
        while self.ui.chat_layout.count() > 0:
            item = self.ui.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            # If it's a layout or spacer, remove it
            elif item.layout():
                self.clear_layout(item.layout())

    def _clear_questions(self):
        scroll_contents = self.ui.scrollAreaWidgetContents
        if layout := scroll_contents.layout():  # Python 3.8+ (walrus operator)
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()


    # You can add more logic here, such as loading the report data, etc.
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

        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home_2)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        if btnName == "btn_dashboard":
            widgets.stackedWidget.setCurrentWidget(widgets.page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))



        # SHOW HOME PAGE
        if btnName == "btn_chat":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_data":
            widgets.stackedWidget.setCurrentWidget(widgets.data_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_anlysis":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        if btnName == "btn_new":
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
    # Create QApplication instance
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
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
