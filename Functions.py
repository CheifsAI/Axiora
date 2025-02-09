from Custom_Widgets import *
from Custom_Widgets.QAppSettings import QAppSettings
from Custom_Widgets.QCustomTipOverlay import QCustomTipOverlay
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
import sys
#from PyQt5 import uic
from OprFuncs import read_file, data_infer
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
         self.main_window.ui.chat_data_btn.clicked.connect(self.handle_chat_data_btn)
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
    def handle_qu_num(self, index):
        self.ques_num_list = self.main_window.ui.qu_num_list
        self.num_qu = self.ques_num_list.itemText(index)
        if self.num_qu.isdigit():  # Ensure it's a valid number
            self.num_qu = int(self.num_qu)
        else:
            self.num_qu = 1  # Default to 1 if invalid

    def handle_qu_btn(self):
        if not isinstance(self.num_qu, int) or self.num_qu <= 0:
            print("Invalid number of questions selected.")
            return

        self.g_questions = self.analyzer.questions_gen(self.num_qu)

        if self.g_questions:
            scrollAreaWidgetContents = self.main_window.ui.scrollAreaWidgetContents
            qu_layout = self.main_window.ui.qu_layout  # Existing layout

            # Debugging
            print("scrollAreaWidgetContents:", scrollAreaWidgetContents)
            print("Type:", type(scrollAreaWidgetContents))

            if scrollAreaWidgetContents is None:
                print("Error: scrollAreaWidgetContents is None! Check UI setup.")
                return

            # Remove this incorrect check, since the debug output proves it's a QWidget
            # if not isinstance(scrollAreaWidgetContents, QWidget):
            #     print("Error: scrollAreaWidgetContents is not a QWidget!")
            #     return

            # Clear previous widgets
            while qu_layout.count():
                item = qu_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            # Add checkboxes for the generated questions
            for question in self.g_questions:
                checkBox = QCheckBox(question, scrollAreaWidgetContents)
                qu_layout.addWidget(checkBox)

            # Ensure UI updates
            scrollAreaWidgetContents.setLayout(qu_layout)
            self.main_window.ui.scrollArea.setWidget(scrollAreaWidgetContents)
            scrollAreaWidgetContents.adjustSize()  # Ensure proper resizing

        else:
            print("No questions generated.")




    def handle_chat_data_btn(self):
        cfpath, _ = QFileDialog.getOpenFileName(
            self.main_window, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xls *.xlsx)"
        )
        if cfpath:
            chat_df = read_file()
            chat_analyzer = DataAnalyzer(dataframe=chat_df,llm=self.llm)
            chat_df_anlysis = chat_analyzer.analysis_data()
            return chat_df_anlysis

            
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
