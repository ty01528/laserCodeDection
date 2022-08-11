import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from front.mainWindowFunc import uiFunction

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = uiFunction()
    ui.startUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
