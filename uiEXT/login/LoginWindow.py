# LoginWindow.py
from PySide6.QtWidgets import QMainWindow, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, Signal
from PySide6.QtGui import QColor
from uiEXT.login.ui_login import Ui_Login 
from uiEXT.login.circular_progress import CircularProgress

counter = 0

class LoginWindow(QMainWindow):
    # Add a custom signal that will be emitted when login is accepted
    login_accepted = Signal()
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        
        # REMOVE TITLE BAR AND MAKE TRANSLUCENT
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # IMPORT AND CONFIGURE CIRCULAR PROGRESS
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
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.ui.bg.setGraphicsEffect(self.shadow)

        # QTIMER TO UPDATE THE PROGRESS
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)

        # OVERRIDE KEY RELEASE EVENT FOR THE QLineEdits
        self.ui.username.keyReleaseEvent = self.check_login
        self.ui.password.keyReleaseEvent = self.check_login

        self.show()

    def check_login(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            username = self.ui.username.text()
            password = self.ui.password.text()

            if username and password == "123456":
                self.ui.user_description.setText(f"Welcome {username}!")
                self.ui.user_description.setStyleSheet("#user_description { color: #bdff00 }")
                self.ui.username.setStyleSheet("#username:focus { border: 3px solid #bdff00; }")
                self.ui.password.setStyleSheet("#password:focus { border: 3px solid #bdff00; }")
                # Emit the login_accepted signal after a short delay (allowing the progress/animation)
                QTimer.singleShot(1200, lambda: self.login_accepted.emit())
            else:
                self.ui.username.setStyleSheet("#username:focus { border: 3px solid rgb(255, 0, 127); }")
                self.ui.password.setStyleSheet("#password:focus { border: 3px solid rgb(255, 0, 127); }")
                self.shacke_window()  # (Consider renaming this method to shake_window)

        # Call the base class event handler if needed
        return super().keyReleaseEvent(event)

    def shacke_window(self):
        # Shake the window to indicate error
        actual_pos = self.pos()
        QTimer.singleShot(0, lambda: self.move(actual_pos.x() + 1, actual_pos.y()))
        QTimer.singleShot(50, lambda: self.move(actual_pos.x() - 2, actual_pos.y()))
        QTimer.singleShot(100, lambda: self.move(actual_pos.x() + 4, actual_pos.y()))
        QTimer.singleShot(150, lambda: self.move(actual_pos.x() - 5, actual_pos.y()))
        QTimer.singleShot(200, lambda: self.move(actual_pos.x() + 4, actual_pos.y()))
        QTimer.singleShot(250, lambda: self.move(actual_pos.x() - 2, actual_pos.y()))
        QTimer.singleShot(300, lambda: self.move(actual_pos.x(), actual_pos.y()))

    def update_progress(self):
        global counter
        self.progress.set_value(counter)
        if counter >= 100:
            self.timer.stop()
            self.animation_login()
        counter += 1

    def animation_login(self):
        self.animation = QPropertyAnimation(self.ui.frame_widgets, b"geometry")
        self.animation.setDuration(1500)
        self.animation.setStartValue(QRect(0, 70, self.ui.frame_widgets.width(), self.ui.frame_widgets.height()))
        self.animation.setEndValue(QRect(0, -325, self.ui.frame_widgets.width(), self.ui.frame_widgets.height()))
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()
