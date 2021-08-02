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
# 进程
from multiprocessing import Process

# 导入serial相关模块
import serial
import serial.tools.list_ports
import win32api
import win32gui
# 默认导入
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegularExpression, QSize, Qt, QThread, QTimer
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QPixmap,
                         QRegularExpressionValidator, QStandardItem,
                         QStandardItemModel)
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
                             QFileDialog, QHeaderView, QLabel, QMenu,
                             QMessageBox, QPushButton, QStatusBar)
# 输入法语言相关
from win32con import WM_INPUTLANGCHANGEREQUEST

# getset全局变量
import GetSetObj
# 导入FTP操作界面
from FTPStation import FTPStationlWin
# 导入全局变量类
from GlobalVariable import GlobalVar
# 导入协议窗口类
from Protocol import ProtocolWin
# 导入阈值设定窗口类
from Threshold import ThresholdWin
# 导入主窗口类
from Ui_Detector import Ui_MainWindow
# 导入功能枚举
from Utilities.Enum.FuncEnum import Func
# 导入状态枚举
from Utilities.Enum.StateEnum import State
# 导入自定义Excel操作类
from Utilities.Excel.OpenPyxl import PrivateOpenPyxl
# 导入FTP类
from Utilities.FTPD.ftpd import PrivateFTP
# 导入串口封装类
from Utilities.Serial.SerialMonitor import PrivateSerialMonitor  # 串口端口监测
from Utilities.Serial.SerialThread import PrivateSerialThread  # 串口数据传输
# 导入自定义线程类
from Utilities.Tool.LocalTimeThread import LocalTimeThread
# 导入自定义工具
from Utilities.Tool.usual import Tools
# 导入验证器
from Utilities.Validator.ValidatorBox import VLDR_INTFOLAT
# 导入表格视图委托
from Utilities.ViewDelegation.TableViewDelegate import PrivateTableViewDelegate