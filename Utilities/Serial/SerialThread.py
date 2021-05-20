# -*- coding: utf-8 -*-
# 导入serial相关模块
import serial
import serial.tools.list_ports
# 默认导入
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication

class PrivateSerialThread(QThread):
    recvSignal = pyqtSignal(bytes)

    def __init__(self):
        super(PrivateSerialThread, self).__init__()
        self.inUseSerial = serial.Serial()
        self.recvComEvent = QThread.event
        
    def  __del__(self):
        if self.inUseSerial.isOpen:
            self.inUseSerial.close()

    def initPort(self, port):
        self.inUseSerial.port = port
        self.inUseSerial.baudrate = 115200
        self.inUseSerial.bytesize = serial.EIGHTBITS
        self.inUseSerial.stopbits = serial.STOPBITS_ONE
        self.inUseSerial.parity = serial.PARITY_NONE
        self.inUseSerial.timeout = None
        self.inUseSerial.xonxoff = False
        self.inUseSerial.rtscts = False
        self.inUseSerial.dsrdtr = False

    def run(self):
        while True:
            self.msleep(5)
            self.data = b''
            tmp = ''
            if self.inUseSerial.isOpen():
                try:
                    self.num = self.inUseSerial.inWaiting()
                    if self.num == 0: # 无数据
                        continue 
                    elif self.num > 0 and self.num <= 4: # 解决00\r\n这个bug
                        # self.inUseSerial.flushInput()
                        self.inUseSerial.read(self.num)
                    else:
                        self.msleep(5)
                        self.num = self.inUseSerial.inWaiting()
                        if self.num >= 9: # 正常接收，至少都是9字节
                            # print("@PrivateSerialThread->run->" + str(self.num)) # 输出收到的字节数
                            self.data = self.inUseSerial.read(self.num)
                            tmp = self.data.decode("utf-8")
                            print("@SerialRecv->" + tmp) 
                            if (tmp[0] == "U")  and (tmp[self.num - 2] == "\r") and (tmp[self.num - 1] == "\n"):
                                self.recvSignal.emit(self.data)
                        elif self.num == 6: # 工作模式改变
                            self.data = self.inUseSerial.read(self.num)
                            tmp = self.data.decode("utf-8")
                            print("@SerialRecv->" + tmp) 
                            if (tmp[0] == "R")  and (tmp[self.num - 2] == "\r") and (tmp[self.num - 1] == "\n"):
                                self.recvSignal.emit(self.data)
                        else:
                            if tmp[0] == "R": # bug->诸如RX1015\r\n之类的
                                self.recvSignal.emit(self.data)
                except:
                    # self.recvSignal.emit(bytes("接收数据失败", encoding = "utf-8"))
                    pass
            else:
                pass