from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget
from buttons import MyButton  # Import the custom button class

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 471)

        self.centralwidget = QWidget(MainWindow)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)

        self.left = QWidget(self.centralwidget)
        self.verticalLayout = QVBoxLayout(self.left)

        # Create the first custom button using MyButton from buttons.py
        self.pushButton = MyButton("Button 1", ":/feather/icons/feather/align-justify.png")
        self.verticalLayout.addWidget(self.pushButton)

        # Create the second custom button
        self.pushButton_2 = MyButton("Home", ":/feather/icons/feather/home.png")
        self.verticalLayout.addWidget(self.pushButton_2)

        # Create the third custom button
        self.pushButton_3 = MyButton("List", ":/feather/icons/feather/list.png")
        self.verticalLayout.addWidget(self.pushButton_3)

        # Add left layout to the main layout
        self.horizontalLayout.addWidget(self.left)

        # Connect custom button signals to custom slots (optional)
        self.pushButton.clicked_signal.connect(self.on_button1_clicked)
        self.pushButton_2.clicked_signal.connect(self.on_button2_clicked)
        self.pushButton_3.clicked_signal.connect(self.on_button3_clicked)

    def on_button1_clicked(self):
        print("Button 1 action triggered!")

    def on_button2_clicked(self):
        print("Home action triggered!")

    def on_button3_clicked(self):
        print("List action triggered!")
