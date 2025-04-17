#from Custom_Widgets import *
#from Custom_Widgets.QAppSettings import QAppSettings
#from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
from PySide6.QtCore import (QSettings, QTimer, QThread, Signal, Qt, QUrl)
from PySide6.QtGui import (QColor, QFont, QFontDatabase, QCursor, QIcon, QPixmap)
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect, QApplication, QMainWindow, 
    QFileDialog, QPushButton, QLabel, QDialog, QVBoxLayout, 
    QTableWidget, QTableWidgetItem, QSizePolicy, QHBoxLayout,
    QFrame, QCheckBox, QWidget, QLineEdit
)
from PySide6.QtSvg import QSvgRenderer
import shutil
from PySide6.QtCore import QFile
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6 import QtCore
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit,
                               QPushButton, QVBoxLayout, QWidget, QLabel,
                               QScrollArea, QSizePolicy, QHBoxLayout,
                               QFileDialog, QTableWidgetItem, QFrame, QCheckBox)

#from PySide6 import uic
import os
import subprocess
from OprFuncs import read_file, data_infer
from DataAnalyzer import DataAnalyzer
from LLM import *
from markdown import markdown
from functools import partial
from uiEXT.ChatBubble import ChatBubble
#from Axioradb import *
from docx import Document
from DatabaseManager import DatabaseManager
import sys
import platform
from datetime import datetime

# Add Shiboken path to sys.path if needed
shiboken_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Lib', 'site-packages', 'shiboken6')
if os.path.exists(shiboken_path) and shiboken_path not in sys.path:
    sys.path.append(shiboken_path)

class SummaryWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, analyzer):
        super().__init__()
        self.analyzer = analyzer

    def run(self):
        try:
            summary = self.analyzer.analysis_data()
            self.finished.emit(summary)
        except Exception as e:
            self.error.emit(str(e))

class GuiFunctions():
    def __init__(self, MainWindow, user_id):
        self.main_window = MainWindow
        self.ui = MainWindow.ui
        self.user_id = user_id
        self.db = DatabaseManager()
        self.llm = llama3b  
        self.selected_qu_list = [] 
        self.setup_connections()
        self.summary_worker = None 
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_animation)
        self.loading_dots = 0
        self.web_view = None  # Track web view instance
        
        # Create output directory with forward slashes
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Connect LLM selection change
        self.ui.llm_combo.currentTextChanged.connect(self.handle_llm_change)

    def setup_connections(self):
        self.main_window.ui.openfile_btn.clicked.connect(self.handle_data_button)
        self.main_window.ui.sum_btn.clicked.connect(self.handle_sum_btn)
        self.main_window.ui.btn_LLMs.clicked.connect(self.handle_btn_LLMs)
        self.main_window.ui.clean_data_btn.clicked.connect(self.handle_clean_data_btn)
        self.main_window.ui.qu_num_list.currentIndexChanged.connect(self.handle_qu_num)
        self.main_window.ui.qu_btn.clicked.connect(self.handle_qu_btn)
        self.main_window.ui.save_qu_btn.clicked.connect(self.handle_save_qu_btn)
        self.main_window.ui.chat_data_btn.clicked.connect(self.handle_chat_data_btn)
        self.main_window.ui.send_btn.clicked.connect(self.send_message)
        self.lineEdit_chat = self.main_window.ui.lineEdit_message
        self.main_window.ui.lineEdit_message.keyReleaseEvent = self.enter_return_release
        self.main_window.ui.qu_data_btn.clicked.connect(self.handle_word_btn)
        self.main_window.ui.btn_dashboard.clicked.connect(self.handle_dashboard_click)
        # Add done button connection
        self.main_window.ui.done_btn.clicked.connect(self.process_selected_questions)

    def handle_word_btn(self):
        fpath, _ = QFileDialog.getOpenFileName(
            self.main_window, "Open Word File", "", "Word Files (*.docx)"
        )
        if fpath:
            document = Document(fpath)
            full_text = []
            for para in document.paragraphs:
                full_text.append(para.text)
            word_content = '\n'.join(full_text)
            
            # Debug: Print the content of the Word file
            print("Word file content:")
            print(word_content)

            # Extract questions from the Word content
            questions = self.extract_questions(word_content)
            
            # Debug: Print the extracted questions
            print("Extracted questions:")
            print(questions)

            # Get references to UI components
            scroll_area = self.main_window.ui.scrollArea
            scroll_contents = self.main_window.ui.scrollAreaWidgetContents

            # Ensure proper widget hierarchy
            if not scroll_contents.layout():
                scroll_contents.setLayout(QVBoxLayout())

            qu_layout = scroll_contents.layout()
            qu_layout.setAlignment(Qt.AlignTop)

            # Clear previous questions
            while qu_layout.count():
                item = qu_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Add new questions with proper parenting
            if questions:
                for i, question in enumerate(questions, 1):
                    question_frame = QFrame(scroll_contents)
                    question_frame.setFrameShape(QFrame.StyledPanel)

                    hbox = QHBoxLayout(question_frame)
                    hbox.setContentsMargins(0, 0, 0, 0)  # Reduce margins
                    hbox.setSpacing(2)  # Reduce spacing between widgets

                    number_label = QLabel(f"{i}.", question_frame)
                    number_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                    hbox.addWidget(number_label)

                    question_label = QLabel(str(question), question_frame)
                    question_label.setWordWrap(True)
                    question_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    hbox.addWidget(question_label)

                    check_box = QCheckBox(question_frame)
                    check_box.setObjectName(f"checkbox_{i}")  # Set unique object name
                    check_box.setProperty("question", question)
                    check_box.stateChanged.connect(self.handle_question_selection)
                    hbox.addWidget(check_box)

                    qu_layout.addWidget(question_frame)

                # Ensure proper layout update
                scroll_contents.adjustSize()
                scroll_area.updateGeometry()
                QApplication.processEvents()  # Force UI refresh
            else:
                error_label = QLabel("No questions extracted. Please check your Word file.", scroll_contents)
                error_label.setAlignment(Qt.AlignCenter)
                qu_layout.addWidget(error_label)

            # Set widget if not already set (should be done once during initialization)
            if scroll_area.widget() != scroll_contents:
                scroll_area.setWidget(scroll_contents)

    def handle_data_button(self):
        dpath, _ = QFileDialog.getOpenFileName(
            self.main_window, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)"
        )
        if dpath:
            self.dpath = dpath
            self.dname = os.path.basename(dpath)
            self.rname = os.path.splitext(os.path.basename(dpath))[0]
            os.makedirs(self.rname, exist_ok=True)  
            self.datasetPath = os.path.join(self.rname, self.dname)
            shutil.copy(dpath, self.datasetPath) 
            self.location = self.main_window.ui.path_location
            self.location.setText(dpath)
            self.df = read_file(dpath)
            self._analyzer_attributes()
            self.datasetID = self.db.saveDataSet(path=self.datasetPath,
                                                 name=self.dname,
                                                 info=self.data_info,
                                                 summary=self.data_summary,
                                                 sample=self.data_sample,
                                                 cols=self.data_cols) 
            self.reportID = self.db.saveReport(user=self.user_id,
                                llm=self.db.llm_id_by_name(self.llm.model),
                                dataset=self.datasetID,
                                rname = self.rname)
            self._show_df()
            
    def _analyzer_attributes(self):
            self.analyzer = DataAnalyzer(dataframe=self.df, llm=self.llm)
            self.data_info = self.analyzer.data_info
            self.data_summary = self.analyzer.data_summary
            self.data_sample = self.analyzer.data_sample
            self.data_cols = self.analyzer.data_cols
    def _show_df(self):
            self.analyzer.report_id = self.reportID
            if "Index" not in self.df.columns:
                self.df.insert(0, "Index", self.df.index)
            self.table = self.main_window.ui.tableData
            self.table.setRowCount(self.df.shape[0])  
            self.table.setColumnCount(self.df.shape[1])  
            self.table.setHorizontalHeaderLabels(self.df.columns.astype(str))
            self.table.horizontalHeader().setVisible(True)
            self.table.resizeColumnsToContents()
            for i in range(self.df.shape[0]):
                for j in range(self.df.shape[1]):
                    self.table.setItem(i, j, QTableWidgetItem(str(self.df.iat[i, j])))

    def handle_sum_btn(self):
        # Disable the summary button and start loading animation
        self.main_window.ui.sum_btn.setEnabled(False)
        self.main_window.ui.sum_btn.setText("Generating")
        self.loading_timer.start(500)  # Update every 500ms
        
        # Create and configure the worker
        self.summary_worker = SummaryWorker(self.analyzer)
        self.summary_worker.finished.connect(self.handle_summary_complete)
        self.summary_worker.error.connect(self.handle_summary_error)
        self.summary_worker.start()
    def _update_summary_text(self,summary):
            summary_md = markdown(summary)
            self.main_window.ui.summary_text.setMarkdown(summary_md)

    def handle_summary_complete(self, summary):
        try:
            # Stop loading animation
            self.loading_timer.stop()
            self.main_window.ui.sum_btn.setText("Generate Summary")
            
            # Save to database and update UI
            self.db.saveSummary(reportID=self.reportID, summary_content=summary)
            self._update_summary_text(summary)
        except Exception as e:
            print(f"Error handling summary completion: {str(e)}")
        finally:
            # Reset UI state
            self.main_window.ui.sum_btn.setEnabled(True)
            self.main_window.ui.sum_btn.setText("Generate Summary")
            if self.summary_worker:
                self.summary_worker.deleteLater()
                self.summary_worker = None

    def handle_summary_error(self, error_message):
        # Stop loading animation
        self.loading_timer.stop()
        self.main_window.ui.sum_btn.setText("Generate Summary")
        print(f"Error generating summary: {error_message}")
        self.main_window.ui.sum_btn.setEnabled(True)
        
        if self.summary_worker:
            self.summary_worker.deleteLater()
            self.summary_worker = None

    def handle_btn_LLMs(self):
        print("Clicked LLM")

    def handle_clean_data_btn(self):
        self.cleaned_df = self.analyzer.drop_nulls()
        self.dname = f"cleaned_{self.dname}"
        self.cleaned_df_path = os.path.join(self.rname, self.dname)
        print(self.cleaned_df_path)
        self.cleaned_df.to_csv(self.cleaned_df_path, index=False)
        self.df = self.cleaned_df
        self._analyzer_attributes()
        self.datasetID = self.db.saveCleanDataset(ogID=self.datasetID,
                                path=self.cleaned_df_path,
                                name=self.dname,
                                info=self.data_info,
                                summary=self.data_summary,
                                sample=self.data_sample,
                                cols=self.data_cols)
        self.db.saveCleanDatasetReport(reportId=self.reportID,cleandataset=self.datasetID)
        self._show_df()

    def extract_questions(self, text):
        """Extracts questions from the text by splitting on newlines."""
        questions = [line.strip() for line in text.split('\n') if line.strip()]
        return questions

    def handle_qu_num(self, index):
        """Handles the selection of the number of questions."""
        self.ques_num_list = self.main_window.ui.qu_num_list  # Get the dropdown list
        self.num_qu = self.ques_num_list.currentText()  # Get text directly

        try:
            self.num_qu = int(self.ques_num_list.currentText().strip())
        except ValueError:
            print(f"⚠️ Invalid selection: {self.num_qu}. Defaulting to 1")
            self.num_qu = 1

        print(f"Number of questions to generate: {self.num_qu}")

    def handle_qu_btn(self):
        # Validate analyzer state
        if not hasattr(self, 'analyzer') or self.analyzer is None:
            print("Analyzer not initialized. Load data first.")
            return

        # Generate questions with error handling and retry mechanism
        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                self.g_questions = self.analyzer.questions_gen(self.num_qu)
                if not isinstance(self.g_questions, list):
                    self.g_questions = []  # Ensure it's a list
            except Exception as e:
                print(f"Question generation failed: {str(e)}")
                self.g_questions = []

            # Validate the number of generated questions
            if len(self.g_questions) == self.num_qu:
                break
            else:
                print(f"Warning: Expected {self.num_qu} questions, but got {len(self.g_questions)}")
                retries += 1

        # Clear the selected questions list when generating new questions
        self.selected_qu_list = []
        self._ques_add()

    def _ques_add(self): # Get references to UI components
        scroll_area = self.main_window.ui.scrollArea
        scroll_contents = self.main_window.ui.scrollAreaWidgetContents

        # Ensure proper widget hierarchy
        if not scroll_contents.layout():
            scroll_contents.setLayout(QVBoxLayout())

        qu_layout = scroll_contents.layout()
        qu_layout.setAlignment(Qt.AlignTop)

        # Clear previous questions
        while qu_layout.count():
            item = qu_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new questions with proper parenting
        if self.g_questions:
            for i, question in enumerate(self.g_questions, 1):
                question_frame = QFrame(scroll_contents)
                question_frame.setFrameShape(QFrame.StyledPanel)

                hbox = QHBoxLayout(question_frame)
                hbox.setContentsMargins(0, 0, 0, 0)  # Reduce margins
                hbox.setSpacing(2)  # Reduce spacing between widgets

                number_label = QLabel(f"{i}.", question_frame)
                number_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                hbox.addWidget(number_label)

                question_label = QLabel(str(question), question_frame)
                question_label.setWordWrap(True)
                question_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                hbox.addWidget(question_label)

                # Create checkbox with the question
                check_box = QCheckBox(question_frame)
                check_box.setObjectName(f"checkbox_{i}")
                
                # Create a custom slot for this specific checkbox
                def create_slot(q):
                    return lambda checked: self.handle_question_selection(q, checked)
                
                # Connect with the custom slot
                slot = create_slot(question)
                check_box.toggled.connect(slot)
                
                hbox.addWidget(check_box)
                qu_layout.addWidget(question_frame)

            # Ensure proper layout update
            scroll_contents.adjustSize()
            scroll_area.updateGeometry()
            QApplication.processEvents()  # Force UI refresh
        else:
            error_label = QLabel("No questions generated. Please check your data.", scroll_contents)
            error_label.setAlignment(Qt.AlignCenter)
            qu_layout.addWidget(error_label)

        # Set widget if not already set (should be done once during initialization)
        if scroll_area.widget() != scroll_contents:
            scroll_area.setWidget(scroll_contents)

    def handle_question_selection(self, question, checked):
        if checked:
            if question not in self.selected_qu_list:
                self.selected_qu_list.append(question)
        else:
            if question in self.selected_qu_list:
                self.selected_qu_list.remove(question)
     
    def handle_save_qu_btn(self):
        self.saved_questions = set()
        for qu in self.selected_qu_list:
            if qu not in self.saved_questions:  
                self.db.saveQuestion(reportID=self.reportID, question=qu)
                self.saved_questions.add(qu) 
        self.qu_saved = True

#
    def handle_chat_data_btn(self):
        cfpath, _ = QFileDialog.getOpenFileName(
            self.main_window, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)"
        )
        if cfpath:
            chat_df = read_file()
            chat_analyzer = DataAnalyzer(dataframe=chat_df, llm=self.llm)
            chat_df_anlysis = chat_analyzer.analysis_data()
            return chat_df_anlysis

    def enter_return_release(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.send_message()
    def _add_user_message(self,user_input):
            user_msg = ChatBubble(user_input, True, "You")
            self.main_window.ui.chat_layout.addWidget(user_msg)
            self.lineEdit_chat.clear()
    def _add_ai_message(self,ai_response):
        ai_msg = ChatBubble(ai_response, False, "AI")
        self.main_window.ui.chat_layout.addWidget(ai_msg)


    def send_message(self):
        print("send_message called")  # Debugging statement
        user_input = self.lineEdit_chat.text()
        if user_input:
            self._add_user_message(user_input=user_input)
            if not hasattr(self, 'analyzer') or not self.analyzer:
                print("Analyzer not initialized!")
                ai_response = "Upload a dataset first."
                ai_msg = ChatBubble(ai_response, False, "AI")
                self.main_window.ui.chat_layout.addWidget(ai_msg)
            else:
                ai_response = self.analyzer.chat(user_input)
                self._add_ai_message(ai_response)

    def process_selected_questions(self):
        """Process selected questions and generate charts"""
        if not self.selected_qu_list:
            print("No questions selected!")
            print("Debug: Current selections:", self.selected_qu_list)
            return
        
        print(f"Processing {len(self.selected_qu_list)} selected questions")
        print(f"Selected questions: {self.selected_qu_list}")
        
        try:
            # Save questions and create dashboard first
            for qu in self.selected_qu_list:
                if not hasattr(self, 'saved_questions'):
                    self.saved_questions = set()
                if qu not in self.saved_questions:
                    self.db.saveQuestion(reportID=self.reportID, question=qu)
                    self.saved_questions.add(qu)
            
            # Create dashboard
            self.dashboardID = self.db.addDashboard(reportID=self.reportID)
            print(f"Created dashboard with ID: {self.dashboardID}")
            
            # Process each question and generate charts
            for question in self.selected_qu_list:
                # Get chart type and column from the question
                chart_info = self.analyzer._chart_select_chain(question)
                
                # Generate visualization
                chart_path = self.analyzer.visual(
                    chart_type=chart_info['chart_type'],
                    column_name=chart_info['columns'],
                    data=self.analyzer.dataframe
                )
                
                if chart_path and os.path.exists(chart_path):
                    print(f"Successfully generated chart at: {chart_path}")
                    self.db.saveCharts(dashID=self.dashboardID, path=chart_path)
            
            # Configure the page widget
            page_widget = self.main_window.ui.page
            if page_widget.layout():
                QWidget().setLayout(page_widget.layout())
            page_layout = QVBoxLayout(page_widget)
            page_layout.setContentsMargins(0, 0, 0, 0)
            page_layout.setSpacing(0)
            
            # Configure widget_3
            widget_3 = self.main_window.ui.widget_3
            widget_3.setMinimumSize(800, 600)
            widget_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            page_layout.addWidget(widget_3)
            
            # Switch to the visualization page
            self.main_window.ui.stackedWidget.setCurrentWidget(self.main_window.ui.page)
            
            # Display the chart
            self.display_current_chart()
            
        except Exception as e:
            print(f"Error processing questions: {str(e)}")
            import traceback
            traceback.print_exc()

    def display_current_chart(self):
        """Display the current chart in widget_3"""
        try:
            # Switch to the visualization page first
            self.main_window.ui.stackedWidget.setCurrentWidget(self.main_window.ui.page)
            
            # Get or create the page layout
            page_widget = self.main_window.ui.page
            if not page_widget.layout():
                page_layout = QVBoxLayout(page_widget)
                page_layout.setContentsMargins(0, 0, 0, 0)
                page_layout.setSpacing(0)
            else:
                page_layout = page_widget.layout()
            
            # Clear any existing widgets from the page layout
            while page_layout.count():
                item = page_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
                    item.widget().deleteLater()
            
            # Create new widget_3
            self.main_window.ui.widget_3 = QWidget(page_widget)
            self.main_window.ui.widget_3.setObjectName("widget_3")
            self.main_window.ui.widget_3.setMinimumSize(800, 600)
            self.main_window.ui.widget_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Create layout for widget_3
            widget_3_layout = QVBoxLayout(self.main_window.ui.widget_3)
            widget_3_layout.setContentsMargins(0, 0, 0, 0)
            widget_3_layout.setSpacing(0)
            
            # Get a list of all HTML files in the output directory
            if os.path.exists(self.output_dir):
                html_files = sorted(
                    [f for f in os.listdir(self.output_dir) if f.endswith('.html')],
                    key=lambda x: os.path.getmtime(os.path.join(self.output_dir, x)),
                    reverse=True
                )
                print(f"Found {len(html_files)} HTML files in {self.output_dir}:")
                for file in html_files:
                    print(f"- {file}")
            else:
                print(f"Directory {self.output_dir} does not exist")
                return
            
            # Check if there are any HTML files
            if not html_files:
                print("No chart files found in the directory")
                return
            
            # Get the most recent chart file
            current_chart_file = html_files[0]
            current_chart_path = os.path.join(self.output_dir, current_chart_file)
            
            print(f"Looking for chart at: {current_chart_path}")
            
            if os.path.exists(current_chart_path):
                print(f"Found chart file: {current_chart_path}")
                
                # Clean up old web view if it exists
                if self.web_view is not None:
                    self.web_view.setParent(None)
                    self.web_view.deleteLater()
                
                # Create new web view widget
                self.web_view = QWebEngineView(self.main_window.ui.widget_3)
                
                # Enable JavaScript and other settings
                settings = self.web_view.settings()
                settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
                settings.setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, True)
                
                # Configure web view
                self.web_view.setMinimumSize(800, 600)
                self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                
                # Add interaction settings
                self.web_view.page().setBackgroundColor(Qt.transparent)
                self.web_view.setAttribute(Qt.WA_TranslucentBackground)
                self.web_view.setContextMenuPolicy(Qt.NoContextMenu)
                
                # Convert to absolute file URL
                abs_path = os.path.abspath(current_chart_path)
                file_url = QUrl.fromLocalFile(abs_path)
                print(f"Loading URL: {file_url.toString()}")
                
                # Connect signals
                self.web_view.loadFinished.connect(self._on_load_finished)
                self.web_view.page().loadFinished.connect(lambda ok: self._inject_interaction_js() if ok else None)
                
                # Load the HTML file
                self.web_view.load(file_url)
                
                # Add web view to widget_3 layout
                widget_3_layout.addWidget(self.web_view)
                
                # Add widget_3 to page layout
                page_layout.addWidget(self.main_window.ui.widget_3)
                
                # Show everything
                self.web_view.show()
                self.main_window.ui.widget_3.show()
                page_widget.show()
                
                print(f"Successfully displayed chart from: {current_chart_path}")
            else:
                print(f"Chart file not found: {current_chart_path}")
                
        except Exception as e:
            print(f"Error displaying chart: {str(e)}")
            import traceback
            traceback.print_exc()

    def _inject_interaction_js(self):
        """Inject JavaScript to enhance chart interactivity"""
        js = """
        if (window.Plotly) {
            var gd = document.querySelector('.plotly-graph-div');
            if (gd) {
                Plotly.relayout(gd, {
                    'showlink': false,
                    'modeBarButtonsToRemove': ['sendDataToCloud'],
                    'responsive': true,
                    'displayModeBar': true,
                    'scrollZoom': true,
                    'editable': true,
                    'dragmode': 'zoom'
                });
                
                // Enable single-click interactions
                gd.on('plotly_click', function(data) {
                    var point = data.points[0];
                    // Handle click event
                    console.log('Clicked point:', point);
                });
                
                // Make chart responsive
                window.addEventListener('resize', function() {
                    Plotly.Plots.resize(gd);
                });
            }
        }
        """
        self.web_view.page().runJavaScript(js)

    def _on_load_finished(self, ok):
        """Handle web view load finished event"""
        if ok:
            print("Chart loaded successfully")
            self._inject_interaction_js()
        else:
            print("Failed to load chart")

    def show_previous_chart(self):
        """Show the previous chart"""
        if hasattr(self, 'current_chart_index') and self.current_chart_index > 0:
            self.current_chart_index -= 1
            self.display_current_chart()

    def show_next_chart(self):
        """Show the next chart"""
        if hasattr(self, 'current_chart_index') and hasattr(self, 'total_charts'):
            if self.current_chart_index < self.total_charts - 1:
                self.current_chart_index += 1
                self.display_current_chart()

    def create_navigation_controls(self):
        """Create navigation controls for multiple charts"""
        # Create navigation widget
        self.nav_widget = QWidget()
        nav_layout = QHBoxLayout(self.nav_widget)
        
        # Create navigation buttons
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.chart_counter = QLabel()
        
        # Add buttons to layout
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.chart_counter)
        nav_layout.addWidget(self.next_btn)
        
        # Connect button signals
        self.prev_btn.clicked.connect(self.show_previous_chart)
        self.next_btn.clicked.connect(self.show_next_chart)
        
        # Add navigation widget to widget_3
        widget_3 = self.main_window.ui.widget_3
        if not widget_3.layout():
            widget_3.setLayout(QVBoxLayout())
        widget_3.layout().addWidget(self.nav_widget)

    def display_svg(self, svg_path=None):
        """Display an SVG file in widget_3"""
        try:
            # If no specific SVG path is provided, look for charts in the output directory
            if svg_path is None:
                output_dir = "output"
                if os.path.exists(output_dir):
                    html_files = sorted(
                        [f for f in os.listdir(output_dir) if f.endswith('.html')],
                        key=lambda x: os.path.getmtime(os.path.join(output_dir, x)),
                        reverse=True
                    )
                    if html_files:
                        # Display the most recent chart
                        self.display_current_chart()
                        return
                    else:
                        print("No charts found in output directory")
                        return
                else:
                    print(f"Output directory {output_dir} does not exist")
                    return
            
            # If a specific SVG path is provided, verify it exists
            if not isinstance(svg_path, str):
                raise ValueError("SVG path must be a string")
            
            if not os.path.exists(svg_path):
                print(f"SVG file not found: {svg_path}")
                return None
            
            # Create SVG widget
            self.svg_widget = QSvgWidget()
            self.svg_widget.load(svg_path)  # Load the SVG file
            
            # Configure widget
            self.svg_widget.setMinimumSize(400, 300)
            self.svg_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Get widget_3 and set up layout
            widget_3 = self.main_window.ui.widget_3
            if not widget_3.layout():
                widget_3.setLayout(QVBoxLayout())
            
            # Clear existing content
            layout = widget_3.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Add SVG widget
            layout.addWidget(self.svg_widget)
            
            # Show everything
            self.svg_widget.show()
            widget_3.show()
            
            print(f"Successfully displayed SVG from: {svg_path}")
            return self.svg_widget
            
        except Exception as e:
            print(f"Error displaying SVG: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def update_loading_animation(self):
        self.loading_dots = (self.loading_dots + 1) % 4
        self.main_window.ui.sum_btn.setText(f"Generating{'.' * self.loading_dots}")

    def handle_llm_change(self, model_name):
        """Handle LLM model selection change"""
        if model_name == "llama3b":
            llm = llama3b.model
            if not self.is_model_installed(llm):
                self.install_model(self.db.llm_installtion_code(llm.model))
            self.llm = llama3b
        elif model_name == "phi35":
            llm = phi35.model
            if not self.is_model_installed(llm):
                self.install_model(self.db.llm_installtion_code(llm.model))
            self.llm = phi35
            
        # Update analyzer if it exists
        if hasattr(self, 'analyzer'):
            self.analyzer.llm = self.llm
            
        print(f"LLM model changed to: {model_name}")


    def is_model_installed(self, model_name):
        # Run `ollama list` to check if the model is installed
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        return model_name in result.stdout

    def install_model(self, install_code):
        # Execute the installation code in the terminal
        process = subprocess.run(install_code, shell=True, capture_output=True, text=True)
        if process.returncode != 0:
            raise RuntimeError(f"Failed to install model: {process.stderr}")

    def handle_dashboard_click(self):
        """Handle dashboard button click by displaying the most recent chart"""
        print("Opening dashboard view...")
        # Switch to the visualization page
        self.main_window.ui.stackedWidget.setCurrentWidget(self.main_window.ui.page)
        # Display the most recent chart
        self.display_current_chart()
