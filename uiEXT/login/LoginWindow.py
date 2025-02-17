from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel,
                               QScrollArea, QSizePolicy, QHBoxLayout, QFileDialog, QTableWidgetItem, QFrame)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from uiEXT.login.ui_login import Ui_Login 
from uiEXT.login.circular_progress import CircularProgress
counter = 0

class LoginWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        # GET WIDGETS FROM "ui_login.py"
        # Load widgets inside LoginWindow
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        
        # REMOVE TITLE BAR
        # ///////////////////////////////////////////////////////////////
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # IMPORT CIRCULAR PROGRESS
        # ///////////////////////////////////////////////////////////////
        self.progress = CircularProgress()
        self.progress.width = 240
        self.progress.height = 240
        self.progress.value = 0
        self.progress.setFixedSize(self.progress.width, self.progress.height)
        self.progress.font_size = 20
        self.progress.add_shadow(True)
        self.progress.progress_width = 4
        self.progress.progress_color = QColor("#bdff00")
        self.progress.text_color = QColor("#E6E6E6")
        self.progress.bg_color = QColor("#222222")
        self.progress.setParent(self.ui.preloader)
        self.progress.show()

        # ADD DROP SHADOW
        # ///////////////////////////////////////////////////////////////
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.ui.bg.setGraphicsEffect(self.shadow)

        # QTIMER
        # ///////////////////////////////////////////////////////////////
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

        # KEY PRESS EVENT
        # ///////////////////////////////////////////////////////////////
        self.ui.username.keyReleaseEvent = self.check_login
        self.ui.password.keyReleaseEvent = self.check_login

        self.show()

    # CHECK LOGIN
    # ///////////////////////////////////////////////////////////////
    def check_login(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            username = self.ui.username.text()
            password = self.ui.password.text()

            def open_main():
                from Axiora import MainWindow
                self.main = MainWindow()
                self.main.show()                
                self.close()

            if username and password == "123456":
                self.ui.user_description.setText(f"Welcome {username}!")
                self.ui.user_description.setStyleSheet("#user_description { color: #bdff00 }")
                self.ui.username.setStyleSheet("#username:focus { border: 3px solid #bdff00; }")
                self.ui.password.setStyleSheet("#password:focus { border: 3px solid #bdff00; }")
                QTimer.singleShot(1200, lambda: open_main())
            else:
                # SET STYLESHEET
                self.ui.username.setStyleSheet("#username:focus { border: 3px solid rgb(255, 0, 127); }")
                self.ui.password.setStyleSheet("#password:focus { border: 3px solid rgb(255, 0, 127); }")
                self.shacke_window()
            

    def shacke_window(self):
        # SHACKE WINDOW
        actual_pos = self.pos()
        QTimer.singleShot(0, lambda: self.move(actual_pos.x() + 1, actual_pos.y()))
        QTimer.singleShot(50, lambda: self.move(actual_pos.x() + -2, actual_pos.y()))
        QTimer.singleShot(100, lambda: self.move(actual_pos.x() + 4, actual_pos.y()))
        QTimer.singleShot(150, lambda: self.move(actual_pos.x() + -5, actual_pos.y()))
        QTimer.singleShot(200, lambda: self.move(actual_pos.x() + 4, actual_pos.y()))
        QTimer.singleShot(250, lambda: self.move(actual_pos.x() + -2, actual_pos.y()))
        QTimer.singleShot(300, lambda: self.move(actual_pos.x(), actual_pos.y()))

    # UPDATE PROGRESS BAR
    # ///////////////////////////////////////////////////////////////
    def update(self):
        global counter

        # SET VALUE TO PROGRESS BAR
        self.progress.set_value(counter)

        # CLOSE SPLASH SCREEN AND OPEN MAIN APP
        if counter >= 100:
            # STOP TIMER
            self.timer.stop()
            self.animation_login()

        # INCREASE COUNTER
        counter += 1

    # START ANIMATION TO LOGIN
    # ///////////////////////////////////////////////////////////////
    def animation_login(self):
        # ANIMATION
        self.animation = QPropertyAnimation(self.ui.frame_widgets, b"geometry")
        self.animation.setDuration(1500)
        self.animation.setStartValue(QRect(0, 70, self.ui.frame_widgets.width(), self.ui.frame_widgets.height()))
        self.animation.setEndValue(QRect(0, -325, self.ui.frame_widgets.width(), self.ui.frame_widgets.height()))
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
