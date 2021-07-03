# -*- coding: utf-8 -*-
# 导入serial相关模块
import serial
import serial.tools.list_ports
# 默认导入
from PyQt5.QtCore import QThread, pyqtSignal

class PrivateSerialThread(QThread):
    recvSignal = pyqtSignal(bytes)

    def __init__(self):
        super(PrivateSerialThread, self).__init__()
        self.usingSerial = serial.Serial()
        self.recvComEvent = QThread.event
        
    def  __del__(self):
        if self.usingSerial.isOpen:
            self.usingSerial.close()

    def initPort(self, port):
        self.usingSerial.port = port
        self.usingSerial.baudrate = 115200
        self.usingSerial.bytesize = serial.EIGHTBITS
        self.usingSerial.stopbits = serial.STOPBITS_ONE
        self.usingSerial.parity = serial.PARITY_NONE
        self.usingSerial.timeout = None
        self.usingSerial.xonxoff = False
        self.usingSerial.rtscts = False
        self.usingSerial.dsrdtr = False

    def run(self):
        while True:
            self.msleep(10)
            self.data = b''
            tmp = ''
            if self.usingSerial.isOpen():
                try:
                    self.num = self.usingSerial.inWaiting()
                    if self.num == 0: # 无数据
                        continue 
                    elif self.num > 0 and self.num <= 4: # 解决00\r\n这个bug
                        # self.usingSerial.flushInput()
                        self.usingSerial.read(self.num)
                    else:
                        self.msleep(10)
                        self.num = self.usingSerial.inWaiting()
                        if self.num >= 9: # 正常通信，至少都是9字节
                            # print("@PrivateSerialThread->run->" + str(self.num)) # 输出收到的字节数
                            self.data = self.usingSerial.read(self.num)
                            tmp = self.data.decode("utf-8")
                            print("@SerialRecv->" + tmp) 
                            if (tmp[0] == "U")  and (tmp[self.num - 2] == "\r") and (tmp[self.num - 1] == "\n"):
                                self.recvSignal.emit(self.data)
                        elif self.num == 6: # 工作模式改变
                            self.data = self.usingSerial.read(self.num)
                            tmp = self.data.decode("utf-8")
                            print("@SerialRecv->" + tmp) 
                            if (tmp[0] == "R")  and (tmp[self.num - 2] == "\r") and (tmp[self.num - 1] == "\n"):
                                self.recvSignal.emit(self.data)
                        else:
                            if tmp[0] == "R": # bug->诸如RX1015\r\n之类的
                                self.recvSignal.emit(self.data)
                            else:
                                self.usingSerial.flushInput()
                except:
                    pass
            else:
                pass