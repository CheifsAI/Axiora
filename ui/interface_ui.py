# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'interface.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QStackedWidget,
    QVBoxLayout, QWidget)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(804, 471)
        font = QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.left = QWidget(self.centralwidget)
        self.left.setObjectName(u"left")
        self.verticalLayout = QVBoxLayout(self.left)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget_4 = QWidget(self.left)
        self.widget_4.setObjectName(u"widget_4")
        self.verticalLayout_4 = QVBoxLayout(self.widget_4)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.pushButton = QPushButton(self.widget_4)
        self.pushButton.setObjectName(u"pushButton")
        icon = QIcon()
        icon.addFile(u":/feather/icons/feather/align-justify.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton.setIcon(icon)

        self.verticalLayout_4.addWidget(self.pushButton)


        self.verticalLayout.addWidget(self.widget_4, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.widget_5 = QWidget(self.left)
        self.widget_5.setObjectName(u"widget_5")
        self.verticalLayout_3 = QVBoxLayout(self.widget_5)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.Home = QPushButton(self.widget_5)
        self.Home.setObjectName(u"Home")
        icon1 = QIcon()
        icon1.addFile(u":/feather/icons/feather/home.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Home.setIcon(icon1)

        self.verticalLayout_3.addWidget(self.Home)

        self.Data = QPushButton(self.widget_5)
        self.Data.setObjectName(u"Data")
        icon2 = QIcon()
        icon2.addFile(u":/feather/icons/feather/list.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Data.setIcon(icon2)

        self.verticalLayout_3.addWidget(self.Data)

        self.Reborts = QPushButton(self.widget_5)
        self.Reborts.setObjectName(u"Reborts")
        icon3 = QIcon()
        icon3.addFile(u":/feather/icons/feather/printer.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Reborts.setIcon(icon3)

        self.verticalLayout_3.addWidget(self.Reborts)

        self.Graphs = QPushButton(self.widget_5)
        self.Graphs.setObjectName(u"Graphs")
        icon4 = QIcon()
        icon4.addFile(u":/feather/icons/feather/pie-chart.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Graphs.setIcon(icon4)

        self.verticalLayout_3.addWidget(self.Graphs)


        self.verticalLayout.addWidget(self.widget_5, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.widget_6 = QWidget(self.left)
        self.widget_6.setObjectName(u"widget_6")
        self.verticalLayout_2 = QVBoxLayout(self.widget_6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.Setting = QPushButton(self.widget_6)
        self.Setting.setObjectName(u"Setting")
        icon5 = QIcon()
        icon5.addFile(u":/feather/icons/feather/settings.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Setting.setIcon(icon5)

        self.verticalLayout_2.addWidget(self.Setting)

        self.Information = QPushButton(self.widget_6)
        self.Information.setObjectName(u"Information")
        icon6 = QIcon()
        icon6.addFile(u":/feather/icons/feather/info.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Information.setIcon(icon6)

        self.verticalLayout_2.addWidget(self.Information)

        self.Help = QPushButton(self.widget_6)
        self.Help.setObjectName(u"Help")
        icon7 = QIcon()
        icon7.addFile(u":/feather/icons/feather/help-circle.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Help.setIcon(icon7)

        self.verticalLayout_2.addWidget(self.Help)


        self.verticalLayout.addWidget(self.widget_6, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignBottom)


        self.horizontalLayout.addWidget(self.left, 0, Qt.AlignmentFlag.AlignLeft)

        self.center = QWidget(self.centralwidget)
        self.center.setObjectName(u"center")
        self.center.setMaximumSize(QSize(200, 16777215))
        self.verticalLayout_5 = QVBoxLayout(self.center)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.widget = QWidget(self.center)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.CloseLeftSideBar = QPushButton(self.widget)
        self.CloseLeftSideBar.setObjectName(u"CloseLeftSideBar")
        icon8 = QIcon()
        icon8.addFile(u":/feather/icons/feather/x-circle.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.CloseLeftSideBar.setIcon(icon8)

        self.horizontalLayout_2.addWidget(self.CloseLeftSideBar)


        self.verticalLayout_5.addWidget(self.widget)

        self.stackedWidget = QStackedWidget(self.center)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.setting = QWidget()
        self.setting.setObjectName(u"setting")
        self.verticalLayout_6 = QVBoxLayout(self.setting)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_3)

        self.widget_2 = QWidget(self.setting)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_7 = QVBoxLayout(self.widget_2)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_2 = QLabel(self.widget_2)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_7.addWidget(self.label_2)

        self.frame = QFrame(self.widget_2)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.comboBox = QComboBox(self.frame)
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout_3.addWidget(self.comboBox)


        self.verticalLayout_7.addWidget(self.frame)


        self.verticalLayout_6.addWidget(self.widget_2, 0, Qt.AlignmentFlag.AlignVCenter)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_2)

        self.stackedWidget.addWidget(self.setting)
        self.information = QWidget()
        self.information.setObjectName(u"information")
        self.verticalLayout_8 = QVBoxLayout(self.information)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_4 = QLabel(self.information)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_8.addWidget(self.label_4, 0, Qt.AlignmentFlag.AlignVCenter)

        self.stackedWidget.addWidget(self.information)
        self.help = QWidget()
        self.help.setObjectName(u"help")
        self.verticalLayout_9 = QVBoxLayout(self.help)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_5 = QLabel(self.help)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_9.addWidget(self.label_5, 0, Qt.AlignmentFlag.AlignVCenter)

        self.stackedWidget.addWidget(self.help)

        self.verticalLayout_5.addWidget(self.stackedWidget)


        self.horizontalLayout.addWidget(self.center)

        self.main = QWidget(self.centralwidget)
        self.main.setObjectName(u"main")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.main.sizePolicy().hasHeightForWidth())
        self.main.setSizePolicy(sizePolicy)
        self.verticalLayout_10 = QVBoxLayout(self.main)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.hedar = QWidget(self.main)
        self.hedar.setObjectName(u"hedar")
        self.horizontalLayout_7 = QHBoxLayout(self.hedar)
        self.horizontalLayout_7.setSpacing(5)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(5, 5, 5, 5)
        self.label_6 = QLabel(self.hedar)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_7.addWidget(self.label_6, 0, Qt.AlignmentFlag.AlignLeft)

        self.frame_3 = QFrame(self.hedar)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMaximumSize(QSize(90, 16777215))
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_6.setSpacing(5)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(5, 5, 5, 5)
        self.notification = QPushButton(self.frame_3)
        self.notification.setObjectName(u"notification")
        icon9 = QIcon()
        icon9.addFile(u":/feather/icons/feather/bell.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.notification.setIcon(icon9)

        self.horizontalLayout_6.addWidget(self.notification)

        self.more = QPushButton(self.frame_3)
        self.more.setObjectName(u"more")
        icon10 = QIcon()
        icon10.addFile(u":/feather/icons/feather/more-horizontal.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.more.setIcon(icon10)

        self.horizontalLayout_6.addWidget(self.more)

        self.persone = QPushButton(self.frame_3)
        self.persone.setObjectName(u"persone")
        icon11 = QIcon()
        icon11.addFile(u":/feather/icons/feather/user.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.persone.setIcon(icon11)

        self.horizontalLayout_6.addWidget(self.persone)


        self.horizontalLayout_7.addWidget(self.frame_3)

        self.searching = QFrame(self.hedar)
        self.searching.setObjectName(u"searching")
        self.searching.setMinimumSize(QSize(150, 0))
        self.searching.setMaximumSize(QSize(150, 16777215))
        self.searching.setFrameShape(QFrame.Shape.StyledPanel)
        self.searching.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.searching)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(5, 5, 5, 5)
        self.label_8 = QLabel(self.searching)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMinimumSize(QSize(16, 16))
        self.label_8.setMaximumSize(QSize(16, 16))
        self.label_8.setPixmap(QPixmap(u":/feather/icons/feather/search.png"))
        self.label_8.setScaledContents(True)
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_8.addWidget(self.label_8)

        self.lineEdit = QLineEdit(self.searching)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_8.addWidget(self.lineEdit)

        self.pushButton_10 = QPushButton(self.searching)
        self.pushButton_10.setObjectName(u"pushButton_10")
        self.pushButton_10.setMinimumSize(QSize(55, 30))
        self.pushButton_10.setMaximumSize(QSize(55, 30))

        self.horizontalLayout_8.addWidget(self.pushButton_10)


        self.horizontalLayout_7.addWidget(self.searching)

        self.frame_4 = QFrame(self.hedar)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMinimumSize(QSize(90, 0))
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(5, 5, 5, 5)
        self.minimize = QPushButton(self.frame_4)
        self.minimize.setObjectName(u"minimize")
        icon12 = QIcon()
        icon12.addFile(u":/feather/icons/feather/window_minimize.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.minimize.setIcon(icon12)

        self.horizontalLayout_9.addWidget(self.minimize, 0, Qt.AlignmentFlag.AlignLeft)

        self.restore = QPushButton(self.frame_4)
        self.restore.setObjectName(u"restore")
        icon13 = QIcon()
        icon13.addFile(u":/feather/icons/feather/square.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.restore.setIcon(icon13)

        self.horizontalLayout_9.addWidget(self.restore)

        self.close = QPushButton(self.frame_4)
        self.close.setObjectName(u"close")
        icon14 = QIcon()
        icon14.addFile(u":/feather/icons/feather/window_close.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.close.setIcon(icon14)

        self.horizontalLayout_9.addWidget(self.close)


        self.horizontalLayout_7.addWidget(self.frame_4, 0, Qt.AlignmentFlag.AlignLeft)


        self.verticalLayout_10.addWidget(self.hedar, 0, Qt.AlignmentFlag.AlignTop)

        self.maincontent = QWidget(self.main)
        self.maincontent.setObjectName(u"maincontent")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.maincontent.sizePolicy().hasHeightForWidth())
        self.maincontent.setSizePolicy(sizePolicy1)
        self.horizontalLayout_10 = QHBoxLayout(self.maincontent)
        self.horizontalLayout_10.setSpacing(5)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(5, 5, 5, 5)
        self.main_2 = QWidget(self.maincontent)
        self.main_2.setObjectName(u"main_2")
        self.verticalLayout_11 = QVBoxLayout(self.main_2)
        self.verticalLayout_11.setSpacing(5)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(5, 5, 5, 5)
        self.stackedWidget_2 = QStackedWidget(self.main_2)
        self.stackedWidget_2.setObjectName(u"stackedWidget_2")
        self.home = QWidget()
        self.home.setObjectName(u"home")
        self.verticalLayout_12 = QVBoxLayout(self.home)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.label_9 = QLabel(self.home)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_12.addWidget(self.label_9)

        self.stackedWidget_2.addWidget(self.home)
        self.data = QWidget()
        self.data.setObjectName(u"data")
        self.verticalLayout_13 = QVBoxLayout(self.data)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.label_10 = QLabel(self.data)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_13.addWidget(self.label_10)

        self.stackedWidget_2.addWidget(self.data)
        self.report = QWidget()
        self.report.setObjectName(u"report")
        self.verticalLayout_14 = QVBoxLayout(self.report)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.label_11 = QLabel(self.report)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_14.addWidget(self.label_11)

        self.stackedWidget_2.addWidget(self.report)
        self.graphs = QWidget()
        self.graphs.setObjectName(u"graphs")
        self.verticalLayout_15 = QVBoxLayout(self.graphs)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.label_12 = QLabel(self.graphs)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_15.addWidget(self.label_12)

        self.stackedWidget_2.addWidget(self.graphs)

        self.verticalLayout_11.addWidget(self.stackedWidget_2)


        self.horizontalLayout_10.addWidget(self.main_2)

        self.right = QWidget(self.maincontent)
        self.right.setObjectName(u"right")
        self.right.setMinimumSize(QSize(200, 0))
        self.verticalLayout_16 = QVBoxLayout(self.right)
        self.verticalLayout_16.setSpacing(5)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(5, 5, 5, 5)
        self.widget_3 = QWidget(self.right)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_11 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_13 = QLabel(self.widget_3)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_11.addWidget(self.label_13)

        self.CloseRightSideBar = QPushButton(self.widget_3)
        self.CloseRightSideBar.setObjectName(u"CloseRightSideBar")
        self.CloseRightSideBar.setIcon(icon8)

        self.horizontalLayout_11.addWidget(self.CloseRightSideBar)


        self.verticalLayout_16.addWidget(self.widget_3)

        self.stackedWidget_3 = QStackedWidget(self.right)
        self.stackedWidget_3.setObjectName(u"stackedWidget_3")
        self.notification_2 = QWidget()
        self.notification_2.setObjectName(u"notification_2")
        self.verticalLayout_17 = QVBoxLayout(self.notification_2)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.label_14 = QLabel(self.notification_2)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_14)

        self.stackedWidget_3.addWidget(self.notification_2)
        self.more_2 = QWidget()
        self.more_2.setObjectName(u"more_2")
        self.verticalLayout_18 = QVBoxLayout(self.more_2)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.label_15 = QLabel(self.more_2)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_18.addWidget(self.label_15)

        self.stackedWidget_3.addWidget(self.more_2)
        self.profile = QWidget()
        self.profile.setObjectName(u"profile")
        self.verticalLayout_19 = QVBoxLayout(self.profile)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.label_16 = QLabel(self.profile)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_19.addWidget(self.label_16)

        self.stackedWidget_3.addWidget(self.profile)

        self.verticalLayout_16.addWidget(self.stackedWidget_3)


        self.horizontalLayout_10.addWidget(self.right)


        self.verticalLayout_10.addWidget(self.maincontent)

        self.footer = QWidget(self.main)
        self.footer.setObjectName(u"footer")
        self.horizontalLayout_4 = QHBoxLayout(self.footer)
        self.horizontalLayout_4.setSpacing(5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.frame_2 = QFrame(self.footer)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_7 = QLabel(self.frame_2)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_5.addWidget(self.label_7)

        self.progressBar = QProgressBar(self.frame_2)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)

        self.horizontalLayout_5.addWidget(self.progressBar)


        self.horizontalLayout_4.addWidget(self.frame_2, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.size = QFrame(self.footer)
        self.size.setObjectName(u"size")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(15)
        sizePolicy2.setVerticalStretch(15)
        sizePolicy2.setHeightForWidth(self.size.sizePolicy().hasHeightForWidth())
        self.size.setSizePolicy(sizePolicy2)
        self.size.setMinimumSize(QSize(15, 15))
        self.size.setFrameShape(QFrame.Shape.StyledPanel)
        self.size.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_4.addWidget(self.size, 0, Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignBottom)


        self.verticalLayout_10.addWidget(self.footer, 0, Qt.AlignmentFlag.AlignBottom)


        self.horizontalLayout.addWidget(self.main)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(1)
        self.stackedWidget_2.setCurrentIndex(3)
        self.stackedWidget_3.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton.setText("")
        self.Home.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.Data.setText(QCoreApplication.translate("MainWindow", u"Data", None))
        self.Reborts.setText(QCoreApplication.translate("MainWindow", u"Reborts", None))
        self.Graphs.setText(QCoreApplication.translate("MainWindow", u"Graphs", None))
        self.Setting.setText(QCoreApplication.translate("MainWindow", u"Setting", None))
        self.Information.setText(QCoreApplication.translate("MainWindow", u"Information", None))
        self.Help.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Center Menu", None))
        self.CloseLeftSideBar.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Setting", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Themes", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Information", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Axiora", None))
        self.notification.setText("")
        self.more.setText("")
        self.persone.setText("")
        self.label_8.setText("")
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Search", None))
        self.pushButton_10.setText(QCoreApplication.translate("MainWindow", u"Ctrl+K", None))
        self.minimize.setText("")
        self.restore.setText("")
        self.close.setText("")
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Data", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Rebort", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Graphs", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Right Menu", None))
        self.CloseRightSideBar.setText("")
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Notifications", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"More", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Profile", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Progress", None))
    # retranslateUi

