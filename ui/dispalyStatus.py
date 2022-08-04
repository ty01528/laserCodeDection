import datetime
import time

from PyQt5 import QtCore, QtWidgets


class disTime(QtCore.QThread):
    def __init__(self, localTimeLabel=QtWidgets.QLabel, parent=None):
        super(disTime, self).__init__(parent)
        self.localTimeLabel = localTimeLabel

    def run(self):
        while (True):
            now_time = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
            self.localTimeLabel.setText(now_time)
            time.sleep(1)


# class disCamStatus(QtCore.QThread):
#     def __init__(self, camStatuLabel=QtWidgets.QLabel, parent=None):
#         super(disCamStatus, self).__init__(parent)
#         self.camStatuLabel = camStatuLabel
#         self.greenCircle = "min-width: 16px; min-height: 16px;max-width:16px; max-height: 16px;border-radius: " \
#                            "8px;  border:1px solid black;background:green "
#         self.redCircle = "min-width: 16px; min-height: 16px;max-width:16px; max-height: 16px;border-radius: 8px;  " \
#                          "border:1px solid black;background:red"
#
#     def run(self):
#         while (True):
#             self.camStatuLabel.setStyleSheet(self.m_green_SheetStyle)
#             time.sleep(1)
