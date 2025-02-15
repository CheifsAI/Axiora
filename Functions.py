from Custom_Widgets import *
#from Custom_Widgets.QAppSettings import QAppSettings
#from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
#from PySide6.QtCore import QSettings, QTimer
#from PySide6.QtGui import QColor, QFont, QFontDatabase
#from PySide6.QtWidgets import QGraphicsDropShadowEffect, QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QSizePolicy
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit,
                               QPushButton, QVBoxLayout, QWidget, QLabel,
                               QScrollArea, QSizePolicy, QHBoxLayout,
                               QFileDialog, QTableWidgetItem, QFrame)

#from PySide6 import uic
from OprFuncs import read_file, data_infer
from DataAnalyzer import DataAnalyzer
from Models import *
from markdown import markdown
from uiEXT.ChatBubble import ChatBubble

class GuiFunctions():
    def __init__(self,MainWindow):
        self.main_window = MainWindow
        self.ui = MainWindow.ui
        self.llm = llama3b
        #self.chat_page = Ui_chat_page()
        #self.chat_page = setupUi
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

    def handle_data_button(self):
        fpath, _ = QFileDialog.getOpenFileName(
            self.main_window, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)"
        )
        if fpath:
            self.location = self.main_window.ui.path_location
            self.location.setText(fpath)
            self.df = read_file(fpath)
            self.analyzer = DataAnalyzer(dataframe=self.df,llm=self.llm)

            # Convert index to a column
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
        #menu = QMenu()
        print("Clicked LLM")

    def handle_clean_data_btn(self):
        self.cleaned_df = self.analyzer.drop_nulls()
        self.table = self.main_window.ui.tableData
        self.table.setRowCount(self.cleaned_df.shape[0])  # Set number of rows
        self.table.setColumnCount(self.cleaned_df.shape[1])  # Set number of columns
        self.table.setHorizontalHeaderLabels(self.cleaned_df.columns)  # Set column headers
        header = self.table.horizontalHeader()
        #header.setStyleSheet("QHeaderView::section { background-color: lightgray; }")
        # Populate the table with data
        for i in range(self.cleaned_df.shape[0]):
            for j in range(self.cleaned_df.shape[1]):
                self.table.setItem(i, j, QTableWidgetItem(str(self.cleaned_df.iat[i, j])))
    
# result = quetions_gen(llm=llm,dataframe=df1,num=2)
# for i, question in enumerate(result, 1):
#    print(markdown(question))
    def handle_qu_num(self, index):
        # More robust index handling
        self.ques_num_list = self.main_window.ui.qu_num_list
        self.num_qu = self.ques_num_list.itemData(index)  # Use itemData for numerical values
        if not isinstance(self.num_qu, int) or self.num_qu <= 0:
            print(f"Invalid question number: {self.num_qu}. Defaulting to 1")
            self.num_qu = 1
        print(f"Number of questions to generate: {self.num_qu}")

    def handle_qu_btn(self):
        # Validate analyzer state
        if not hasattr(self, 'analyzer') or self.analyzer is None:
            print("Analyzer not initialized. Load data first.")
            return

        # Generate questions with error handling
        try:
            self.g_questions = self.analyzer.questions_gen(self.num_qu)
            if not isinstance(self.g_questions, list):
                self.g_questions = []  # Ensure it's a list
        except Exception as e:
            print(f"Question generation failed: {str(e)}")
            self.g_questions = []

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
                
                qu_layout.addWidget(question_frame)

                # Automatically send the question to the model
                self.send_question_to_model(question, Qt.Checked)

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
            chat_analyzer = DataAnalyzer(dataframe=chat_df,llm=self.llm)
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
