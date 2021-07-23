# -*- coding: utf-8 -*-
# 导入日期时间模块
import datetime as dt
# 导入os
import os
# 导入time相关模块
import time

# 默认导入
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox

# 导入协议通信界面
from Ui_FTPUtil import Ui_FTPSetting


class FTPStationlWin(QtWidgets.QDialog, Ui_FTPSetting):
    ftpAppendSignal = pyqtSignal(str)

    def __init__(self):
        super(FTPStationlWin, self).__init__()  # 继承父类的所有属性
        self.initUi()

    def initUi(self):
        self.setupUi(self)
        # 设置窗口居中显示
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()
        self.Wsize = self.geometry()
        centerX = int((self.width - self.Wsize.width()) / 2)
        centerY = int((self.height - self.Wsize.height()) / 2 - 20)
        self.move(centerX, centerY)
        self.setWindowTitle("Protocol")
        iconPath = os.path.join(os.getcwd(),'./resources/icons/IDDD.ico')
        self.setWindowIcon(QIcon(iconPath))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 阻塞父类窗口不能点击
        # self.setWindowModality(Qt.ApplicationModal)
