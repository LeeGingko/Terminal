# -*- coding: utf-8 -*-
# 导入日期时间模块
import datetime as dt

# 导入serial相关模块
import serial
import serial.tools.list_ports
# 默认导入
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *


class PersonalSerial(QThread):
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

    def openPort(self):
        # try:
        self.serial.open()
            # if self.serial.isOpen():
                # return True
        # except:
            # return False

    def closePort(self):
        self.serial.close()

    def portIsOpen(self):
        return self.serial.isOpen()

    def portFlush(self):
        self.serial.flush()

    def portFlushOutput(self):
        self.serial.flushOutput()

    def portFlushInput(self):
        self.serial.flushInput()

    def portWrite(self, data):
        self.serial.write(data)

    def run(self):
        pass
