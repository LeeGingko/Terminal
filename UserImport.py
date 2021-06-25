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
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRegularExpression, QSize, Qt, QThread, QTimer
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPixmap, QRegularExpressionValidator, QStandardItem, QStandardItemModel
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import QAbstractItemView, QAction, QApplication, QFileDialog, QHeaderView, QLabel, QMenu, QMessageBox, QPushButton, QStatusBar

# getset全局变量
import GetSetObj
# # 导入黑色主题
# import qdarkstyle
# 全局变量
import GlobalVariable
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
# 引入串口封装类
from Utilities.Serial.SerialMonitor import PrivateSerialMonitor  # 串口端口监测
from Utilities.Serial.SerialThread import PrivateSerialThread  # 串口数据传输
# 导入自定义线程类
from Utilities.Tool.LocalTimeThread import LocalTimeThread
# 导入自定义工具
from Utilities.Tool.usual import Tools
# 导入表格视图委托
from Utilities.ViewDelegation.TableViewDelegate import PrivateTableViewDelegate
