# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# 导入串口调试窗口
from Ui_SerialUtil import Ui_dialog_SerialSettings

# 导入serial相关模块
import serial
import serial.tools.list_ports
from PyQt5.QtSerialPort import QSerialPortInfo
from serial.win32 import DTR_CONTROL_DISABLE


class serialUtilWin(QtWidgets.QDialog, Ui_dialog_SerialSettings):
    def __init__(self):
        super().__init__()
        self.setupUi(self)