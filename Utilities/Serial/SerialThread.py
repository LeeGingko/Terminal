# -*- coding: utf-8 -*-
# 导入serial相关模块
import serial
import serial.tools.list_ports
# 默认导入
from PyQt5.QtCore import QMutex, QThread, QWaitCondition, pyqtSignal

class PrivateSerialThread(QThread):
    recvSignal = pyqtSignal(bytes)

    def __init__(self):
        super(PrivateSerialThread, self).__init__()
        self.usingSerial = serial.Serial()
        self.buffer = bytes()
        self.isPause = False
              
    def  __del__(self):
        if self.usingSerial.isOpen:
            self.usingSerial.close()

    def pause(self):
        self.isPause = True

    def resume(self):
        self.isPause = False

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
            if self.isPause == False:
                self.msleep(1)
                self.data = b''
                tmp = ''
                if self.usingSerial.isOpen():
                    try:
                        self.num = self.usingSerial.inWaiting()
                        if self.num == 0: # 无数据
                            continue
                        else:
                            self.msleep(1)
                            self.num = self.usingSerial.inWaiting()
                            # print("@SerialRecv Leng:" + str(self.num)) # 输出收到的字节数
                            self.data = self.usingSerial.read(self.num)
                            tmp = self.data.decode("utf-8")
                            print("@SerialRecv Data:" + tmp) # 输出收到的数据
                            if tmp[0] == "U": # 数据帧头
                                if (tmp[self.num - 2] != "\r") and (tmp[self.num - 1] != "\n"): # 部分数据帧
                                    self.buffer = self.data
                                    # print("@Seg1:" + self.buffer.decode("utf-8"))
                                    continue
                                elif (tmp[self.num - 2] == "\r") and (tmp[self.num - 1] == "\n"):
                                    self.buffer = self.data
                                    self.recvSignal.emit(self.buffer)
                            # elif (tmp[0] != "U") and (tmp[0] != "R") and (tmp[self.num - 2 : self.num] == "\r\n"): 
                            elif (tmp[0] != "U") and (tmp[0] != "G") and (tmp[self.num - 2] == "\r") and (tmp[self.num - 1] == "\n"): 
                                self.buffer = self.buffer + self.data
                                self.recvSignal.emit(self.buffer)
                                print("@SegAll:" + self.buffer.decode("utf-8"))
                                self.buffer.clear()
                            elif (tmp[0] == "G") and (tmp[self.num - 2] == "\r") and (tmp[self.num - 1] == "\n"):
                                self.recvSignal.emit(self.data)
                            else:
                                self.usingSerial.flushInput()
                    except:
                        pass
                else:
                    pass
            else:
                self.msleep(1)