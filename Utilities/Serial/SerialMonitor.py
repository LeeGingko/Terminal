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
        self.portList = []
        self.descriptionList = []

    def searchPorts(self):
        self.portList = serial.tools.list_ports.comports()
        self.portList.sort()
        if len(self.portList) >= 1:
            for p in self.portList:
                self.descriptionList.append(p.description)

    def run(self):
        # while True:
        #     self.msleep(100)
        #     list = serial.tools.list_ports.comports()
        #     list.sort()
        #     if len(list) >= 1:
        #         if len(list) != len(self.portList):
        #             self.portList = list.copy()
        #             self.descriptionList.clear()
        #             for p in list:
        #                 self.descriptionList.append(p.description)
        #             self.portChangeSignal.emit(self.descriptionList)
        #         else:
        #             pass
        pass
