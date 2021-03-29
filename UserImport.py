# -*- coding: utf-8 -*-
# 导入日期时间模块
import datetime as dt
# 导入os
import os
# 导入pickle模块
import pickle as pk
# 导入系统模块
import sys
# 导入time相关模块
import time

# 导入serial相关模块
import serial
import serial.tools.list_ports
# 默认导入
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import *

# 导入qrc资源
from resources import resources_rc
# 导入主窗口类
from Ui_Detector import Ui_MainWindow
# 导入功能枚举
from Utilities.Enum.FuncEnum import Func
# 导入状态枚举
from Utilities.Enum.StateEnum import State
# 导入自定义Excel操作类
from Utilities.Excel.OpenPyExcel import PersonalExcel
# 工作模式更新类
from Utilities.Monitor.WMMonitor import WMThread
# 引入串口封装类
from Utilities.Serial.SerialThread import PersonalSerial
# 导入自定义线程类
from Utilities.Time.LocalTimeThread import TimeThread
from Utilities.Time.OpNameInput import GetNameThread
# 导入自定义工具
from Utilities.Time.usual import Tools
