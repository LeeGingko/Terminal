# -*- coding: utf-8 -*-
# 导入serial相关模块
import serial
import serial.tools.list_ports
# 默认导入
from PyQt5.QtCore import QThread, pyqtSignal

class PrivateSerialMonitor(QThread):
    portChangeSignal = pyqtSignal(list, str, set)

    def __init__(self):
        super(PrivateSerialMonitor, self).__init__()
        self.tmpList = []
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
            self.tmpList.clear()
            self.tmpList = serial.tools.list_ports.comports()
            self.tmpList.sort() 
            if len(self.tmpList) == 0 and len(self.portList) == 1:
                self.portChangeSignal.emit(['NOCOM'], '', set(self.portList))
                self.portList.clear()
            elif len(self.tmpList) >= 1:
                if len(self.tmpList) != len(self.portList):
                    action = ''
                    # print("tlist：" + str(len(self.tmpList)))
                    # print("plist：" + str(len(self.portList)))
                    if len(self.tmpList) > len(self.portList):
                        diffset = set(self.tmpList).difference(set(self.portList))
                        action = 'UPON'
                    else:
                        diffset = set(self.portList).difference(set(self.tmpList))
                        action = 'DOWN'
                    self.portList.clear()
                    self.descriptionList.clear()
                    self.portList = self.tmpList.copy()
                    for p in self.tmpList:
                        self.descriptionList.append(p.description)
                    self.portChangeSignal.emit(self.descriptionList, action, diffset)
                else:
                    pass
            else:
                self.portList.clear()