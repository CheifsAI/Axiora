from Custom_Widgets import *
#from Custom_Widgets.QAppSettings import QAppSettings
#from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
#from PySide6.QtCore import QSettings, QTimer
#from PySide6.QtGui import QColor, QFont, QFontDatabase
#from PySide6.QtWidgets import QGraphicsDropShadowEffect, QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QSizePolicy
from PySide6.QtSvg import QSvgRenderer
import shutil
from PySide6.QtCore import QFile
from PySide6.QtWebEngineWidgets import QWebEngineView 
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
        self.selected_qu_list = []
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
        self.web_view = QWebEngineView()
        self.main_window.ui.gridLayout_2.addWidget(self.web_view)
        self.load_svg("Teams Played Away.svg") 

    def load_svg(self, file_path):
        # Debug: Check if the file exists
        if not QFile.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return

        # Load the SVG file as an HTML page
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SVG Viewer</title>
        </head>
        <body style="margin: 0; padding: 0;">
            <object data="{file_path}" type="image/svg+xml" width="100%" height="100%"></object>
        </body>
        </html>
        """
        self.web_view.setHtml(html_content, QUrl.fromLocalFile(file_path))
        print(f"SVG file loaded from: {file_path}")
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
                    check_box.stateChanged.connect(partial(self.handle_question_selection, question))
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
            self.datasetID = self.db.saveDataSet(path=self.datasetPath,name=self.dname) 
            self.db.saveMetaData(id=self.datasetID,
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
        self.summary = markdown(self.analyzer.analysis_data())
        self.summary_text = self.main_window.ui.summary_text
        self.summary_text.setMarkdown(self.summary)

    def handle_btn_LLMs(self):
        print("Clicked LLM")

    def handle_clean_data_btn(self):
        self.cleaned_df = self.analyzer.drop_nulls()
        output_path = os.path.join(self.rname, f"cleaned_{self.fname}")
        self.cleaned_df.to_csv(output_path, index=False)
        self.table = self.main_window.ui.tableData
        self.table.setRowCount(self.cleaned_df.shape[0])  # Set number of rows
        self.table.setColumnCount(self.cleaned_df.shape[1])  # Set number of columns
        self.table.setHorizontalHeaderLabels(self.cleaned_df.columns)  # Set column headers
        header = self.table.horizontalHeader()
        # header.setStyleSheet("QHeaderView::section { background-color: lightgray; }")
        # Populate the table with data
        for i in range(self.cleaned_df.shape[0]):
            for j in range(self.cleaned_df.shape[1]):
                self.table.setItem(i, j, QTableWidgetItem(str(self.cleaned_df.iat[i, j])))

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

                check_box = QCheckBox(question_frame)
                check_box.stateChanged.connect(partial(self.handle_question_selection, question))
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

    def handle_question_selection(self, question, state):
        if state == Qt.Checked:
            if question not in self.selected_qu_list:
                self.selected_qu_list.append(question)
            print(f"Question selected: {question}")
        else:
            if question in self.selected_qu_list:
                self.selected_qu_list.remove(question)
            print(f"Question deselected: {question}")

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
