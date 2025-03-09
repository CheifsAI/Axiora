#from Custom_Widgets import *
#from Custom_Widgets.QAppSettings import QAppSettings
#from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import (QGraphicsDropShadowEffect, QApplication, QMainWindow, 
                             QFileDialog, QPushButton, QLabel, QDialog, QVBoxLayout, 
                             QTableWidget, QTableWidgetItem, QSizePolicy)
from PySide6.QtSvg import QSvgRenderer
import shutil
from PySide6.QtCore import QFile
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6 import QtCore
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt,QUrl
from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit,
                               QPushButton, QVBoxLayout, QWidget, QLabel,
                               QScrollArea, QSizePolicy, QHBoxLayout,
                               QFileDialog, QTableWidgetItem, QFrame, QCheckBox)

#from PySide6 import uic
import os
from OprFuncs import read_file, data_infer
from DataAnalyzer import DataAnalyzer
from LLM import *
from markdown import markdown
from functools import partial
from uiEXT.ChatBubble import ChatBubble
#from Axioradb import *
from docx import Document
from DatabaseManager import DatabaseManager

class GuiFunctions():
    def __init__(self, MainWindow,user_id):
        self.main_window = MainWindow
        self.ui = MainWindow.ui
        self.user_id = user_id
        self.db = DatabaseManager()
        self.llm = llama3b
        self.selected_qu_list = []  # Initialize empty list
        self.setup_connections()

    def setup_connections(self):
        self.main_window.ui.openfile_btn.clicked.connect(self.handle_data_button)
        self.main_window.ui.sum_btn.clicked.connect(self.handle_sum_btn)
        self.main_window.ui.btn_LLMs.clicked.connect(self.handle_btn_LLMs)
        self.main_window.ui.clean_data_btn.clicked.connect(self.handle_clean_data_btn)
        self.main_window.ui.qu_num_list.currentIndexChanged.connect(self.handle_qu_num)
        self.main_window.ui.qu_btn.clicked.connect(self.handle_qu_btn)
        self.main_window.ui.chat_data_btn.clicked.connect(self.handle_chat_data_btn)
        self.main_window.ui.send_btn.clicked.connect(self.send_message)
        self.main_window.ui.lineEdit_message.keyReleaseEvent = self.enter_return_release
        self.main_window.ui.qu_data_btn.clicked.connect(self.handle_word_btn)
        self.main_window.ui.pushButton_2.clicked.connect(self.display_svg)
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
            self.analyzer = DataAnalyzer(dataframe=self.df, llm=self.llm)
            self.data_info = self.analyzer.data_info
            self.data_summary = self.analyzer.data_summary
            self.data_sample = self.analyzer.data_sample
            self.data_cols = self.analyzer.data_cols
            self.datasetID = self.db.saveDataSet(path=self.datasetPath,
                                                 name=self.dname,
                                                 info=self.data_info,
                                                 summary=self.data_summary,
                                                 sample=self.data_sample,
                                                 cols=self.data_cols) 
            self.sessionID = self.db.saveSession(user=self.user_id,
                                llm=self.db.llm_id_by_name(self.llm.model),
                                dataset=self.datasetID)
            self.df.insert(0, "Index", self.df.index)

            self.table = self.main_window.ui.tableData
            self.table.setRowCount(self.df.shape[0])  # Set number of rows
            self.table.setColumnCount(self.df.shape[1])  # Set number of columns (including index)

            # Ensure column headers are correctly applied
            self.table.setHorizontalHeaderLabels(self.df.columns.astype(str))

            # Ensure visibility and auto-resizing
            self.table.horizontalHeader().setVisible(True)
            self.table.resizeColumnsToContents()

            # Populate the table with data
            for i in range(self.df.shape[0]):
                for j in range(self.df.shape[1]):
                    self.table.setItem(i, j, QTableWidgetItem(str(self.df.iat[i, j])))

    def handle_sum_btn(self):
        self.summary = self.analyzer.analysis_data()
        self.db.saveSummary(session=self.sessionID,summary_content=self.summary)
        self.summary_md = markdown(self.summary)
        self.summary_text = self.main_window.ui.summary_text
        self.summary_text.setMarkdown(self.summary_md)

    def handle_btn_LLMs(self):
        print("Clicked LLM")

    def handle_clean_data_btn(self):
        self.cleaned_df = self.analyzer.drop_nulls()
        self.dname = f"cleaned_{self.dname}"
        self.cleaned_df_path = os.path.join(self.rname, self.dname)
        print(self.cleaned_df_path)
        self.cleaned_df.to_csv(self.cleaned_df_path, index=False)
        self.df = self.cleaned_df
        self.analyzer = DataAnalyzer(dataframe=self.df, llm=self.llm)
        self.data_info = self.analyzer.data_info
        self.data_summary = self.analyzer.data_summary
        self.data_sample = self.analyzer.data_sample
        self.data_cols = self.analyzer.data_cols
        self.datasetID = self.db.saveCleanDataset(ogID=self.datasetID,
                                path=self.cleaned_df_path,
                                name=self.dname,
                                info=self.data_info,
                                summary=self.data_summary,
                                sample=self.data_sample,
                                cols=self.data_cols)
        self.db.saveCleanSession(sessId=self.sessionID,cleandataset=self.datasetID)
        self.table = self.main_window.ui.tableData
        self.table.setRowCount(self.df.shape[0])  # Set number of rows
        self.table.setColumnCount(self.df.shape[1])  # Set number of columns
        self.table.setHorizontalHeaderLabels(self.df.columns)  # Set column headers
        header = self.table.horizontalHeader()
        # header.setStyleSheet("QHeaderView::section { background-color: lightgray; }")
        # Populate the table with data
        for i in range(self.df.shape[0]):
            for j in range(self.df.shape[1]):
                self.table.setItem(i, j, QTableWidgetItem(str(self.df.iat[i, j])))

    import re

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

    def send_question_to_model(self, question, state):
        if state == Qt.Checked:
            response = self.analyzer.chat(question)
            ai_msg = ChatBubble(str(response), False, "AI")
            self.main_window.ui.chat_layout.addWidget(ai_msg)
        else:
            print(f"Question unchecked: {question}")

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

    def send_message(self):
        print("send_message called")  # Debugging statement
        lineEdit_chat = self.main_window.ui.lineEdit_message
        user_input = lineEdit_chat.text()
        if user_input:
            user_msg = ChatBubble(user_input, True, "You")
            self.main_window.ui.chat_layout.addWidget(user_msg)
            lineEdit_chat.clear()
            if not hasattr(self, 'analyzer') or not self.analyzer:
                print("Analyzer not initialized!")
                ai_response = "Upload a dataset first."
                ai_msg = ChatBubble(ai_response, False, "AI")
                self.main_window.ui.chat_layout.addWidget(ai_msg)
            else:
                ai_response = self.analyzer.chat(user_input)
                ai_msg = ChatBubble(ai_response, False, "AI")
                self.main_window.ui.chat_layout.addWidget(ai_msg)

    def process_selected_questions(self):
        """Process selected questions and generate charts"""
        if not self.selected_qu_list:
            print("No questions selected!")
            print("Debug: Current selections:", self.selected_qu_list)
            return
        
        print(f"Processing {len(self.selected_qu_list)} selected questions")
        print(f"Selected questions: {self.selected_qu_list}")
        
        try:
            # Get visualization code for all selected questions
            vis_codes = self.analyzer.visual(
                questions_list=self.selected_qu_list,
                report=self.rname  # Use the dataset directory
            )
            
            # Execute each visualization code
            for i, code in enumerate(vis_codes):
                #try:
                    # Import required modules in the execution environment
                    exec_env = {
                        'df': self.analyzer.dataframe,
                        #'pygal': __import__('pygal'),
                        #'RedBlueStyle': getattr(__import__('pygal.style'), 'RedBlueStyle')
                    }
                    
                    # Clean up the code and ensure proper file path
                    code = "\n".join(line.strip() for line in code.splitlines() if line.strip())
                    
                    # Replace the chart rendering path to use numbered filenames
                    #chart_path = os.path.join(self.rname, f"chart_{i+1}.svg")
                    #code = code.replace(
                      #  "chart.render_to_file('{report}/{chart_title}.svg')",
                     #   f"chart.render_to_file(r'{chart_path}')"
                    #)
                    
                    print(f"Executing visualization code for question {i+1}:")
                    print(code)
                    
                    # Execute the visualization code
                    exec(code, exec_env)
                    
                    # Verify the file was created
                    #if os.path.exists(chart_path):
                     #   print(f"Successfully created chart: {chart_path}")
                    #else:
                     #   print(f"Failed to create chart: {chart_path}")
                      #  self.create_error_svg(chart_path, f"Error generating chart for question {i+1}")
                    
                #except Exception as e:
                 #   print(f"Error executing visualization code for question {i+1}: {str(e)}")
                  #  error_file = os.path.join(self.rname, f"chart_{i+1}.svg")
                   # self.create_error_svg(error_file, f"Error: {str(e)}")
            
            # Set up for chart display
            self.current_chart_index = 0
            self.total_charts = len(self.selected_qu_list)
            
            # Display the first chart
            self.display_current_chart()
            
            # Switch to the visualization page
            self.main_window.ui.stackedWidget.setCurrentWidget(self.main_window.ui.page)
            
        except Exception as e:
            print(f"Error processing questions: {str(e)}")
            import traceback
            traceback.print_exc()

    def create_error_svg(self, chart_path, error_message):
        """Create a simple SVG with an error message"""
        try:
            svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
                <rect width="100%" height="100%" fill="#2b2b2b"/>
                <text x="50%" y="50%" text-anchor="middle" fill="white" font-family="Arial">
                    {error_message}
                </text>
            </svg>'''
            
            with open(chart_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            print(f"Error SVG created at {chart_path}")
        except Exception as e:
            print(f"Error creating error SVG: {str(e)}")
            import traceback
            traceback.print_exc()

    def display_current_chart(self):
        """Display the current chart in widget_3"""
        try:
            # Ensure we have a valid chart index
            if not hasattr(self, 'current_chart_index'):
                print("No current chart index set")
                return
            
            # Get a list of all .svg files in the directory
            svg_files = [f for f in os.listdir(self.rname) if f.endswith('.svg')]
            
            # Check if there are any .svg files
            if not svg_files:
                print("No SVG files found in the directory")
                return
            
            # Ensure the current_chart_index is within bounds
            if self.current_chart_index < 0 or self.current_chart_index >= len(svg_files):
                print("Invalid chart index")
                return
            
            # Get the current chart file
            current_chart_file = svg_files[self.current_chart_index]
            current_chart_path = os.path.join(self.rname, current_chart_file)
            
            print(f"Looking for chart at: {current_chart_path}")
            
            if os.path.exists(current_chart_path):
                print(f"Found chart file: {current_chart_path}")
                
                # Create navigation buttons if they don't exist
                if not hasattr(self, 'nav_widget'):
                    self.create_navigation_controls()
                
                # Display the SVG
                if self.display_svg(current_chart_path):
                    # Update navigation button states
                    if hasattr(self, 'prev_btn') and hasattr(self, 'next_btn'):
                        self.prev_btn.setEnabled(self.current_chart_index > 0)
                        self.next_btn.setEnabled(self.current_chart_index < len(svg_files) - 1)
                    
                    # Update chart counter label
                    if hasattr(self, 'chart_counter'):
                        self.chart_counter.setText(f"Chart {self.current_chart_index + 1} of {len(svg_files)}")
                else:
                    print("Failed to display SVG widget")
            else:
                print(f"Chart file not found: {current_chart_path}")
                # Create error SVG if chart is missing
                self.create_error_svg(current_chart_path, "Chart file not found")
                
        except Exception as e:
            print(f"Error displaying chart: {str(e)}")
            import traceback
            traceback.print_exc()

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

    def show_previous_chart(self):
        """Show the previous chart"""
        if self.current_chart_index > 0:
            self.current_chart_index -= 1
            self.display_current_chart()

    def show_next_chart(self):
        """Show the next chart"""
        if self.current_chart_index < self.total_charts - 1:
            self.current_chart_index += 1
            self.display_current_chart()

    def display_svg(self, svg_path):
        """Display an SVG file in widget_3"""
        try:
            # Verify the file exists and is a valid path
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
            
            # Clear existing content except navigation controls
            layout = widget_3.layout()
            while layout.count() > 1:  # Keep navigation controls
                item = layout.takeAt(1)
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
