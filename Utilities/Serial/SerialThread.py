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
    recvSignal = pyqtSignal(str)

    def __init__(self):
        super(PersonalSerial, self).__init__()
        self.userSerial = serial.Serial()
        
    def  __del__(self):
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
            QApplication.processEvents()
            time.sleep(0.1)
            self.data = b""
            tmp = ""
            if self.userSerial.isOpen():
                try:
                    self.num = self.userSerial.inWaiting()
                    # print(self.num)
                    if self.num > 0 and self.num <= 4:
                        self.userSerial.flushInput()
                    elif self.num == 6:
                        time.sleep(0.01)
                        self.num = self.userSerial.inWaiting()
                        # print("PersonalSerial->run->" + str(self.num)) # 输出收到的字节数
                        if self.num == 6:
                            self.data = self.userSerial.read(self.num)
                            tmp = self.data.decode("utf-8")
                            print(self.data.decode("utf-8"))
                            if tmp[0] == "R" and tmp[4] == "\r" and tmp[5] == "\n":
                                self.recvSignal.emit(tmp[1:4])
                except:
                    pass