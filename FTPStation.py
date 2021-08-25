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

# 导入pandas
import pandas as pd
# 导入PING
from multiping import MultiPing, MultiPingSocketError
# 默认导入
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QRegularExpression, Qt, pyqtSlot
from PyQt5.QtGui import (QFont, QIcon, QRegularExpressionValidator,
                         QStandardItem, QStandardItemModel)
from PyQt5.QtWidgets import (QAbstractItemDelegate, QAbstractItemView, QAction, QApplication,
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
        self.createDetRecordFile()

    def initUi(self):
        self.setupUi(self)
        # 获取应用程序当前工作路径
        self.configFolder = os.path.join(os.getcwd(), 'configurations')
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
        self.tableHeadline = [ "名称", "大小", "修改时间"]
        self.excelHeadline = [ "检测员",   "检测时间",   "漏电流(μA)", "工作电流(μA)",   "ID核对",
                               "在线检测", "被测选发",    "电流(mA)",   "电压(V)",      "电流判断",
                               "内置选发",  "电流(mA)",   "电压(V)",   "电流判断",       "结论"    ]
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
        self.tv_FileInfo.verticalHeader().setFont(QFont("幼圆", 12, QFont.Light))
        self.tv_FileInfo.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tv_FileInfo.setEditTriggers (QAbstractItemView.NoEditTriggers)
        # 3.1 表格视图上下文菜单
        self.tvMenu = QMenu(self.tv_FileInfo)
        # self.tv_FileInfo.customContextMenuRequested.connect(self.tvCustomContextMenuRequested)
        self.isThisPCAsServer = False
        #*------------------------------- 表格显示控件之模型、委托、视图初始化 MVC--------------------------------*#
        # 检测数据Excel文件初始化
        self.excel = PrivateOpenPyxl()  # 实例化Excel对象
        self.xlsxFiles = []             # Excel文件名存储
        self.detFileList = []           # 检测文件           
        self.detFileDateList = []       # 检测文件保存时间          
        self.detIdList = []             # 检测文件中的所有ID       
        self.detTimeList = []           # ID对应的检测时间         
        self.detFileIdTimeList = []     # 综合信息List
        self.detFileIdTimeDict = {}     # 综合信息Dict
        self.detFileIdTimeDictBkp = {}  # 综合信息Dict备份
        self.detDateOfDetFile = []      # 模块检测日期时间

    def tvUpLoad(self):
        self.tbMessageAppend('开始上传')

    def tvDownLoad(self):
        self.tbMessageAppend('开始下载')

    def on_tv_FileInfo_customContextMenuRequested(self, p):
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

            self.le_ServerIP.clear()
            self.le_UserName.clear()
            self.le_UserPasswd.clear()

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
            self.downLoad.setText('下载汇总文件')
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
                # self.btn_ScanLocalFile.setEnabled(False)
                # self.btn_MergeFile.setEnabled(False)
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
                                    self.tbMessageAppend('目标计算机拒绝连接，请确认服务器是否开启')
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
        cnt = 0
        for file in xlsxFiles:
            xlsxStat = os.stat(file)
            if '~$' not in file:
                if ('xlsx' in file) and ('年' in file) and ('月' in file) and ('日' in file):
                    cnt = cnt + 1
                    #-------------------------------------------------------------文件名-------------------------------------------------------------#
                    filenameItem = QStandardItem(file)
                    filenameItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                    self.tableViewModel.setItem(self.tableviewRowIndex, 0, filenameItem)
                    #-------------------------------------------------------------文件大小-------------------------------------------------------------#
                    sizeOfFile = xlsxStat.st_size
                    if sizeOfFile < 1024:
                        size = '%.1fB' % sizeOfFile
                    elif sizeOfFile >= 1024 and sizeOfFile < 1024 * 1024:
                        sizeOfFile = sizeOfFile / 1024
                        size = '%.1fKB' % sizeOfFile
                    elif sizeOfFile >= 1024 * 1024 and sizeOfFile < 1024 * 1024 * 1024:
                        sizeOfFile = sizeOfFile / (1024 * 1024)
                        size = '%.1fMB' % sizeOfFile
                    sizeItem = QStandardItem(size)
                    sizeItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                    self.tableViewModel.setItem(self.tableviewRowIndex, 1, sizeItem)
                    #-------------------------------------------------------------修改时间-------------------------------------------------------------#
                    modifyTime = time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime(xlsxStat.st_mtime))
                    modifyItem = QStandardItem(modifyTime)
                    modifyItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                    self.tableViewModel.setItem(self.tableviewRowIndex, 2, modifyItem)
                    self.tableviewRowIndex = self.tableviewRowIndex + 1
        if cnt != 0:
            self.tbMessageAppend('检测到[' + str(cnt) + '个]检测相关文件')
            self.tbMessageAppend('本地文件扫描完成')
        else:
            self.tbMessageAppend('本地暂无检测相关文件')

    @QtCore.pyqtSlot()
    def on_btn_ScanRemoteFile_clicked(self):
        if self.pcAsServerOrClient == False: # 客户端才具有的功能
            try:
                self.tableviewRowIndex = 0
                self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())
                res = self.myftp.mlsd(path='.', facts=['modify', 'create', 'size'])
                cnt = 0
                for r in res:
                    if ('xlsx' in r[0]) and ('年' in r[0]) and ('月' in r[0]) and ('日' in r[0]):
                        cnt = cnt + 1
                        #-------------------------------------------------------------文件名-------------------------------------------------------------#
                        filenameItem = QStandardItem(r[0])
                        filenameItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                        self.tableViewModel.setItem(self.tableviewRowIndex, 0, filenameItem)
                        #-------------------------------------------------------------文件大小-------------------------------------------------------------#
                        sizeOfFile = int(r[1]['size'])
                        if sizeOfFile < 1024:
                            size = '%.1fB' % sizeOfFile
                        elif sizeOfFile >= 1024 and sizeOfFile < 1024 * 1024:
                            sizeOfFile = sizeOfFile / 1024
                            size = '%.1fKB' % sizeOfFile
                        elif sizeOfFile >= 1024 * 1024 and sizeOfFile < 1024 * 1024 * 1024:
                            sizeOfFile = sizeOfFile / (1024 * 1024)
                            size = '%.1fMB' % sizeOfFile
                        sizeItem = QStandardItem(size)
                        sizeItem.setFont(QFont('Times New Roman', 16, QFont.Weight.Light))
                        self.tableViewModel.setItem(self.tableviewRowIndex, 1, sizeItem)
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
                        self.tableviewRowIndex = self.tableviewRowIndex + 1
                if cnt == 0:
                    self.tbMessageAppend('服务器暂无检测相关文件')
                    return
                self.tbMessageAppend('服务器文件扫描完成')
            except error_perm:
                self.tbMessageAppend('无此目录')

    @QtCore.pyqtSlot()
    def on_btn_PushFile_clicked(self):
        if self.pcAsServerOrClient == False:
            self.tbMessageAppend('上传文件')
            if self.tableViewModel.rowCount() != 0:
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
                self.tbMessageAppend('请进行本地文件扫描！')
            
    @QtCore.pyqtSlot()
    def on_btn_PullFile_clicked(self):
        if self.pcAsServerOrClient == False:
            self.tbMessageAppend('下载文件')
            try:
                res = self.myftp.mlsd(path='.', facts=['modify', 'create', 'size'])
                cnt = 0
                for r in res:
                    if ('xlsx' in r[0]) and ('年' in r[0]) and ('月' in r[0]) and ('日' in r[0]):
                        cnt = cnt + 1
                        with open(r[0], 'wb') as fp:
                            self.tbMessageAppend('开始下载文件...\n>>' + r[0])
                            try:
                                downloadcmd = 'RETR ' + r[0]
                                res = self.myftp.retrbinary(downloadcmd, fp.write)
                                if res.find('226 Transfer complete.') != -1:
                                    self.tbMessageAppend('下载完成')
                            except error_perm:
                                self.tbMessageAppend('下载失败')
                if cnt == 0:
                    self.tbMessageAppend('服务器暂无检测相关文件')
            except error_perm:
                self.tbMessageAppend('无此文件')
            except ConnectionAbortedError:
                self.tbMessageAppend('连接已断开，请重新连接')
                self.btn_Connection.setText('连接服务器')
               
    @QtCore.pyqtSlot()
    def on_btn_MergeFile_clicked(self):
        self.xlsxFiles.clear()
        self.detFileList.clear()            # 检测文件
        self.detIdList.clear()              # 检测文件中的所有ID
        self.detTimeList.clear()            # ID对应的检测时间
        self.detFileIdTimeList.clear()      # 综合信息List
        self.detFileIdTimeDict.clear()      # 综合信息Dict
        self.detDateOfDetFile.clear()       # 模块检测日期时间        
        self.detFileIdTimeDictBkp.clear()   # 综合信息Dict备份
        self.tbMessageAppend('开始汇总...')
        # 列出文件
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
            if ('xlsx' in file) and ('年' in file) and ('月' in file) and ('日' in file) and ('汇总' not in file):
                self.detFileDateList.append(file)
                cnt = cnt + 1
                f = shutil.copy(file, 'f{0}.xlsx'.format(cnt))
                self.detFileList.append(f)
                self.excel.loadSheet(f)
                idRowGen = self.excel.ws.iter_rows(2, self.excel.ws.max_row, 1, self.excel.ws.max_column)
                self.detIdList.clear()          # 检测文件中的所有ID
                self.detTimeList.clear()        # ID对应的检测时间
                for rowid in idRowGen:
                    self.detIdList.append(rowid[6].value)
                    self.detTimeList.append(rowid[1].value)
                self.detFileIdTimeList.append([self.detIdList.copy(), self.detTimeList.copy()])
                self.excel.closeSheet()
        if cnt == 0:
            self.tbMessageAppend('无检测文件，请检测')
            return
        self.detFileIdTimeDict = dict.fromkeys(self.detFileList)
        for i in range(len(self.detFileList)):
            self.detFileIdTimeDict[self.detFileList[i]] = self.detFileIdTimeList[i]
        self.detFileIdTimeDictBkp = self.detFileIdTimeDict.copy()
        # 查找重复ID,对其检测结果按日期时间进行筛选
        tmp = set()
        l = len(self.detFileIdTimeDict)
        for index in range(l):
            if index != l-1: # 最后一位无须与其他比较
                f1 = self.detFileList[index]
                for t in range(l-1, index, -1):
                    f2 = self.detFileList[t]
                    tmp.clear()
                    tmp = set(self.detFileIdTimeDict[f2][0]) & set(self.detFileIdTimeDict[f1][0]) # 交集
                    if tmp != set():
                        print(tmp)
                        for id in tmp:
                            i = self.detFileIdTimeDict[f1][0].index(id)
                            j = self.detFileIdTimeDict[f2][0].index(id)
                            t1 = self.detFileIdTimeDict[f1][1][i]
                            t2 = self.detFileIdTimeDict[f2][1][j]
                            if t1 < t2:
                                self.excel.loadSheet(f1)
                                row = self.excel.getRowIndexByID(id)
                                self.excel.deleteRow(row)
                                self.detFileIdTimeDict[f1][0].remove(id)
                                self.detFileIdTimeDict[f1][1].remove(t1)
                            else:
                                self.excel.loadSheet(f2)
                                row = self.excel.getRowIndexByID(id)
                                self.excel.deleteRow(row)
                                self.detFileIdTimeDict[f2][0].remove(id)
                                self.detFileIdTimeDict[f2][1].remove(t2)
                            self.excel.saveSheet()
                            self.excel.closeSheet()
                    else:
                        continue
        # 汇总所有文件，生成汇总文件
        result = pd.DataFrame()
        for f in self.detFileList:
            result.reset_index()
            tmp = pd.read_excel(f)
            tmp.reset_index()
            result = pd.concat([result, tmp], ignore_index=True)
            os.remove(f)
        merge = '汇总.xlsx'
        result.to_excel(merge)
        self.excel.loadSheet(merge)
        maxrow = self.excel.ws.max_row # 获取最大行
        self.excel.addNamedStyle() # 为表格添加命名样式
        self.excel.deleteCloumn(1) # 删除第一列
        self.excel.saveSheet()
        for f in self.detFileDateList:
            self.detDateOfDetFile.append(f[0:11])
        mindate = min(self.detDateOfDetFile)
        maxdate = max(self.detDateOfDetFile)
        fianlmerge = '汇总' + '_[' + mindate + '-' + maxdate + ']_' + str(maxrow) + '条' +'.xlsx'
        try:
            os.rename(merge, fianlmerge)
            self.tbMessageAppend('已成生汇总文件：\n' + fianlmerge)
        except FileExistsError:
            os.remove(fianlmerge)
            os.rename(merge, fianlmerge)
            self.tbMessageAppend('已覆盖汇总文件：\n' + fianlmerge)
        self.excel.closeSheet()
        # 设置表头样式
        self.excel.setHeaderStyle(fianlmerge, self.excelHeadline)
        # 设置数据样式
        self.excel.setCellStyle(fianlmerge)
        # 完成汇总
        QApplication.processEvents()
        time.sleep(1)
        self.tbMessageAppend('完成汇总')

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