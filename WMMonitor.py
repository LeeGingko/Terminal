# -*- coding: utf-8 -*-
import time
# 导入日期时间模块
import datetime as dt

# 导入serial相关模块
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *

class WMThread(QThread):
    wmChangedSignal = pyqtSignal(str)
    
    def __init__(self, portInstance):
        super(WMThread, self).__init__()
        self.portInstance = portInstance
        self.wmIsChanged = False
        self.dt = dt

    def __del__(self):
        self.quit()
        self.wait()

    def run(self):
        while True:
            self.sleep(1)
            startTiming = dt.datetime.now()
            # self.wmlock.acquire()
            # try:
                
            #     self.num = self.portInstance.inWaiting()
            #     # print("workModeCheck num:" + str(self.num)) # 输出收到的字节数
            #     if self.num > 0:
            #         time.sleep(0.01)
            #         self.num = self.serialInstance.inWaiting()
            #     if self.num > 0:
            #         self.data = self.serialInstance.read(self.num)
            #         self.wmChangedSignal.emit(self.data)
            #     elif self.num == 0:
            #         endTiming = dt.datetime.now()
            #         if (endTiming - startTiming).seconds >= 2:
            #             QApplication.processEvents()
            #             print("WMThread" + "@接收数据超时")
            #         else:
            #             continue
            #     else:
            #         continue
            # except:
                # continue
