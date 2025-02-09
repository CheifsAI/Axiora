from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
import sys
#from PyQt5 import uic
from OprFuncs import read_file
from DataAnalyzer import DataAnalyzer
#from PyQt5.QtWidgets import QMenu, QAction
from Models import *
from markdown import markdown

class GuiFunctions():
    def __init__(self,MainWindow):
        self.main_window = MainWindow
        self.ui = MainWindow.ui
        self.llm = llama3b
        self.setup_connections()

    def setup_connections(self):
         self.main_window.ui.openfile_btn.clicked.connect(self.handle_data_button)
         self.main_window.ui.sum_btn.clicked.connect(self.handle_sum_btn)
         self.main_window.ui.btn_LLMs.clicked.connect(self.handle_btn_LLMs)
         self.main_window.ui.clean_data_btn.clicked.connect(self.handle_clean_data_btn)
         self.main_window.ui.qu_num_list.currentIndexChanged.connect(self.handle_qu_num)
         self.main_window.ui.qu_btn.clicked.connect(self.handle_qu_btn)

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
        print(self.summary)

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
    def handle_qu_num(self,index):
        self.ques_num_list = self.main_window.ui.qu_num_list
        self.num_qu = self.ques_num_list.itemText(index)
        return self.num_qu
    def handle_qu_btn(self):
        # Generate questions
        self.g_questions = self.analyzer.quetions_gen(self.num_qu)
        
        if self.g_questions:
            scrollAreaWidgetContents = self.main_window.ui.scrollAreaWidgetContents
            qu_layout = self.main_window.ui.qu_layout
            while qu_layout.count():
                item = qu_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            # Add a checkbox for each question in g_questions
            for i, question in enumerate(self.g_questions):
                checkBox = QCheckBox(parent = scrollAreaWidgetContents)  # Create a new QCheckBox
                checkBox.setObjectName(f"checkBox_{i}")  # Set a unique object name
                checkBox.setText(question)  # Set the checkbox text to the question
                qu_layout.addWidget(checkBox)  # Add the checkbox to the layout
            
            # Set the layout for the scroll area widget contents
            scrollAreaWidgetContents.setLayout(qu_layout)
            self.scrollArea.setWidget(scrollAreaWidgetContents)
            
            
# Functions.py

class ChatHandler:
    def __init__(self):
        # Initialize the chat handler with an empty dictionary to store user messages
        self.user_messages = {}

    def handle_message(self, user, message):
        """
        Handles a new message from a user.

        Args:
            user (str): The username of the sender.
            message (str): The content of the message.

        Returns:
            str: A response to the message.
        """

        # Check if the user is already in the chat
        if user not in self.user_messages:
            # If not, add them with an empty list of messages
            self.user_messages[user] = []

        # Add the new message to the user's list of messages
        self.user_messages[user].append(message)

        # Generate a response based on the message content
        if "hello" in message.lower():
            return f"Hello {user}!"
        elif "goodbye" in message.lower():
            return f"Goodbye {user}, it was nice chatting with you!"
        else:
            return "What's up?"

    def get_user_messages(self, user):
        """
        Gets the list of messages from a specific user.

        Args:
            user (str): The username of the sender.

        Returns:
            list: A list of messages sent by the user.
        """

        # Check if the user is in the chat
        if user not in self.user_messages:
            return []

        # Return the list of messages for the user
        return self.user_messages[user]
