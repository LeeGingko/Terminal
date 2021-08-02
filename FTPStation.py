# -*- coding: utf-8 -*-
# 导入日期时间模块
import datetime as dt
import ftplib
# -*- coding: utf-8 -*-.
# 导入日志模块
import logging
# 导入os
import os
# 导入pickle模块
import pickle as pk
# 导入socket模块
import socket
# 导入time模块
import time
# 导入FTPLIB Client
from ftplib import FTP
from typing import overload

# 导入PING
from multiping import MultiPing, MultiPingSocketError
# 默认导入
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject, QRegularExpression, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QRegularExpressionValidator
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QLabel,
                             QMessageBox)

# 导入协议通信界面
from Ui_FTPUtil import Ui_FTPSetting
# 导入PYFTPDLIB类 Server
from Utilities.FTPD.ftpd import PrivateFTP
# 导入自定义工具
from Utilities.Tool.usual import Tools


class FTPStationlWin(QtWidgets.QWidget, Ui_FTPSetting):

    def __init__(self):
        super(FTPStationlWin, self).__init__()  # 继承父类的所有属性
        self.initUi()
        # 获取应用程序当前工作路径
        self.configFolder = os.path.join(os.getcwd(), 'configurations')
        self.ftpRecordFile = os.path.join(self.configFolder, 'ftpOperationRecord.txt')
        self.isThisPCAsServer = False
        self.userAttribute = { 'U1':None, 'U2':None, 'U3':None }
        self.createFTPOperationRecord()

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
        self.setWindowTitle("FTPUtil")
        iconPath = os.path.join(os.getcwd(),'./resources/icons/IDDD.ico')
        self.setWindowIcon(QIcon(iconPath))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowStaysOnTopHint)
        # 自定义工具实例化
        self.usualTools = Tools()
        # 服务IP填写规则
        serveripregv = QRegularExpressionValidator(self)
        serveripreg = QRegularExpression("\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b")
        serveripregv.setRegularExpression(serveripreg)
        self.le_ServerIP.setValidator(serveripregv)
        # 显示本机IP
        pc = socket.gethostname()
        self.ip = socket.gethostbyname(pc)
        self.lb_LocalIP.setText(self.ip)
        # 消息提示窗口初始化
        self.tb_Message.setFontFamily("微软雅黑")
        self.tb_Message.setFontPointSize(16)
        # 本机是否为服务器
        self.thisPCServerOrClient = None
        # self.btn_ThisPCAsServer.setStyleSheet("QPushButton{background-color: rgb(175, 203, 75)}")
        # self.btn_ThisPCAsServer.setStyleSheet("QPushButton{background-color: rgb(255, 0, 0)}")
        self.disableAllFunc()
        self.ftpThread = PrivateFTP()
        self.isServerStart = False
        self.isClientConnect = False
        self.myftp = FTP()
        self.myftp.set_debuglevel(2)
        self.myftp.encoding = 'gbk'

    def disableAllFunc(self):
        self.le_ServerIP.setEnabled(False)
        self.le_UserName.setEnabled(False)
        self.le_UserPasswd.setEnabled(False)
        self.btn_Connection.setEnabled(False)
        self.btn_PushFile.setEnabled(False)
        self.btn_PullFile.setEnabled(False)
        self.btn_MergeFile.setEnabled(False)

    def tbMessageAppend(self, str):
        ts = self.usualTools.getTimeStamp()
        self.tb_Message.append(ts + str)
        self.tb_Message.moveCursor(self.tb_Message.textCursor().End)  
     
    @QtCore.pyqtSlot()
    def on_btn_ThisPCAsServer_clicked(self):
        if self.thisPCServerOrClient == None:
            self.thisPCServerOrClient = True
            self.le_ServerIP.setEnabled(False)
            self.le_UserName.setEnabled(False)
            self.le_UserPasswd.setEnabled(False) 
            self.btn_ThisPCAsClient.setEnabled(False)
            self.btn_Connection.setEnabled(True)
            self.btn_Connection.setText('开启服务器')
            self.lb_ServiceType.setText('本机工作类型：服务器')
            self.tbMessageAppend('本机已作为服务器')

    @QtCore.pyqtSlot()
    def on_btn_ThisPCAsClient_clicked(self):
        if self.thisPCServerOrClient == None:
            self.thisPCServerOrClient = False
            self.le_ServerIP.setEnabled(True)
            self.le_UserName.setEnabled(True)
            self.le_UserPasswd.setEnabled(True)
            self.btn_ThisPCAsServer.setEnabled(False)          
            self.btn_Connection.setEnabled(True)
            self.btn_Connection.setText('连接服务器')
            self.lb_ServiceType.setText('本机工作类型：客户端')
            self.tbMessageAppend('本机已作为客户端')

    @QtCore.pyqtSlot()
    def on_btn_Connection_clicked(self):
        l = list()
        btnText = self.btn_Connection.text()
        if self.thisPCServerOrClient == True:
            if btnText == '开启服务器':
                self.btn_Connection.setText('关闭服务器')
                if self.isServerStart == False:
                    self.ftpThread.start()
                    self.isServerStart = True
                    self.btn_PushFile.setEnabled(True)
                    self.btn_PullFile.setEnabled(True)
                    self.btn_MergeFile.setEnabled(True)
                    self.tbMessageAppend('服务器已开启，服务器IP:' + self.ip)
            elif btnText == '关闭服务器':
                self.btn_Connection.setText('开启服务器')
                self.ftpThread.server.close_all() # 关闭服务器及其所有连接
                self.isServerStart = False
                self.btn_PushFile.setEnabled(False)
                self.btn_PullFile.setEnabled(False)
                self.btn_MergeFile.setEnabled(False)
                self.tbMessageAppend('服务器已关闭')
        elif self.thisPCServerOrClient == False: # 作为客户端
            a = 1 if self.le_ServerIP.text() != '' else 0
            b = 1 if self.le_UserName.text() != '' else 0
            c = 1 if self.le_UserPasswd.text() != '' else 0
            if btnText == '连接服务器':
                if (a + b + c) == 3:
                    l.clear()
                    if self.isClientConnect == False:
                        l.append(self.le_ServerIP.text())
                        try:
                            mp = MultiPing(l)
                            mp.send()
                            responses, no_responses = mp.receive(1)
                            if responses != {} and no_responses == []:
                                try:
                                    self.myftp.connect(self.le_ServerIP.text())
                                    self.isClientConnect = True
                                    self.btn_PushFile.setEnabled(True)
                                    self.btn_PullFile.setEnabled(True)
                                    self.btn_MergeFile.setEnabled(True)
                                    self.btn_Connection.setText('断开连接')
                                    self.tbMessageAppend('已连接到服务器:'+ self.myftp.host)
                                    welcome = self.myftp.getwelcome()
                                    if welcome.find('220 PYFTPDLIB 1.5.6 READY.'):
                                        self.tbMessageAppend('服务器已就绪')
                                except ftplib.error_perm:
                                    pass
                                except ftplib.error_perm:
                                    pass
                                except ftplib.error_proto:
                                    pass
                                except TimeoutError:
                                    self.tbMessageAppend('连接超时，请检查IP是否本机IP')
                                except ConnectionRefusedError:
                                    self.tbMessageAppend('目标计算机拒绝连接，检查服务器是否关闭')
                            elif responses == {} and no_responses != []:
                                self.tbMessageAppend('该IP服务器未启动，或该IP无法连通！')
                        except MultiPingSocketError:
                            self.tbMessageAppend('IP格式错误，请检查输入IP')
                elif (a + b + c) < 3:
                    QMessageBox.warning(self, "连接服务器", "有空白输入，请输入完整登录信息", QMessageBox.Yes)
            elif btnText == '断开连接':
                self.isClientConnect = False
                self.myftp.quit()
                self.btn_PushFile.setEnabled(False)
                self.btn_PullFile.setEnabled(False)
                self.btn_MergeFile.setEnabled(True)
                self.tbMessageAppend('已和服务器:' + self.myftp.host + '断开连接')
                self.btn_Connection.setText('连接服务器')

    @QtCore.pyqtSlot()
    def on_btn_ScanFile_clicked(self):
        pass

    @QtCore.pyqtSlot()
    def on_btn_PushFile_clicked(self):
        pass

    @QtCore.pyqtSlot()
    def on_btn_PullFile_clicked(self):
        pass

    @QtCore.pyqtSlot()
    def on_btn_MergeFile_clicked(self):
        pass

    @QtCore.pyqtSlot()
    def on_btn_ShowFile_clicked(self):
        pass

    def createFTPOperationRecord(self):
        if not os.path.isfile(self.ftpRecordFile):
            self.loadFTPOperationRecord()
        else:
            try:
                with open(self.ftpRecordFile, encoding="utf-8", mode="w") as frf:
                    self.saved_info = (self.isThisPCAsServer, self.userAttribute)
                    frf.write(self.saved_info)
            except:
                pass

    def loadFTPOperationRecord(self):
        try:
            with open(self.ftpRecordFile, "rb") as ofrf:
                lfor = pk.load(ofrf) # 将二进制文件对象转换成Python对象
            self.isThisPCAsServer = lfor[0]
            self.userAttribute = lfor[1]
        except:
            pass
    
    def saveFTPOperationRecord(self):
        self.saved_info = (self.isThisPCAsServer, self.userAttribute)
        with open(self.ftpRecordFile, "wb") as frf:
            pk.dump(self.saved_info, frf) # 用dump函数将Python对象转成二进制对象文件
