from main_page import *
from FunctionsAB import GuiFunctions

class Application(QApplication):
    def __init__(self) -> None:
        super().__init__([])

        self.win = AnalyticsDashoard()
        # self.win = QColorDialog()
        self.win.show()

        self.setStyleSheet(STYLE_QSS)

        self.app_functions = GuiFunctions(self.win)

app = Application()

app.exec()