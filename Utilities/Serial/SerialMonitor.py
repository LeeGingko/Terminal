# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
# 导入serial相关模块
import serial
import serial.tools.list_ports
# 默认导入
from PyQt5.QtCore import QThread, pyqtSignal

class PrivateSerialMonitor(QThread):
    portChangeSignal = pyqtSignal(list)

    def __init__(self):
        super(PrivateSerialMonitor, self).__init__()
        self.list = []
        self.portList = []
        self.descriptionList = []

    def searchPorts(self):
        self.portList = serial.tools.list_ports.comports()
        self.portList.sort()
        if len(self.portList) >= 1:
            for p in self.portList:
                self.descriptionList.append(p.description)

    def run(self):
        while True:
            self.msleep(1000)
            self.list.clear()
            self.list = serial.tools.list_ports.comports()
            self.list.sort()
            # print("tlist：" + str(len(self.list)))
            # print("plist：" + str(len(self.portList)))
            if len(self.list) == 0 and len(self.portList) == 1:
                self.portList.clear()
                self.portChangeSignal.emit(['NOCOM'])
            elif len(self.list) >= 1:
                if len(self.list) != len(self.portList):
                    self.portList.clear()
                    self.descriptionList.clear()
                    self.portList = self.list.copy()
                    for p in self.list:
                        self.descriptionList.append(p.description)
                    self.portChangeSignal.emit(self.descriptionList)
                else:
                    pass
            else:
                self.portList.clear()