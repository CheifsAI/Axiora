import sys
import os
import platform
import ctypes
import matplotlib.pyplot as plt
import uuid
import markdown
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Import Qt modules first
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QHeaderView, QLabel, 
    QVBoxLayout, QSizePolicy, QPushButton, QGridLayout, QWidget, QFrame, QCheckBox, QTableWidget, QTableWidgetItem, QScrollArea, QHBoxLayout
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
from uiEXT.ColDialog import ColDialog
from time_series_forecaster import time_series_forecaster
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

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
        self.user_id = uuid.UUID(user_id)  # Convert string back to UUID
        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        
        # Initialize app functions after UI setup
        self.app_functions = GuiFunctions(self, self.user_id)
        self.load_oldreports()
        
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
        widgets.btn_predictions.clicked.connect(self.buttonClick)
        widgets.btn_print.clicked.connect(self.buttonClick)
        
        
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

        # Connect column header click event
        widgets.tableData.horizontalHeader().sectionClicked.connect(self.show_column_dialog)

    def load_oldreports(self):

        # Create a grid layout for the home page
        if hasattr(self.ui, 'home_2'):
            # Clear existing layout if any
            if self.ui.home_2.layout():
                QWidget().setLayout(self.ui.home_2.layout())
            
            # Create new grid layout
            grid_layout = QGridLayout(self.ui.home_2)
            grid_layout.setSpacing(10)
            grid_layout.setContentsMargins(20, 20, 20, 20)

            # Create welcome message widget for top left
            welcome_widget = QWidget()
            welcome_layout = QVBoxLayout(welcome_widget)
            welcome_layout.addStretch()

            # Add welcome widget to top left
            grid_layout.addWidget(welcome_widget, 0, 0)

            # Create reports container for top right
            reports_container = QWidget()
            reports_layout = QVBoxLayout(reports_container)
            reports_layout.setSpacing(5)
            reports_layout.setContentsMargins(0, 0, 0, 0)

            # Add title
            title_label = QLabel("Your Reports")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    padding: 10px;
                    background-color: rgb(196, 7, 105);
                    border-radius: 4px;
                }
            """)
            title_label.setAlignment(Qt.AlignCenter)
            reports_layout.addWidget(title_label)
            reports_layout.addSpacing(10)

            reports = self.app_functions.db.get_user_reports(self.user_id)
            for report in reports:
                report_btn = QPushButton()
                report_btn.setObjectName(report['name'])
                report_btn.setMinimumHeight(40)
                report_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                report_btn.setText(report['name'])
                report_btn.setProperty("report_id", report['id'])
                report_btn.setProperty("report_name", report['name'])
                
                # Set button style
                report_btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(24, 196, 199);
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        padding: 5px 10px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: rgb(7, 60, 196);
                    }
                """)
                
                # Add icon
                report_logo = "images/icons/cil-report-colored-1.png"
                pixmap_report_logo = QPixmap(report_logo)
                if not pixmap_report_logo.isNull():
                    scaled_pixmap = pixmap_report_logo.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    report_btn.setIcon(QIcon(scaled_pixmap))
                    report_btn.setIconSize(QSize(24, 24))
                
                report_btn.clicked.connect(self.report_button_clicked)
                reports_layout.addWidget(report_btn)

            # Add reports container to top right
            grid_layout.addWidget(reports_container, 0, 1)

            # Add empty widgets for bottom left and right
            bottom_left = QWidget()
            bottom_right = QWidget()
            grid_layout.addWidget(bottom_left, 1, 0)
            grid_layout.addWidget(bottom_right, 1, 1)

            # Add horizontal line
            horizontal_line = QFrame()
            horizontal_line.setFrameShape(QFrame.Shape.HLine)
            horizontal_line.setStyleSheet("background-color: #ddd;")
            grid_layout.addWidget(horizontal_line, 1, 0, 1, 2)

            # Add vertical line
            vertical_line = QFrame()
            vertical_line.setFrameShape(QFrame.Shape.VLine)
            vertical_line.setStyleSheet("background-color: #ddd;")
            grid_layout.addWidget(vertical_line, 0, 1, 2, 1)

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
        self.app_functions.datasetID = report_dataset
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

        # Load and display forecasting data if it exists
        forecasting_data = self.app_functions.db.get_forecasting(report_id)
        if forecasting_data:
            # Create a container for the predictions page content
            content_container = QWidget()
            content_layout = QVBoxLayout(content_container)
            content_layout.setSpacing(20)
            content_layout.setContentsMargins(20, 20, 20, 20)
            
            # Load the predicted DataFrame
            predictions_df = read_file(forecasting_data['predicted_df'])
            
            # Create and add the feature DataFrame table
            feature_table = QTableWidget()
            feature_table.setColumnCount(len(predictions_df.columns))
            feature_table.setRowCount(len(predictions_df))
            feature_table.setHorizontalHeaderLabels(predictions_df.columns)
            
            # Fill the table with data
            for i in range(len(predictions_df)):
                for j in range(len(predictions_df.columns)):
                    item = QTableWidgetItem(str(predictions_df.iloc[i, j]))
                    feature_table.setItem(i, j, item)
            
            # Set table properties
            feature_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            feature_table.setMinimumHeight(200)
            feature_table.setMaximumHeight(400)
            feature_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            feature_table.setAlternatingRowColors(True)
            feature_table.setStyleSheet("""
                QTableWidget {
                    background-color: #2c313c;
                    alternate-background-color: #1b1e23;
                    gridline-color: #3d4451;
                    border: 1px solid #3d4451;
                    color: #ffffff;
                }
                QHeaderView::section {
                    background-color: #1b1e23;
                    color: #00a6fb;
                    padding: 4px;
                    border: 1px solid #3d4451;
                    font-weight: bold;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QTableWidget::item:selected {
                    background-color: #00a6fb;
                    color: #ffffff;
                }
            """)
            
            # Add table to content layout
            content_layout.addWidget(feature_table)
            
            # Create a container for the plots with proper styling
            plot_container = QFrame()
            plot_container.setStyleSheet("""
                QFrame {
                    background-color: #2c313c;
                    border: 2px solid #3d4451;
                    border-radius: 10px;
                }
            """)
            plot_layout = QGridLayout(plot_container)
            plot_layout.setSpacing(20)
            plot_layout.setContentsMargins(20, 20, 20, 20)
            
            # Get forecasting data from database
            if hasattr(self.app_functions, 'reportID'):
                forecasting_data = self.app_functions.db.get_forecasting(self.app_functions.reportID)
                if forecasting_data and 'charts_path' in forecasting_data:
                    # Load and display charts from the charts directory
                    charts_dir = forecasting_data['charts_path']
                    if os.path.exists(charts_dir):
                        chart_files = [f for f in os.listdir(charts_dir) if f.endswith('.png')]
                        for i, chart_file in enumerate(chart_files):
                            chart_path = os.path.join(charts_dir, chart_file)
                            if os.path.exists(chart_path):
                                # Create a frame for each chart section
                                chart_section = QFrame()
                                chart_section.setStyleSheet("""
                                    QFrame {
                                        background-color: #1b1e23;
                                        border: 2px solid #3d4451;
                                        border-radius: 10px;
                                    }
                                """)
                                # Set size policy to make charts fill their containers
                                chart_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                                chart_section.setMinimumSize(600, 500)
                                chart_section_layout = QVBoxLayout(chart_section)
                                chart_section_layout.setContentsMargins(0, 0, 0, 0)
                                chart_section_layout.setSpacing(0)

                                # Add title label
                                title = QLabel()
                                if i == 0:
                                    title.setText("Time Series Overview")
                                elif i == 1:
                                    title.setText("Feature Importance Analysis")
                                elif i == 2:
                                    title.setText("Actual vs Predicted Values")
                                elif i == 3:
                                    title.setText("Model Performance (R² Plot)")
                                
                                title.setStyleSheet("""
                                    QLabel {
                                        color: #00a6fb;
                                        font-size: 16px;
                                        font-weight: bold;
                                        padding: 15px;
                                        background-color: #2c313c;
                                        border-top-left-radius: 8px;
                                        border-top-right-radius: 8px;
                                        border-bottom: 2px solid #3d4451;
                                    }
                                """)
                                title.setAlignment(Qt.AlignCenter)
                                title.setFixedHeight(50)
                                chart_section_layout.addWidget(title)

                                # Create chart content widget with dark background
                                chart_content = QWidget()
                                chart_content.setStyleSheet("background-color: #1b1e23;")
                                chart_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                                chart_content_layout = QVBoxLayout(chart_content)
                                chart_content_layout.setContentsMargins(0, 0, 0, 0)
                                chart_content_layout.setSpacing(0)

                                # Create figure and load image with proper sizing
                                dpi = 100  # Set DPI for better resolution
                                fig_width = 580 / dpi  # Calculate figure width in inches
                                fig_height = 430 / dpi  # Calculate figure height in inches
                                fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi, tight_layout=True)
                                fig.patch.set_facecolor('#1b1e23')
                                ax = plt.gca()
                                ax.set_facecolor('#1b1e23')
                                
                                img = plt.imread(chart_path)
                                plt.imshow(img)
                                plt.axis('off')
                                
                                # Add the plot canvas with proper sizing
                                canvas = FigureCanvas(fig)
                                canvas.setStyleSheet("background-color: #1b1e23;")
                                canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                                chart_content_layout.addWidget(canvas)

                                # Add metrics labels if they exist
                                if 'rmse' in forecasting_data and 'r2' in forecasting_data:
                                    metrics_frame = QFrame()
                                    metrics_frame.setStyleSheet("""
                                        QFrame {
                                            background-color: #2c313c;
                                            border-radius: 5px;
                                            padding: 5px;
                                        }
                                    """)
                                    metrics_layout = QVBoxLayout(metrics_frame)  # Changed to vertical layout
                                    metrics_layout.setContentsMargins(10, 5, 10, 5)
                                    metrics_layout.setSpacing(5)  # Reduced spacing between labels

                                    # R² Score Label with None handling
                                    r2_value = forecasting_data['r2']
                                    r2_text = f"R² Score on Test set: {r2_value:.4f}" if r2_value is not None else "R² Score on Test set: N/A"
                                    r2_label = QLabel(r2_text)
                                    r2_label.setStyleSheet("""
                                        QLabel {
                                            color: #00a6fb;
                                            font-size: 14px;
                                            font-weight: bold;
                                            padding: 5px;
                                        }
                                    """)
                                    metrics_layout.addWidget(r2_label)

                                    # RMSE Score Label with None handling
                                    rmse_value = forecasting_data['rmse']
                                    rmse_text = f"RMSE Score on Test set: {rmse_value:.2f}" if rmse_value is not None else "RMSE Score on Test set: N/A"
                                    rmse_label = QLabel(rmse_text)
                                    rmse_label.setStyleSheet("""
                                        QLabel {
                                            color: #00a6fb;
                                            font-size: 14px;
                                            font-weight: bold;
                                            padding: 5px;
                                        }
                                    """)
                                    metrics_layout.addWidget(rmse_label)

                                    chart_content_layout.addWidget(metrics_frame)

                                # Create scroll area with proper sizing
                                chart_scroll = QScrollArea()
                                chart_scroll.setStyleSheet("""
                                    QScrollArea {
                                        border: none;
                                        background-color: #1b1e23;
                                    }
                                    QScrollBar:vertical {
                                        border: none;
                                        background: #1b1e23;
                                        width: 8px;
                                        margin: 0;
                                    }
                                    QScrollBar::handle:vertical {
                                        background-color: #3d4451;
                                        min-height: 30px;
                                        border-radius: 4px;
                                    }
                                    QScrollBar::handle:vertical:hover {
                                        background-color: #00a6fb;
                                    }
                                    QScrollBar:horizontal {
                                        border: none;
                                        background: #1b1e23;
                                        height: 8px;
                                        margin: 0;
                                    }
                                    QScrollBar::handle:horizontal {
                                        background-color: #3d4451;
                                        min-width: 30px;
                                        border-radius: 4px;
                                    }
                                    QScrollBar::handle:horizontal:hover {
                                        background-color: #00a6fb;
                                    }
                                """)
                                chart_scroll.setWidget(chart_content)
                                chart_scroll.setWidgetResizable(True)
                                chart_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                                chart_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                                chart_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                                chart_section_layout.addWidget(chart_scroll)

                                # Position the chart sections in the grid with proper spacing
                                plot_layout.setSpacing(10)
                                plot_layout.setContentsMargins(10, 10, 10, 10)
                                if i == 0:  # Time Series Overview
                                    plot_layout.addWidget(chart_section, 0, 0)
                                elif i == 1:  # Feature Importance
                                    plot_layout.addWidget(chart_section, 0, 1)
                                elif i == 2:  # Actual vs Predicted
                                    plot_layout.addWidget(chart_section, 1, 0)
                                elif i == 3:  # R² Plot
                                    plot_layout.addWidget(chart_section, 1, 1)

            # Add final metrics section below all charts
            if hasattr(self.app_functions, 'reportID'):
                forecasting_data = self.app_functions.db.get_forecasting(self.app_functions.reportID)
                if forecasting_data and 'rmse' in forecasting_data and 'r2' in forecasting_data:
                    metrics_frame = QFrame()
                    metrics_frame.setStyleSheet("""
                        QFrame {
                            background-color: #2c313c;
                            border: 2px solid #3d4451;
                            border-radius: 10px;
                            margin-top: 10px;
                        }
                    """)
                    metrics_layout = QVBoxLayout(metrics_frame)
                    metrics_layout.setContentsMargins(20, 15, 20, 15)
                    metrics_layout.setSpacing(10)

                    # Title for metrics section
                    metrics_title = QLabel("Final Model Performance Metrics")
                    metrics_title.setStyleSheet("""
                        QLabel {
                            color: #00a6fb;
                            font-size: 18px;
                            font-weight: bold;
                            padding: 5px;
                        }
                    """)
                    metrics_title.setAlignment(Qt.AlignCenter)
                    metrics_layout.addWidget(metrics_title)

                    # R² Score Label with None handling
                    r2_value = forecasting_data['r2']
                    r2_text = f"R² Score on Test set: {r2_value:.4f}" if r2_value is not None else "R² Score on Test set: N/A"
                    r2_label = QLabel(r2_text)
                    r2_label.setStyleSheet("""
                        QLabel {
                            color: #ffffff;
                            font-size: 16px;
                            font-weight: bold;
                            padding: 5px;
                        }
                    """)
                    r2_label.setAlignment(Qt.AlignCenter)
                    metrics_layout.addWidget(r2_label)

                    # RMSE Score Label with None handling
                    rmse_value = forecasting_data['rmse']
                    rmse_text = f"RMSE Score on Test set: {rmse_value:.2f}" if rmse_value is not None else "RMSE Score on Test set: N/A"
                    rmse_label = QLabel(rmse_text)
                    rmse_label.setStyleSheet("""
                        QLabel {
                            color: #ffffff;
                            font-size: 16px;
                            font-weight: bold;
                            padding: 5px;
                        }
                    """)
                    rmse_label.setAlignment(Qt.AlignCenter)
                    metrics_layout.addWidget(rmse_label)

                    # Add metrics frame to the main layout in a new row
                    plot_layout.addWidget(metrics_frame, 2, 0, 1, 2)  # Span across both columns

            # Create main scroll area for all charts
            main_scroll = QScrollArea()
            main_scroll.setWidget(plot_container)
            main_scroll.setWidgetResizable(True)
            main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            main_scroll.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background-color: #2c313c;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #1b1e23;
                    width: 14px;
                    margin: 15px 0 15px 0;
                    border-radius: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #3d4451;
                    min-height: 30px;
                    border-radius: 7px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #00a6fb;
                }
                QScrollBar:horizontal {
                    border: none;
                    background: #1b1e23;
                    height: 14px;
                    margin: 0px 15px 0 15px;
                    border-radius: 0px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #3d4451;
                    min-width: 30px;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #00a6fb;
                }
            """)
            
            # Add the main scroll area to the content layout
            content_layout.addWidget(main_scroll)
            
            # Add the content container to the predictions page
            if hasattr(widgets, 'predictions_page'):
                # Get the existing layout
                existing_layout = widgets.predictions_page.layout()
                if existing_layout is None:
                    existing_layout = QVBoxLayout(widgets.predictions_page)
                    existing_layout.setSpacing(20)
                    existing_layout.setContentsMargins(20, 20, 20, 20)
                
                # Create a scroll area for the entire page
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                scroll_area.setWidget(content_container)
                
                # Add the scroll area to the existing layout
                existing_layout.addWidget(scroll_area)

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

        print(f"Button clicked: {btnName}")  # Debug print

        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home_2)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        elif btnName == "btn_dashboard":
            widgets.stackedWidget.setCurrentWidget(widgets.page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        elif btnName == "btn_predictions":
            print("Attempting to switch to predictions page...")  # Debug print
            try:
                widgets.stackedWidget.setCurrentWidget(widgets.predictions_page)
                print("Successfully switched to predictions page")  # Debug print
                UIFunctions.resetStyle(self, btnName)
                btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
                
                # Update prediction controls with current dataset columns
                if hasattr(self.app_functions, 'df'):
                    print("Updating prediction controls with dataset columns")  # Debug print
                    df = self.app_functions.df
                    
                    # Update target column combo
                    widgets.target_col_combo.clear()
                    widgets.target_col_combo.addItems(df.columns)
                    
                    # Update date column combos
                    all_columns = list(df.columns)
                    
                    # Update single date column combo
                    widgets.date_col_combo.clear()
                    widgets.date_col_combo.addItems(all_columns)
                    # Try to select a date column by default
                    for i, col in enumerate(all_columns):
                        if 'date' in col.lower():
                            widgets.date_col_combo.setCurrentIndex(i)
                            break
                    
                    # Update year/month/day combos
                    widgets.year_combo.clear()
                    widgets.month_combo.clear()
                    widgets.day_combo.clear()
                    
                    widgets.year_combo.addItems(all_columns)
                    widgets.month_combo.addItems(all_columns)
                    widgets.day_combo.addItems(all_columns)
                    
                    # Try to select appropriate columns by default
                    for i, col in enumerate(all_columns):
                        col_lower = col.lower()
                        if 'year' in col_lower:
                            widgets.year_combo.setCurrentIndex(i)
                        elif 'month' in col_lower:
                            widgets.month_combo.setCurrentIndex(i)
                        elif 'day' in col_lower:
                            widgets.day_combo.setCurrentIndex(i)
                    
                    # Connect radio buttons to stack switching
                    widgets.single_date_radio.toggled.connect(lambda checked: 
                        widgets.date_stack.setCurrentWidget(widgets.single_date_page if checked 
                        else widgets.multi_date_page))
                    
                    # Connect predict button
                    try:
                        widgets.predict_btn.clicked.disconnect()
                    except:
                        pass
                    widgets.predict_btn.clicked.connect(self.generate_predictions)
            except Exception as e:
                print(f"Error switching to predictions page: {str(e)}")  # Debug print

        elif btnName == "btn_print":
            self.generate_pdf_report()
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        elif btnName == "btn_chat":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        elif btnName == "btn_data":
            widgets.stackedWidget.setCurrentWidget(widgets.data_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        elif btnName == "btn_anlysis":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        elif btnName == "btn_new":
            print("New Report BTN clicked!")
            # Clear all user output and start fresh
            self._clear_chat_display()
            self._clear_questions()
            
            # Clear the DataFrame and related attributes
            self.app_functions.df = None
            self.app_functions.datasetID = None
            self.app_functions.dname = None
            self.app_functions.rname = None
            self.app_functions.reportID = None
            
            # Clear the summary text
            self.ui.summary_text.setText("")
            
            # Clear the table data
            self.ui.tableData.clear()
            self.ui.tableData.setRowCount(0)
            self.ui.tableData.setColumnCount(0)
            
            # Clear any existing charts
            if hasattr(self.app_functions, 'chart_paths'):
                self.app_functions.chart_paths = []
            
            # Clear the predictions page if it exists
            if hasattr(widgets, 'predictions_page'):
                # Remove all widgets from the predictions page
                layout = widgets.predictions_page.layout()
                if layout:
                    while layout.count():
                        item = layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
            
            # Clear the analyzer memory
            if hasattr(self.app_functions, 'analyzer'):
                self.app_functions.analyzer.memory = []
            
            # Clear any stored questions
            if hasattr(self.app_functions, 'g_questions'):
                self.app_functions.g_questions = []
            
            # Switch to the data page for new report setup
            widgets.stackedWidget.setCurrentWidget(widgets.data_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

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

    def show_column_dialog(self, column_index):
        """Show the column dialog when a column header is clicked"""
        column_name = widgets.tableData.horizontalHeaderItem(column_index).text()
        dialog = ColDialog(self, self.app_functions.df, column_name)
        dialog.setWindowTitle(f"Column Options - {column_name}")
        dialog.exec_()

    def generate_predictions(self):
        """Generate predictions using the time series forecaster"""
        try:
            if not hasattr(self.app_functions, 'df'):
                print("No dataset loaded!")
                return
            
            # Clear previous predictions but keep the controls
            if hasattr(widgets, 'predictions_page'):
                existing_layout = widgets.predictions_page.layout()
                if existing_layout:
                    # Keep track of the prediction controls
                    prediction_controls = None
                    for i in range(existing_layout.count()):
                        widget = existing_layout.itemAt(i).widget()
                        if widget and widget.objectName() == "prediction_controls":
                            prediction_controls = widget
                            break
                    
                    # Clear all widgets
                    while existing_layout.count():
                        item = existing_layout.takeAt(0)
                        if item.widget() and item.widget() != prediction_controls:
                            item.widget().deleteLater()
                    
                    # Add back the prediction controls if they existed
                    if prediction_controls:
                        existing_layout.addWidget(prediction_controls)
            
            df = self.app_functions.df
            target_col = widgets.target_col_combo.currentText()
            
            # Get date columns based on selection mode
            if widgets.single_date_radio.isChecked():
                date_cols = widgets.date_col_combo.currentText()
            else:
                date_cols = [
                    widgets.year_combo.currentText(),
                    widgets.month_combo.currentText(),
                    widgets.day_combo.currentText()
                ]
            
            horizon = widgets.horizon_spin.value()
            
            # Generate predictions and get plots
            predictions, plots = time_series_forecaster(
                dataframe=df,
                target_col=target_col,
                date_cols=date_cols,
                forecast_horizon=horizon
            )
            
            # 1. Save predictions DataFrame to CSV
            forecast_filename = f"forecast_{horizon}_{target_col}.csv"
            forecast_path = os.path.join(self.app_functions.rname, forecast_filename)
            predictions.to_csv(forecast_path, index=False)
            
            # 2. Create folder for charts and save them as PNG
            charts_folder = os.path.join(self.app_functions.rname, f"forecast_charts_{horizon}_{target_col}")
            os.makedirs(charts_folder, exist_ok=True)
            
            # Save each plot as PNG
            chart_paths = []
            for i, plot in enumerate(plots):
                if plot is not None:
                    chart_name = f"chart_{i+1}.png"
                    chart_path = os.path.join(charts_folder, chart_name)
                    plot.savefig(chart_path, bbox_inches='tight', dpi=300)
                    chart_paths.append(chart_path)
                    plt.close(plot)
            
            # 3. Save to database using DatabaseManager
            self.app_functions.db.saveForecasting(
                reportID=self.app_functions.reportID,
                target_column=target_col,
                predicted_df=forecast_path,
                rmse=predictions.get('rmse', None),  # Get RMSE if available
                r2=predictions.get('r2', None),      # Get R2 if available
                charts_path=charts_folder
            )
            
            # Create a container for the predictions page content
            content_container = QWidget()
            content_layout = QVBoxLayout(content_container)
            content_layout.setSpacing(20)
            content_layout.setContentsMargins(20, 20, 20, 20)
            
            # Create and add the feature DataFrame table
            feature_table = QTableWidget()
            feature_table.setColumnCount(len(predictions.columns))
            feature_table.setRowCount(len(predictions))
            feature_table.setHorizontalHeaderLabels(predictions.columns)
            
            # Fill the table with data
            for i in range(len(predictions)):
                for j in range(len(predictions.columns)):
                    item = QTableWidgetItem(str(predictions.iloc[i, j]))
                    feature_table.setItem(i, j, item)
            
            # Set table properties
            feature_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            feature_table.setMinimumHeight(200)
            feature_table.setMaximumHeight(400)
            feature_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            feature_table.setAlternatingRowColors(True)
            feature_table.setStyleSheet("""
                QTableWidget {
                    background-color: #2c313c;
                    alternate-background-color: #1b1e23;
                    gridline-color: #3d4451;
                    border: 1px solid #3d4451;
                    color: #ffffff;
                }
                QHeaderView::section {
                    background-color: #1b1e23;
                    color: #00a6fb;
                    padding: 4px;
                    border: 1px solid #3d4451;
                    font-weight: bold;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QTableWidget::item:selected {
                    background-color: #00a6fb;
                    color: #ffffff;
                }
            """)
            
            # Add table to content layout
            content_layout.addWidget(feature_table)
            
            # Create a container for the plots with proper styling
            plot_container = QFrame()
            plot_container.setStyleSheet("""
                QFrame {
                    background-color: #2c313c;
                    border: 2px solid #3d4451;
                    border-radius: 10px;
                }
            """)
            plot_layout = QGridLayout(plot_container)
            plot_layout.setSpacing(20)
            plot_layout.setContentsMargins(20, 20, 20, 20)
            
            # Get forecasting data from database
            if hasattr(self.app_functions, 'reportID'):
                forecasting_data = self.app_functions.db.get_forecasting(self.app_functions.reportID)
                if forecasting_data and 'charts_path' in forecasting_data:
                    # Load and display charts from the charts directory
                    charts_dir = forecasting_data['charts_path']
                    if os.path.exists(charts_dir):
                        chart_files = [f for f in os.listdir(charts_dir) if f.endswith('.png')]
                        for i, chart_file in enumerate(chart_files):
                            chart_path = os.path.join(charts_dir, chart_file)
                            if os.path.exists(chart_path):
                                # Create a frame for each chart section
                                chart_section = QFrame()
                                chart_section.setStyleSheet("""
                                    QFrame {
                                        background-color: #1b1e23;
                                        border: 2px solid #3d4451;
                                        border-radius: 10px;
                                    }
                                """)
                                # Set size policy to make charts fill their containers
                                chart_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                                chart_section.setMinimumSize(600, 500)
                                chart_section_layout = QVBoxLayout(chart_section)
                                chart_section_layout.setContentsMargins(0, 0, 0, 0)
                                chart_section_layout.setSpacing(0)

                                # Add title label
                                title = QLabel()
                                if i == 0:
                                    title.setText("Time Series Overview")
                                elif i == 1:
                                    title.setText("Feature Importance Analysis")
                                elif i == 2:
                                    title.setText("Actual vs Predicted Values")
                                elif i == 3:
                                    title.setText("Model Performance (R² Plot)")
                                
                                title.setStyleSheet("""
                                    QLabel {
                                        color: #00a6fb;
                                        font-size: 16px;
                                        font-weight: bold;
                                        padding: 15px;
                                        background-color: #2c313c;
                                        border-top-left-radius: 8px;
                                        border-top-right-radius: 8px;
                                        border-bottom: 2px solid #3d4451;
                                    }
                                """)
                                title.setAlignment(Qt.AlignCenter)
                                title.setFixedHeight(50)
                                chart_section_layout.addWidget(title)

                                # Create chart content widget with dark background
                                chart_content = QWidget()
                                chart_content.setStyleSheet("background-color: #1b1e23;")
                                chart_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                                chart_content_layout = QVBoxLayout(chart_content)
                                chart_content_layout.setContentsMargins(0, 0, 0, 0)
                                chart_content_layout.setSpacing(0)

                                # Create figure and load image with proper sizing
                                dpi = 100  # Set DPI for better resolution
                                fig_width = 580 / dpi  # Calculate figure width in inches
                                fig_height = 430 / dpi  # Calculate figure height in inches
                                fig = plt.figure(figsize=(fig_width, fig_height), dpi=dpi, tight_layout=True)
                                fig.patch.set_facecolor('#1b1e23')
                                ax = plt.gca()
                                ax.set_facecolor('#1b1e23')
                                
                                img = plt.imread(chart_path)
                                plt.imshow(img)
                                plt.axis('off')
                                
                                # Add the plot canvas with proper sizing
                                canvas = FigureCanvas(fig)
                                canvas.setStyleSheet("background-color: #1b1e23;")
                                canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                                chart_content_layout.addWidget(canvas)

                                # Add metrics labels if they exist
                                if 'rmse' in forecasting_data and 'r2' in forecasting_data:
                                    metrics_frame = QFrame()
                                    metrics_frame.setStyleSheet("""
                                        QFrame {
                                            background-color: #2c313c;
                                            border-radius: 5px;
                                            padding: 5px;
                                        }
                                    """)
                                    metrics_layout = QVBoxLayout(metrics_frame)  # Changed to vertical layout
                                    metrics_layout.setContentsMargins(10, 5, 10, 5)
                                    metrics_layout.setSpacing(5)  # Reduced spacing between labels

                                    # R² Score Label with None handling
                                    r2_value = forecasting_data['r2']
                                    r2_text = f"R² Score on Test set: {r2_value:.4f}" if r2_value is not None else "R² Score on Test set: N/A"
                                    r2_label = QLabel(r2_text)
                                    r2_label.setStyleSheet("""
                                        QLabel {
                                            color: #00a6fb;
                                            font-size: 14px;
                                            font-weight: bold;
                                            padding: 5px;
                                        }
                                    """)
                                    metrics_layout.addWidget(r2_label)

                                    # RMSE Score Label with None handling
                                    rmse_value = forecasting_data['rmse']
                                    rmse_text = f"RMSE Score on Test set: {rmse_value:.2f}" if rmse_value is not None else "RMSE Score on Test set: N/A"
                                    rmse_label = QLabel(rmse_text)
                                    rmse_label.setStyleSheet("""
                                        QLabel {
                                            color: #00a6fb;
                                            font-size: 14px;
                                            font-weight: bold;
                                            padding: 5px;
                                        }
                                    """)
                                    metrics_layout.addWidget(rmse_label)

                                    chart_content_layout.addWidget(metrics_frame)

                                # Create scroll area with proper sizing
                                chart_scroll = QScrollArea()
                                chart_scroll.setStyleSheet("""
                                    QScrollArea {
                                        border: none;
                                        background-color: #1b1e23;
                                    }
                                    QScrollBar:vertical {
                                        border: none;
                                        background: #1b1e23;
                                        width: 8px;
                                        margin: 0;
                                    }
                                    QScrollBar::handle:vertical {
                                        background-color: #3d4451;
                                        min-height: 30px;
                                        border-radius: 4px;
                                    }
                                    QScrollBar::handle:vertical:hover {
                                        background-color: #00a6fb;
                                    }
                                    QScrollBar:horizontal {
                                        border: none;
                                        background: #1b1e23;
                                        height: 8px;
                                        margin: 0;
                                    }
                                    QScrollBar::handle:horizontal {
                                        background-color: #3d4451;
                                        min-width: 30px;
                                        border-radius: 4px;
                                    }
                                    QScrollBar::handle:horizontal:hover {
                                        background-color: #00a6fb;
                                    }
                                """)
                                chart_scroll.setWidget(chart_content)
                                chart_scroll.setWidgetResizable(True)
                                chart_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                                chart_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                                chart_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                                chart_section_layout.addWidget(chart_scroll)

                                # Position the chart sections in the grid with proper spacing
                                plot_layout.setSpacing(10)
                                plot_layout.setContentsMargins(10, 10, 10, 10)
                                if i == 0:  # Time Series Overview
                                    plot_layout.addWidget(chart_section, 0, 0)
                                elif i == 1:  # Feature Importance
                                    plot_layout.addWidget(chart_section, 0, 1)
                                elif i == 2:  # Actual vs Predicted
                                    plot_layout.addWidget(chart_section, 1, 0)
                                elif i == 3:  # R² Plot
                                    plot_layout.addWidget(chart_section, 1, 1)

            # Create main scroll area for all charts
            main_scroll = QScrollArea()
            main_scroll.setWidget(plot_container)
            main_scroll.setWidgetResizable(True)
            main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            main_scroll.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background-color: #2c313c;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #1b1e23;
                    width: 14px;
                    margin: 15px 0 15px 0;
                    border-radius: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #3d4451;
                    min-height: 30px;
                    border-radius: 7px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #00a6fb;
                }
                QScrollBar:horizontal {
                    border: none;
                    background: #1b1e23;
                    height: 14px;
                    margin: 0px 15px 0 15px;
                    border-radius: 0px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #3d4451;
                    min-width: 30px;
                    border-radius: 7px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #00a6fb;
                }
            """)
            
            # Add the main scroll area to the content layout
            content_layout.addWidget(main_scroll)
            
            # Add the content container to the predictions page
            if hasattr(widgets, 'predictions_page'):
                # Get the existing layout
                existing_layout = widgets.predictions_page.layout()
                if existing_layout is None:
                    existing_layout = QVBoxLayout(widgets.predictions_page)
                    existing_layout.setSpacing(20)
                    existing_layout.setContentsMargins(20, 20, 20, 20)
                
                # Create a scroll area for the entire page
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                scroll_area.setWidget(content_container)
                
                # Add the scroll area to the existing layout
                existing_layout.addWidget(scroll_area)
            
        except Exception as e:
            print(f"Error generating predictions: {str(e)}")
            import traceback
            traceback.print_exc()

    def generate_pdf_report(self):
        """Generate a PDF report containing summary, questions, charts, and forecasting data"""
        try:
            if not hasattr(self.app_functions, 'reportID'):
                print("No report loaded!")
                return

            # Create PDF document
            report_name = f"{self.app_functions.rname}_report.pdf"
            doc = SimpleDocTemplate(report_name, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            elements.append(Paragraph(f"Report: {self.app_functions.rname}", title_style))
            elements.append(Spacer(1, 20))

            # Add summary section
            if hasattr(self.ui, 'summary_text'):
                summary = self.ui.summary_text.toPlainText()
                if summary:
                    elements.append(Paragraph("Summary", styles['Heading2']))
                    elements.append(Spacer(1, 10))
                    elements.append(Paragraph(summary, styles['Normal']))
                    elements.append(Spacer(1, 20))

            # Add questions section
            if hasattr(self.app_functions, 'g_questions') and self.app_functions.g_questions:
                elements.append(Paragraph("Questions", styles['Heading2']))
                elements.append(Spacer(1, 10))
                for i, question in enumerate(self.app_functions.g_questions, 1):
                    elements.append(Paragraph(f"{i}. {question}", styles['Normal']))
                elements.append(Spacer(1, 20))

            # Add charts section
            if hasattr(self.app_functions, 'chart_paths') and self.app_functions.chart_paths:
                elements.append(Paragraph("Charts", styles['Heading2']))
                elements.append(Spacer(1, 10))
                for chart_path in self.app_functions.chart_paths:
                    if os.path.exists(chart_path):
                        # Convert HTML chart to PNG if needed
                        if chart_path.endswith('.html'):
                            # You might need to use a headless browser to convert HTML to image
                            # For now, we'll skip HTML charts
                            continue
                        try:
                            img = Image(chart_path, width=6*inch, height=4*inch)
                            elements.append(img)
                            elements.append(Spacer(1, 20))
                        except Exception as e:
                            print(f"Error adding chart {chart_path}: {str(e)}")

            # Add forecasting section
            if hasattr(widgets, 'predictions_page'):
                elements.append(Paragraph("Forecasting", styles['Heading2']))
                elements.append(Spacer(1, 10))
                
                # Get forecasting data from the database
                forecasting_data = self.app_functions.db.get_forecasting(self.app_functions.reportID)
                if forecasting_data:
                    # Add RMSE and R2 scores if available
                    if 'rmse' in forecasting_data and forecasting_data['rmse']:
                        elements.append(Paragraph(f"RMSE Score: {forecasting_data['rmse']}", styles['Normal']))
                    if 'r2' in forecasting_data and forecasting_data['r2']:
                        elements.append(Paragraph(f"R2 Score: {forecasting_data['r2']}", styles['Normal']))
                    
                    # Add forecasting charts
                    if 'charts_path' in forecasting_data:
                        charts_dir = forecasting_data['charts_path']
                        if os.path.exists(charts_dir):
                            chart_files = [f for f in os.listdir(charts_dir) if f.endswith('.png')]
                            for chart_file in chart_files:
                                chart_path = os.path.join(charts_dir, chart_file)
                                try:
                                    img = Image(chart_path, width=6*inch, height=4*inch)
                                    elements.append(img)
                                    elements.append(Spacer(1, 20))
                                except Exception as e:
                                    print(f"Error adding forecasting chart {chart_path}: {str(e)}")

            # Build the PDF
            doc.build(elements)
            print(f"PDF report generated: {report_name}")

        except Exception as e:
            print(f"Error generating PDF report: {str(e)}")
            import traceback
            traceback.print_exc()

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
