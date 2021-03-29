# -*- coding: utf-8 -*-
import time
# 导入日期时间模块
import datetime as dt

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal

class GetNameThread(QThread):
    inputNameSignal = pyqtSignal(str)
    inputSecondSignal = pyqtSignal(str)

    def __init__(self):
        super(GetNameThread, self).__init__()

    def run(self):
        cnt = 20
        while True:
            QApplication.processEvents()
            time.sleep(1)
            self.inputNameSignal.emit("sec")
            cnt -= 1
            if cnt == 0:
                self.inputNameSignal.emit("TimeOut")
