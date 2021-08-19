# -*- coding: utf-8 -*-
# 导入日期时间模块
import datetime as dt
# 导入FTPLIB模块
import ftplib
# 导入glob
import glob
# 导入os
import os
# 导入pickle模块
import pickle as pk
# 导入shutil模块
import shutil
# 导入socket模块
import socket
# 导入time模块
import time
# 导入FTPLIB Client
from ftplib import FTP, error_perm, error_proto, error_temp
from typing import Dict

# 导入PING
from multiping import MultiPing, MultiPingSocketError
# 默认导入
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QRegularExpression, Qt
from PyQt5.QtGui import (QFont, QIcon, QRegularExpressionValidator,
                         QStandardItem, QStandardItemModel)
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
                             QFileDialog, QHeaderView, QMenu, QMessageBox)

# 导入协议通信界面
from Ui_FTPUtil import Ui_FTPSetting
# 导入自定义Excel操作类
from Utilities.Excel.OpenPyxl import PrivateOpenPyxl
# 导入PYFTPDLIB类 Server
from Utilities.FTPD.ftpd import PrivateFTP
# 导入自定义工具
from Utilities.Tool.usual import Tools
# 导入表格视图委托
from Utilities.ViewDelegation.TableViewDelegate import PrivateTableViewDelegate


class FTPStationlWin(QtWidgets.QWidget, Ui_FTPSetting):

    def __init__(self):
        super(FTPStationlWin, self).__init__()  # 继承父类的所有属性
        self.initUi()
        self.createFTPOperationRecord()
        self.createDetRecordFile()

    def initUi(self):
        self.setupUi(self)
        # 获取应用程序当前工作路径
        self.configFolder = os.path.join(os.getcwd(), 'configurations')
        self.ftpRecordFile = os.path.join(self.configFolder, 'ftpOperationRecord.txt')
        self.detRecordFile = os.path.join(self.configFolder, 'detRecordFile.txt')
        # 设置窗口居中显示
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()
        self.Wsize = self.geometry()
        centerX = int((self.width - self.Wsize.width()) / 2)
        centerY = int((self.height - self.Wsize.height()) / 2 - 35)
        self.move(centerX, centerY)
        self.setWindowTitle("FTPUtil")
        iconPath = os.path.join(os.getcwd(),'./resources/icons/IDDD.ico')
        self.setWindowIcon(QIcon(iconPath))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
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
        self.pcAsServerOrClient = None
        # self.btn_ThisPCAsServer.setStyleSheet("QPushButton{color: rgb(0, 170, 255)}")
        self.disableAllFunc()
        self.ftpThread = PrivateFTP()
        self.isServerStart = False
        self.isClientConnect = False
        self.myftp = FTP()
        self.myftp.set_debuglevel(2)
        self.myftp.encoding = 'gbk'
        #*------------------------------- 表格显示控件之模型、委托、视图初始化 MVC--------------------------------*#
        # 1 表格模型初始化
        self.tableViewModel = QStandardItemModel(0, 3, self)
        self.tableviewRowIndex = 0 # 表格视图写入数据行索引
        self.tableHeadline = [
            "名称",       "大小",     "修改时间", 
            "检测人员",  "所属类型",   "操作状态"]
        self.tableViewModel.setHorizontalHeaderLabels(self.tableHeadline) # 设置表头
        # 2 表格委托初始化
        self.tableViewDelegate = PrivateTableViewDelegate()    
        # 3 表格视图初始化
        self.tv_FileInfo.setModel(self.tableViewModel)
        self.tv_FileInfo.horizontalHeader().setStretchLastSection(True)
        self.tv_FileInfo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tv_FileInfo.setItemDelegate(self.tableViewDelegate)
        self.tv_FileInfo.horizontalHeader().setFont(QFont("幼圆", 12, QFont.Light))
        # self.tv_FileInfo.setSelectionBehavior(QAbstractItemDelegate.SelectRows)
        self.tv_FileInfo.verticalHeader().hide()
        self.tv_FileInfo.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tv_FileInfo.setEditTriggers (QAbstractItemView.NoEditTriggers)
        # 3.1 表格视图上下文菜单
        self.tvMenu = QMenu(self.tv_FileInfo)
        self.tv_FileInfo.customContextMenuRequested.connect(self.tvCustomContextMenuRequested)
        #*------------------------------- 表格显示控件之模型、委托、视图初始化 MVC--------------------------------*#
        self.detFileInfo = {}
        self.isThisPCAsServer = False
        # 检测数据Excel文件初始化
        self.excel = PrivateOpenPyxl() # 实例化Excel对象
        self.excel = PrivateOpenPyxl() # 实例化Excel对象
        self.xlsxFiles = []         
        self.detFileList = []       # 检测文件           
        self.detIdList = []         # 检测文件中的所有ID       
        self.detTimeList = []       # ID对应的检测时间         
        self.detFileIdTimeList = [] # 综合信息List
        self.detFileIdTimeDict = {} # 综合信息Dict
        self.dupIdSet = set()       

    def tvUpLoad(self):
        self.tbMessageAppend('开始上传')

    def tvDownLoad(self):
        self.tbMessageAppend('开始下载')

    def tvCustomContextMenuRequested(self, p):
        self.tvIndex = self.tv_FileInfo.selectionModel().selectedRows()
        self.tvRowList = []
        for i in self.tvIndex:
            self.tvRowList.append(i.row())
        self.tvRowList.sort(key=int, reverse=True)
        self.tvMenu.exec_(self.tv_FileInfo.mapToGlobal(p))

    def tbMessageAppend(self, str):
        ts = self.usualTools.getTimeStamp()
        self.tb_Message.append(ts + str)
        self.tb_Message.moveCursor(self.tb_Message.textCursor().End)  

    def disableAllFunc(self):
        self.le_ServerIP.setEnabled(False)
        self.le_UserName.setEnabled(False)
        self.le_UserPasswd.setEnabled(False)
        self.btn_Connection.setEnabled(False)
        self.btn_ScanLocalFile.setEnabled(False)
        self.btn_ScanRemoteFile.setEnabled(False)
        self.btn_PushFile.setEnabled(False)
        self.btn_PullFile.setEnabled(False)
        self.btn_MergeFile.setEnabled(False)
     
    @QtCore.pyqtSlot()
    def on_btn_ThisPCAsServer_clicked(self):
        if self.pcAsServerOrClient == None:
            self.pcAsServerOrClient = True
            self.le_ServerIP.setEnabled(False)
            self.le_UserName.setEnabled(False)
            self.le_UserPasswd.setEnabled(False) 
            self.btn_ThisPCAsClient.setEnabled(False)
            self.btn_Connection.setEnabled(True)
            self.btn_Connection.setText('开启服务器')
            self.lb_ServiceType.setText('本机工作类型')
            self.btn_ThisPCAsServer.setStyleSheet("QPushButton{color: rgb(0, 170, 255)}")
            self.tbMessageAppend('本机已作为服务器')
            # 服务器按键布局
            self.btn_ScanLocalFile.move(360, 10)
            self.btn_MergeFile.move(360, 80)
            self.line_Right.move(354, 153)
            self.btn_ScanRemoteFile.move(360, 160)
            self.btn_PushFile.move(360, 230)
            self.btn_ScanLocalFile.setEnabled(True)
            self.btn_MergeFile.setEnabled(True)            
            self.btn_PullFile.move(360, 300)
            # 视图右键动作
            self.upLoad = QAction()
            self.upLoad.setText('上传本地汇总文件')
            self.upLoad.triggered.connect(self.tvUpLoad)
            self.tvMenu.addAction(self.upLoad)


    @QtCore.pyqtSlot()
    def on_btn_ThisPCAsClient_clicked(self):
        if self.pcAsServerOrClient == None:
            self.pcAsServerOrClient = False
            self.le_ServerIP.setEnabled(True)
            self.le_UserName.setEnabled(True)
            self.le_UserPasswd.setEnabled(True)
            self.btn_ThisPCAsServer.setEnabled(False)          
            self.btn_Connection.setEnabled(True)
            self.btn_Connection.setText('连接服务器')
            self.lb_ServiceType.setText('本机工作类型')
            self.le_ServerIP.setFocus()
            self.btn_ThisPCAsClient.setStyleSheet("QPushButton{color: rgb(0, 170, 255)}")
            self.tbMessageAppend('本机已作为客户端')
            # 客户端按键布局
            self.btn_ScanLocalFile.move(360, 10)
            self.btn_ScanRemoteFile.move(360, 80)
            self.btn_PushFile.move(360, 150)
            self.btn_PullFile.move(360, 220)
            self.line_Right.move(354, 293)
            self.btn_MergeFile.move(360, 300)
            # 视图右键动作
            self.downLoad = QAction()
            self.downLoad.setText('下载选中远端文件')
            self.downLoad.triggered.connect(self.tvDownLoad)
            self.tvMenu.addAction(self.downLoad)

    @QtCore.pyqtSlot()
    def on_btn_Connection_clicked(self):
        l = list()
        self.btn_Connection.setEnabled(False)
        btnText = self.btn_Connection.text()
        if self.pcAsServerOrClient == True: # 作为服务器
            if btnText == '开启服务器':
                self.btn_Connection.setText('关闭服务器')
                if self.isServerStart == False:
                    self.ftpThread.start()
                    self.isServerStart = True
                    self.btn_ScanLocalFile.setEnabled(True)
                    self.btn_MergeFile.setEnabled(True)
                    self.tbMessageAppend('服务器已开启，服务器IP:' + self.ip)
            elif btnText == '关闭服务器':
                self.btn_Connection.setText('开启服务器')
                self.ftpThread.server.close_all() # 关闭服务器及其所有连接
                self.isServerStart = False
                self.btn_ScanLocalFile.setEnabled(False)
                self.btn_MergeFile.setEnabled(False)
                self.tbMessageAppend('服务器已关闭')
        elif self.pcAsServerOrClient == False: # 作为客户端
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
                                    res = self.myftp.connect(self.le_ServerIP.text())
                                    if res.find('220 PYFTPDLIB 1.5.6 READY.') != -1:
                                        self.tbMessageAppend('服务器已就绪')
                                        QApplication.processEvents()
                                        time.sleep(1)
                                        welcome = self.myftp.getwelcome()
                                        if welcome.find('220 PYFTPDLIB 1.5.6 READY.') != -1:
                                            self.tbMessageAppend('已连接到服务器:'+ self.myftp.host)
                                            self.isClientConnect = True
                                            self.btn_Connection.setText('断开连接')
                                            QApplication.processEvents()
                                            time.sleep(1)
                                            try:
                                                res = self.myftp.login(self.le_UserName.text(), self.le_UserPasswd.text())
                                                if res.find('Login Successful.') != -1:
                                                    self.tbMessageAppend('登录成功！')
                                                    self.myftp.set_pasv('PASV')
                                                    self.btn_ScanLocalFile.setEnabled(True)
                                                    self.btn_ScanRemoteFile.setEnabled(True)
                                                    self.btn_PushFile.setEnabled(True)
                                                    self.btn_PullFile.setEnabled(True)
                                                QApplication.processEvents()
                                            except error_perm:
                                                self.tbMessageAppend('登录失败，请检查用户名和密码并重新连接')
                                                QApplication.processEvents()
                                                time.sleep(1)
                                                res = self.myftp.quit()
                                                if res.find('221 Goodbye') != -1:
                                                    self.tbMessageAppend('已和服务器:' + self.myftp.host + '断开连接')
                                                    self.isClientConnect = False
                                                self.btn_Connection.setText('连接服务器')
                                                QApplication.processEvents()
                                except EOFError:
                                    self.tbMessageAppend('connection:EOFError')
                                except error_temp:
                                    self.tbMessageAppend('connection:error_temp')
                                except error_perm:
                                    self.tbMessageAppend('connection:error_perm')
                                except error_proto:
                                    self.tbMessageAppend('connection:error_proto')
                                except TimeoutError:
                                    self.tbMessageAppend('连接超时，请检查IP是否正确')
                                    QApplication.processEvents()
                                except ConnectionRefusedError:
                                    self.tbMessageAppend('目标计算机拒绝连接，检查服务器是否关闭')
                                    QApplication.processEvents()
                            elif responses == {} and no_responses != []:
                                self.tbMessageAppend('该IP服务器未启动，或该IP无法连通！')
                        except MultiPingSocketError:
                            self.tbMessageAppend('IP格式错误，请检查输入IP')
                            QApplication.processEvents()
                elif (a + b + c) < 3:
                    QMessageBox.warning(self, "连接服务器", "有空白输入，请输入完整登录信息", QMessageBox.Yes)
            elif btnText == '断开连接':
                self.isClientConnect = False
                try:
                    res = self.myftp.quit()
                    if res.find('221 Goodbye') != -1:
                        self.tbMessageAppend('已和服务器:' + self.myftp.host + '断开连接')
                except ConnectionResetError:
                    self.tbMessageAppend('服务器已关闭，连接已断开！')
                except ConnectionAbortedError:
                    self.tbMessageAppend('服务器已关闭，连接已断开！')
                self.btn_ScanLocalFile.setEnabled(False)
                self.btn_ScanRemoteFile.setEnabled(False)
                self.btn_PushFile.setEnabled(False)
                self.btn_PullFile.setEnabled(False)
                self.btn_Connection.setText('连接服务器')
        self.btn_Connection.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_btn_ScanLocalFile_clicked(self):
        self.tableviewRowIndex = 0
        self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())
        xlsxFiles = glob.glob('*.xlsx')
        for file in xlsxFiles:
            xlsxStat = os.stat(file)
            if '~$' not in file:
                if ('xlsx' in file) and ('年' in file) and ('月' in file) and ('日' in file):
                    #-------------------------------------------------------------文件名-------------------------------------------------------------#
                    filenameItem = QStandardItem(file)
                    filenameItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                    self.tableViewModel.setItem(self.tableviewRowIndex, 0, filenameItem)
                    #-------------------------------------------------------------文件大小-------------------------------------------------------------#
                    sizeOfFile = xlsxStat.st_size / 1024
                    sizeItem = QStandardItem('%.1f' % sizeOfFile)
                    sizeItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                    self.tableViewModel.setItem(self.tableviewRowIndex, 1, sizeItem)
                    #-------------------------------------------------------------修改时间-------------------------------------------------------------#
                    modifyTime = time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime(xlsxStat.st_mtime))
                    modifyItem = QStandardItem(modifyTime)
                    modifyItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                    self.tableViewModel.setItem(self.tableviewRowIndex, 2, modifyItem)
                    #-------------------------------------------------------------检测人员-------------------------------------------------------------#
                    l = len(file)
                    ulp = file.rfind('_', 0, l) # '_'：姓名前的下划线位置
                    detNameItem = QStandardItem(file[ulp + 1 : l - 5])
                    detNameItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                    self.tableViewModel.setItem(self.tableviewRowIndex, 3, detNameItem)
                    #-------------------------------------------------------------所属类型------------------------------------------------------------#
                    typeItem = QStandardItem('检测结果')
                    typeItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                    self.tableViewModel.setItem(self.tableviewRowIndex, 4, typeItem)
                    #-------------------------------------------------------------操作状态-------------------------------------------------------------#
                    opstaItem = QStandardItem('-')
                    opstaItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                    self.tableViewModel.setItem(self.tableviewRowIndex, 5, opstaItem)
                    self.tableviewRowIndex = self.tableviewRowIndex + 1
        self.tbMessageAppend('本地文件扫描完成')

    @QtCore.pyqtSlot()
    def on_btn_ScanRemoteFile_clicked(self):
        if self.pcAsServerOrClient == False: # 客户端才具有的功能
            try:
                self.tableviewRowIndex = 0
                self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())
                res = self.myftp.mlsd(path='.', facts=['modify', 'create', 'size'])
                if res != []:
                    for r in res:
                        if ('xlsx' in r[0]) and ('年' in r[0]) and ('月' in r[0]) and ('日' in r[0]):
                            #-------------------------------------------------------------文件名-------------------------------------------------------------#
                            filenameItem = QStandardItem(r[0])
                            filenameItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                            self.tableViewModel.setItem(self.tableviewRowIndex, 0, filenameItem)
                            #-------------------------------------------------------------文件大小-------------------------------------------------------------#
                            sizeOfFile = int(r[1]['size']) / 1024
                            sizeItem = QStandardItem('%.1f' % sizeOfFile)
                            sizeItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                            self.tableViewModel.setItem(self.tableviewRowIndex, 1, sizeItem)
                            #-------------------------------------------------------------创建时间-------------------------------------------------------------#
                            # hour = int(r[1]['create'][8:10])
                            # if hour >= 0 and hour <= 15:
                            #     hour = hour + 8
                            # elif hour >= 16 and hour <= 24:
                            #     hour = hour - 16
                            # createTime = str(r[1]['create'][0:4]) + '年' + str(r[1]['create'][4:6]) + '月' + str(r[1]['create'][6:8]) + '日 ' +\
                            #             '%02d' % hour + '时' + str(r[1]['create'][10:12]) + '分' + str(r[1]['modify'][12:14]) + '秒'
                            # createItem = QStandardItem(createTime)
                            # createItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                            # self.tableViewModel.setItem(self.tableviewRowIndex, 2, createItem)
                            #-------------------------------------------------------------修改时间-------------------------------------------------------------#
                            hour = int(r[1]['modify'][8:10])
                            if hour >= 0 and hour <= 15:
                                hour = hour + 8
                            elif hour >= 16 and hour <= 24:
                                hour = hour - 16
                            modifyTime = str(r[1]['modify'][0:4]) + '年' + str(r[1]['modify'][4:6]) + '月' + str(r[1]['modify'][6:8]) + '日 ' +\
                                        '%02d' % hour + '时' + str(r[1]['modify'][10:12]) + '分' + str(r[1]['modify'][12:14]) + '秒' 
                            modifyItem = QStandardItem(modifyTime)
                            modifyItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                            self.tableViewModel.setItem(self.tableviewRowIndex, 2, modifyItem)
                            # #-------------------------------------------------------------修改时间-------------------------------------------------------------#
                            # posItem = QStandardItem('远端')
                            # posItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                            # self.tableViewModel.setItem(self.tableviewRowIndex, 4, posItem)
                            self.tableviewRowIndex = self.tableviewRowIndex + 1
                    self.tbMessageAppend('服务器文件扫描完成')
                else:
                    self.tbMessageAppend('服务器暂无检测文件')
            except error_perm:
                self.tbMessageAppend('无此目录')

    @QtCore.pyqtSlot()
    def on_btn_PushFile_clicked(self):
        if self.pcAsServerOrClient == False:
            if self.tv_FileInfo.rowCount() != 0:
                try:
                    xlsxFiles = glob.glob('*.xlsx')
                    for xf in xlsxFiles:
                        if ('xlsx' in xf) and ('年' in xf) and ('月' in xf) and ('日' in xf):
                            with open(xf, 'rb') as fp:
                                self.tbMessageAppend('开始上传文件...\n>>' + xf)
                                try:
                                    uploadcmd = 'STOR ' + xf
                                    res = self.myftp.storbinary(uploadcmd, fp)
                                    if res.find('226 Transfer complete.') != -1:
                                        self.tbMessageAppend('上传完成')
                                except error_perm:
                                    self.tbMessageAppend('上传失败')
                except error_perm:
                    self.tbMessageAppend('无此文件')
                except ConnectionAbortedError:
                    self.tbMessageAppend('连接已断开，请重新连接')
                    self.btn_Connection.setText('连接服务器')
            else:
                self.tbMessageAppend('请进行文件扫描操作！')
            
    @QtCore.pyqtSlot()
    def on_btn_PullFile_clicked(self):
        if self.pcAsServerOrClient == False:
            if self.tv_FileInfo.rowCount() != 0:
                try:
                    res = self.myftp.mlsd(path='.', facts=['modify', 'create', 'size'])
                    for r in res:
                        if ('xlsx' in r[0]) and ('年' in r[0]) and ('月' in r[0]) and ('日' in r[0]):
                            with open(r[0], 'wb') as fp:
                                self.tbMessageAppend('开始下载文件...\n>>' + r[0])
                                try:
                                    downloadcmd = 'RETR ' + r[0]
                                    res = self.myftp.retrbinary(downloadcmd, fp.write)
                                    if res.find('226 Transfer complete.') != -1:
                                        self.tbMessageAppend('下载完成')
                                except error_perm:
                                    self.tbMessageAppend('下载失败')
                except error_perm:
                    self.tbMessageAppend('无此文件')
                except ConnectionAbortedError:
                    self.tbMessageAppend('连接已断开，请重新连接')
                    self.btn_Connection.setText('连接服务器')
            else:
                self.tbMessageAppend('请进行文件扫描操作！')
    
    @QtCore.pyqtSlot()
    def on_btn_MergeFile_clicked(self):
        self.xlsxFiles.clear()
        self.detFileList.clear()        # 检测文件
        self.detIdList.clear()          # 检测文件中的所有ID
        self.detTimeList.clear()        # ID对应的检测时间
        self.detFileIdTimeList.clear()  # 综合信息List
        self.detFileIdTimeDict.clear()  # 综合信息Dict
        # 列出文件
        self.tbMessageAppend('开始汇总...')
        time.sleep(1)
        QApplication.processEvents()
        self.xlsxFiles = glob.glob('*.xlsx')     
        # 检查是否有打开的文件
        if not self.checkXlsxState():
            time.sleep(1)
            self.tbMessageAppend('退出汇总')
            QApplication.processEvents()
            return
        # 获取文件和ID，列出文件中的所有ID及其对应检测记录的时间，生成对应的字典
        f = ''
        cnt = 0
        for file in self.xlsxFiles:
            # if '~$' not in file :
            if ('xlsx' in file) and ('年' in file) and ('月' in file) and ('日' in file):
                cnt = cnt + 1
                f = shutil.copy(file, 'f{0}.xlsx'.format(cnt))
                self.detFileList.append(f)
                self.excel.loadSheet(file)
                idRowGen = self.excel.ws.iter_rows(2, self.excel.ws.max_row, 1, self.excel.ws.max_column)
                self.detIdList.clear()          # 检测文件中的所有ID
                self.detTimeList.clear()        # ID对应的检测时间
                for rowid in idRowGen:
                    self.detIdList.append(rowid[6].value)
                    self.detTimeList.append(rowid[1].value)
                self.detFileIdTimeList.append([self.detIdList.copy(), self.detTimeList.copy()])
                self.excel.closeSheet()
        self.detFileIdTimeDict = dict.fromkeys(self.detFileList)
        for i in range(len(self.detFileList)):
            self.detFileIdTimeDict[self.detFileList[i]] = self.detFileIdTimeList[i]
        # 查找重复ID,对其检测结果按日期时间进行筛选
        l = len(self.detFileIdTimeDict)
        for index in range(l):
            if index != l-1:
                f1 = self.detFileList[index]
                for t in range(l-1, index, -1):
                    f2 = self.detFileList[t]
                    tmp = set(self.detFileIdTimeDict[f2][0]) & set(self.detFileIdTimeDict[f1][0])
                    print(tmp)
                    if tmp != set():
                        for id in tmp:
                            i = self.detFileIdTimeDict[f1][0].index(id)
                            j = self.detFileIdTimeDict[f2][0].index(id)
                            if self.detFileIdTimeDict[f1][1][i] < self.detFileIdTimeDict[f2][1][j]:
                                self.excel.loadSheet(f1)
                            else:
                                self.excel.loadSheet(f2)
                            row = self.excel.getRowIndexByID(id)
                            self.excel.deleteRow(row)
                            self.excel.saveSheet()
                            self.excel.closeSheet()
                    else:
                        pass
        # 根据特定的检测时间进行筛选，保留最新检测时间的记录

        # 汇总所有文件，生成汇总文件

        # 完成汇总
        time.sleep(1)
        self.tbMessageAppend('完成汇总')
        QApplication.processEvents()

    @QtCore.pyqtSlot()
    def on_btn_ShowFile_clicked(self):
        pass

    def createFTPOperationRecord(self): 
        if os.path.isfile(self.ftpRecordFile):
            pass
        else:
            try:
                with open(self.ftpRecordFile, encoding="gbk", mode="w") as frf:
                    self.saved_info = self.userAttribute
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

    def createDetRecordFile(self):
        if os.path.isfile(self.detRecordFile):
            pass
        else:
            try:
                with open(self.detRecordFile, encoding="gbk", mode="w") as frf:
                    # self.saved_info = (self.isThisPCAsServer, self.userAttribute)
                    # frf.write(self.saved_info)
                    pass
            except:
                pass

    def loadDetRecordFile(self):
        try:
            with open(self.detRecordFile, "rb") as ofrf:
                lfor = pk.load(ofrf) # 将二进制文件对象转换成Python对象
            self.isThisPCAsServer = lfor[0]
            self.userAttribute = lfor[1]
        except:
            pass
    
    def saveDetRecordFile(self):
        self.saved_info = (self.isThisPCAsServer, self.userAttribute)
        with open(self.detRecordFile, "wb") as frf:
            pk.dump(self.saved_info, frf) # 用dump函数将Python对象转成二进制对象文件

    def checkXlsxState(self):
        openFileList = []
        for file in self.xlsxFiles:
            if '~$' not in file:
                if self.usualTools.isExcelFileOpen(file) == True:
                    openFileList.append(file)
                else:
                    continue
        if len(openFileList) > 0:
            self.tb_Message.append('已被打开文件：')
            for f in openFileList:
                self.tb_Message.append(f)
            self.tb_Message.append('请先关闭上述文件！')
            self.tb_Message.moveCursor(self.tb_Message.textCursor().End)
            QApplication.processEvents()
            return False
        return True
