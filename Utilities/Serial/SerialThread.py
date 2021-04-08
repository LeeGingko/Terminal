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
        self.userSerial = serial.Serial()
        
    def  __del__(self):
        if self.userSerial.isOpen:
            self.userSerial.close()
        self.quit()
        self.wait()

    def initPort(self, port):
        self.userSerial.port = port
        self.userSerial.baudrate = 115200
        self.userSerial.bytesize = serial.EIGHTBITS
        self.userSerial.stopbits = serial.STOPBITS_ONE
        self.userSerial.parity = serial.PARITY_NONE
        self.userSerial.timeout = None
        self.userSerial.xonxoff = False
        self.userSerial.rtscts = False
        self.userSerial.dsrdtr = False

    def run(self):
        while True:
            self.msleep(10)
            self.data = b""
            tmp = ""
            if self.userSerial.isOpen():
                try:
                    self.num = self.userSerial.inWaiting()
                    if self.num == 0: # 无数据
                        continue 
                    elif self.num > 0 and self.num <= 4: # 解决00\r\n这个bug
                        self.userSerial.flushInput()
                    else:
                        self.msleep(10)
                        self.num = self.userSerial.inWaiting()
                        if self.num >= 9: # 正常接收，至少都是9字节
                            print("PersonalSerial->run->" + str(self.num)) # 输出收到的字节数
                            self.data = self.userSerial.read(self.num)
                            tmp = self.data.decode("utf-8")
                            print("@PersonalSerial->run->" + tmp) 
                            if (tmp[0] == "U")  and (tmp[self.num - 2] == "\r") and (tmp[self.num - 1] == "\n"):
                                self.recvSignal.emit(self.data)
                        elif self.num == 6: # 工作模式改变
                            self.data = self.userSerial.read(self.num)
                            tmp = self.data.decode("utf-8")
                            print("@PersonalSerial->run->" + tmp) 
                            if (tmp[0] == "R")  and (tmp[self.num - 2] == "\r") and (tmp[self.num - 1] == "\n"):
                                self.recvSignal.emit(self.data)
                except:
                    self.recvSignal.emit(bytes("接收数据失败", encoding="utf-8"))
            else:
                pass