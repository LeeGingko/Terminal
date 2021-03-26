# -*- coding: utf-8 -*-
# 时间
import time
# 导入日期时间模块
import datetime as dt

# 导入serial相关模块
import serial
import serial.tools.list_ports
# 默认导入
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication

class PersonalSerial(QThread):
    recvSignal = pyqtSignal(bytes)

    def __init__(self):
        super(PersonalSerial, self).__init__()
        self.serial = serial.Serial()
        
    def initPort(self, port):
        self.serial.port = port
        self.serial.baudrate = 115200
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.parity = serial.PARITY_NONE
        self.serial.timeout = None
        self.serial.xonxoff = False
        self.serial.rtscts = False
        self.serial.dsrdtr = False

    def run(self):
        # startTiming = dt.datetime.now()
        # while True:
        #     QApplication.processEvents()
        #     try:
        #         self.num = self.serial.inWaiting()
        #         # print(self.num) # 输出收到的字节数
        #         if self.num > 0:
        #             time.sleep(0.01)
        #             self.num = self.serial.inWaiting()
        #         if self.num >= 28:
        #             self.data = self.serial.read(self.num)
        #             self.recvSignal.emit(self.data)
        #         elif self.num == 0:
        #             endTiming = dt.datetime.now()
        #             if (endTiming - startTiming).seconds >= 6:
        #                 self.textBrowser.append(self.usualTools.getTimeStamp()+ "@接收数据超时")
        #                 break
        #             else:
        #                 continue
        #     except:
        #         continue
        # if self.num >= 28:
        #     self.data = self.serial.read(self.num)

        pass
