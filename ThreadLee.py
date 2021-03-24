# -*- coding: utf-8 -*-
import time

from PyQt5.QtCore import QThread, pyqtSignal

class TimeThread(QThread):
    secondSignal = pyqtSignal(str)

    def __init__(self):
        super(TimeThread, self).__init__()
        self.timeStamp = ""

    def run(self):
        while True:
            APM = str((time.strftime("%p"),time.localtime()[0]))
            if APM[0:2] == "AM":
                self.timeStamp = time.strftime("%Y年%m月%d日\n上午 %H:%M:%S ", time.localtime())
            else:
                self.timeStamp = time.strftime("%Y年%m月%d日\n下午 %H:%M:%S ", time.localtime())
            dayOfWeek = time.localtime().tm_wday
            if dayOfWeek == 0:
                self.timeStamp = self.timeStamp + "星期一"
            elif dayOfWeek == 1:
                self.timeStamp = self.timeStamp + "星期二"
            elif dayOfWeek == 2:
                self.timeStamp = self.timeStamp + "星期三"
            elif dayOfWeek == 3:
                self.timeStamp = self.timeStamp + "星期四"
            elif dayOfWeek == 4:
                self.timeStamp = self.timeStamp + "星期五"
            elif dayOfWeek == 5:
                self.timeStamp = self.timeStamp + "星期六"
            elif dayOfWeek == 6:
                self.timeStamp = self.timeStamp + "星期天"
            self.secondSignal.emit(self.timeStamp)
            self.sleep(1)
