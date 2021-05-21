# -*- coding: utf-8 -*-
import time

from PyQt5.QtCore import QThread, pyqtSignal

class LocalTimeThread(QThread):
    secondSignal = pyqtSignal(str)

    def __init__(self):
        super(LocalTimeThread, self).__init__()
        self.timeStamp = ""

    def  __del__(self):
        # self.secondSignal.__del__()
        # self.wait()
        # self.quit()
        pass
        
    def run(self):
        dayOfWeek = time.localtime().tm_wday
        weekday = ""
        if dayOfWeek == 0:
            weekday =  "星期一"
        elif dayOfWeek == 1:
            weekday = "星期二"
        elif dayOfWeek == 2:
            weekday = "星期三"
        elif dayOfWeek == 3:
            weekday = "星期四"
        elif dayOfWeek == 4:
            weekday = "星期五"
        elif dayOfWeek == 5:
            weekday = "星期六"
        elif dayOfWeek == 6:
            weekday = "星期天"
        while True:
            AMPM = str((time.strftime("%p"), time.localtime()[0])[0])
            if AMPM[0:2] == "AM":
                self.timeStamp = time.strftime("%Y年%m月%d日 上午 %H:%M:%S  ", time.localtime())
            elif AMPM[0:2] == "PM": # PM
                self.timeStamp = time.strftime("%Y年%m月%d日 下午 %H:%M:%S  ", time.localtime())
            self.secondSignal.emit(self.timeStamp + weekday)
            self.sleep(1)
