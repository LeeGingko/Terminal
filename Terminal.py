# -*- coding: utf-8 -*-
from PyQt5.QtGui import QPixmap
from UserImport import *

class MainWin(QtWidgets.QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        super(MainWin, self).__init__()  # 继承父类的所有属性
        # 获取程序当前工作路径
        self.currentWorkDirectory = ''
        self.currentWorkDirectory = os.getcwd()
        self.configFolder = os.path.join(os.getcwd(), 'configurations')
        self.createConfigurationsFolder()
        # 初始化UI
        self.initUi()

    def __del__(self):
        self.timsRefresh.wait()
        self.protocolWin.serialManager.wait()
        self.protocolWin.serialMonitor.wait()
        print("{} 退出主线程".format(__file__))

    def initUi(self):
        # 初始化主窗口
        self.setupUi(self)
        # 设置窗口居中显示
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()
        # print("Your screen's size is:", self.width, "X", self.height)
        self.resize(self.width, self.height)
        self.Wsize = self.geometry()
        centerX = int((self.width - self.Wsize.width()) / 2)
        centerY = int((self.height - self.Wsize.height()) / 2 - 10)
        self.move(centerX, centerY)
        self.setWindowTitle("Detector")
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setWindowState(Qt.WindowMaximized)
        self.isEncodeOK = False
        iconPath = os.path.join(self.currentWorkDirectory, './resources/icons/IDDD.ico')
        self.setWindowIcon(QIcon(iconPath))
        self.setIconSize(QSize(256, 256))
        # 状态栏初始化
        self.myStatusBar = QStatusBar()
        self.myStatusBar.setFont(QFont("Times New Roman", 16, QFont.Light))
        self.pathLabel = QLabel(self)
        self.myStatusBar.addPermanentWidget(self.pathLabel) # 添加操作文件显示控件
        self.setStatusBar(self.myStatusBar)
        # 消息提示窗口初始化
        self.textBrowser.setFontFamily("微软雅黑")
        self.textBrowser.setFontPointSize(14)
        # 自定义工具实例化
        self.usualTools = Tools()
        # 配置文件路径
        self.configFile = 'config.txt'
        self.configFilePath = os.path.join(self.configFolder, self.configFile)
        # 模块状态记录
        self.devicesState = {}
        self.devicesStateFile = 'devicesState.txt'
        self.devicesStateFilePath = os.path.join(self.configFolder, self.devicesStateFile) # 每获取一个编号，则存入到硬盘
        # 检测结果记录存储文件，防止意外断电导致检测数据丢失
        self.resultsFile = 'results.txt'
        self.resultsFilePath = os.path.join(self.currentWorkDirectory, self.resultsFile)
        # 分别创建文件
        self.createConfigFile()
        self.createDevicesStateFile()
        self.createResultsFile()
        # 通信配置界面类实例
        self.protocolWin = ProtocolWin()
        self.protocolWin.protocolAppendSignal.connect(self.userTextBrowserAppend)
        # 串口通信实例传入到全局对象，供阈值设置实例访问
        GetSetObj.set(self.protocolWin)
        # 串口接收线程处理函数
        self.protocolWin.serialManager.recvSignal.connect(self.serialRecvData)
        # 阈值设置界面类实例
        self.thresholdWin = ThresholdWin()
        self.thresholdWin.thresholdAppendSignal.connect(self.userTextBrowserAppend)
        self.thresholdWin.openFileSignal.connect(self.showOperationFile)
        # 工作模式初始化
        self.workMode = { "encoding": "X",  "detection": "X" } # 未知状态
        # 检测以及编码默认状态设置
        self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/NONE)}")
        self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/NONE)}")
        # 操作人员姓名录入
        self.is_name_input = False
        self.name = "操作员01" # 默认操作员姓名
        self.isNameInput = False
        nameRegValidator = QRegularExpressionValidator(self)
        nameReg = QRegularExpression("^(?![\\《\\》\\，\\、\\。\\；\\：\\‘\\’\\“\\”\\？\\【\\】\\（\\）\\-\\—])[a-zA-Z0-9\u4e00-\u9fa5]+$")
        nameRegValidator.setRegularExpression(nameReg)
        self.lineEdit_op_name.setValidator(nameRegValidator)
        self.lineEdit_op_name.setMaxLength(7)
        # 本地时间更新线程
        self.timsRefresh = LocalTimeThread()
        self.timsRefresh.secondSignal.connect(self.showDaetTime)
        self.timsRefresh.start()
        # 检测数据Excel文件初始化
        self.excel = PrivateOpenPyxl() # Excel实例化全局对象
        self.isExcelSavedFirst = True # 是否是第一次保存Excel
        self.isExcelSaved = False # 是否是已经保存 Excel
        self.excelFilePath = "" # Excel文件路径
        self.excelFile = "" # Excel文件
        self.excelOpenState = False
        # 另存为文件
        self.isExcelAsSavedFirst = True # 是否是第一次另存为Excel
        self.isExcelAsSaved = False # 是否是已经另存为Excel
        self.excelAsFilePath = "" # Excel另存为文件路径
        self.excelAsFile = "" # Excel另存为文件
        self.excelAsOpenState = False
        self.excelRecordFile = os.path.join(self.configFolder, 'excel_save_record.txt')
        self.createExcelRecordFile()
        # 默认检测结果
        initTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # 检测时间
        self.resultDefaultList = [
            "name",  initTime,    "E",    "E",   "失败",
            "离线",   "EEEEE",     "E",    "E",   "异常",
            "EEEEE",    "E",      "E",    "异常", '失败' ]
        # 测试检测结果，初始为默认检测结果
        self.resultList = self.resultDefaultList.copy()
        # 单次测试检测结果备份，进行重复检测结果判断
        self.resultLastList = self.resultList.copy()
        #*------------------------------- 表格之模型、委托、视图初始化 --------------------------------*#
        # 1 表格模型初始化
        self.tableRow = 0 # 写入excel表格的行索引
        self.tableHeadline = [
            "检测员",   "检测时间",   "漏电流(μA)", "工作电流(μA)",  "ID核对",
            "在线检测", "被测选发",   "电流(mA)",   "电压(V)",      "电流判断",
            "内置选发", "电流(mA)",  "电压(V)",    "电流判断",      "结论" ]   
        self.tableViewModel = QStandardItemModel(0, 15, self)
        self.tableViewModel.setHorizontalHeaderLabels(self.tableHeadline) # 设置表头
        # 2 表格委托初始化
        self.tableViewDelegate = PrivateTableViewDelegate()
        # 3 表格视图初始化
        self.tableView_result.setModel(self.tableViewModel)
        self.tableView_result.horizontalHeader().setStretchLastSection(True)
        self.tableView_result.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView_result.setItemDelegate(self.tableViewDelegate)
        self.tableView_result.horizontalHeader().setFont(QFont("幼圆", 12, QFont.Light))
        self.tableView_result.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_result.verticalHeader().hide()
        self.tableView_result.setContextMenuPolicy(Qt.CustomContextMenu)
        # 3.1 表格视图上下文菜单
        self.tvMenu = QMenu(self.tableView_result)
        self.saveSelected = QAction()
        self.saveAll = QAction()
        self.dropSelected = QAction()
        self.dropAll = QAction()
        self.saveSelected.setText('保存选中行')
        self.saveAll.setText('保存全部行')
        self.dropSelected.setText('删除选中行')
        self.dropAll.setText('删除全部行')
        self.saveSelected.triggered.connect(self.tvSaveSelected)
        self.saveAll.triggered.connect(self.tvSaveAll)
        self.dropSelected.triggered.connect(self.tvDropSelected)
        self.dropAll.triggered.connect(self.tvDropAll)
        # self.tvMenu.addAction(self.saveSelected)
        # self.tvMenu.addAction(self.saveAll)
        self.tvMenu.addAction(self.dropSelected)
        # self.tvMenu.addAction(self.dropAll)
        self.tableView_result.customContextMenuRequested.connect(self.tvCustomContextMenuRequested)
        # 编码输入验证器设置
        regValidator = QRegularExpressionValidator(self)
        reg = QRegularExpression("[A-E0-9]+$") # 字母范围A~F, 数字0~9
        regValidator.setRegularExpression(reg)
        # UID输入编辑栏初始化
        self.lineEdit_uidInput.setMaxLength(5)
        self.lineEdit_uidInput.setValidator(regValidator)
        self.lineEdit_uidInput.setToolTip("字母范围A~E, 数字0~9")
        self.lineEdit_uidInput.setFocus()
        self.setMouseTracking(True)
        # 配置文件路径
        self.thresholdWin.configPath = self.configFilePath
        # 发送命令响应
        self.isDeviceResponsed = False
        # 检测状态
        self.detectionState = None # 未知状态
        # 确认检测完毕
        self.confirmDetection = False
        # 失能保存和另存为
        self.pushBtn_saveResults.setEnabled(False)
        self.pushBtn_saveResultsAs.setEnabled(False)
        # 查询命令返回编码
        self.queryCode = 'EEEEE'
        # 是否只是查询编码
        self.isPureQueryCode = None
        # 点击了保存还是另存为
        self.savedOrSavedAsClicked = None
        # 先加载保存记录
        self.openExcelRecord()
        # 测试仪响应定时器
        self.devResponseTimer = QTimer()
        self.devResponseTimer.timeout.connect(self.deviceNoResponse)
        # 接通电源参数下发定时器
        self.powerOnParaTimer = QTimer() 
        self.powerOnParaTimer.timeout.connect(self.autoSendParameters)
        # 下发参数阈值
        self.startParaTimer = QTimer() # 使用定时器，防止主界面卡在步骤1中
        self.startParaTimer.timeout.connect(self.autoSendParameters)   
        # 1 连接控制仪串口
        self.protocolWin.autoConnectDetector()
        # 2 四秒后执行参数下发
        self.startParaTimer.start(4000)
        self.lineEdit_op_name.setFocus()
        self.isLVLCOK = False
        self.encDetEncdetQue = 0
        self.detResCode = [ -1, -1, -1, -1, -1, -1, -1]

    def showDaetTime(self, timeStr):
        self.myStatusBar.showMessage(timeStr)
    
    def userTextBrowserAppend(self, str):
        t = self.usualTools.getTimeStamp()
        self.textBrowser.append(t + str)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)         
    
    def createConfigurationsFolder(self):
        if not os.path.isdir(self.configFolder):
            os.mkdir(self.configFolder)
        else:
            pass

    def createConfigFile(self):
        if os.path.isfile(self.configFilePath): # 文件已存在
            pass
        else: # 创建文件
            try:
                with open(self.configFilePath, encoding="utf-8", mode="w") as scfp:
                    # scfp.write(self.configFilePath)
                    pass
            except:
                pass

    def createDevicesStateFile(self):
        if os.path.isfile(self.devicesStateFilePath): # 文件已存在
            pass
        else: # 创建文件
            try:
                with open(self.devicesStateFilePath, encoding="gbk", mode="w") as sdsf:
                    sdsf.write(self.devicesState)
            except:
                pass
    
    def updateDevicesStateFile(self):
        with open(self.devicesStateFilePath, mode='wb') as sdsf:
            pk.dump(self.devicesState, sdsf)
        
    def loadDevicesStateFile(self):
        try:
            with open(self.devicesStateFilePath, mode='rb') as sdsf:
                r = pk.load(sdsf)
                # print(r)
            return r
        except:
            pass

    def createExcelRecordFile(self):
        if not os.path.isfile(self.excelRecordFile):
            self.openExcelRecord()
        else:
            pass

    def openExcelRecord(self):
        try:
            with open(self.excelRecordFile, "rb") as esrf:
                oer = pk.load(esrf) # 将二进制文件对象转换成Python对象
            self.isExcelSavedFirst = oer[0][0]
            self.isExcelSaved = oer[0][1]
            self.excelFilePath = oer[1]
            self.excelFile = os.path.split(self.excelFilePath)[1]
            # As
            self.isExcelAsSavedFirst = oer[2][0]
            self.isExcelAsSaved = oer[2][1]
            self.excelAsFilePath = oer[3]
            self.excelAsFile = os.path.split(self.excelAsFilePath)[1]
        except:
            pass
    
    def saveExcelRecord(self):
        self.saved_info = ([self.isExcelSavedFirst, self.isExcelSaved],  self.excelFilePath, [self.isExcelAsSavedFirst, self.isExcelAsSaved], self.excelAsFilePath)
        with open(self.excelRecordFile, "wb") as esrf:
            pk.dump(self.saved_info, esrf) # 用dump函数将Python对象转成二进制对象文件
    
    def createResultsFile(self):
        if os.path.isfile(self.resultsFile): # 文件已存在
            pass
        else: # 创建文件
            try:
                with open(self.resultsFilePath, encoding="gbk", mode="w") as srfp:
                    # sdsf.write(self.devicesState) 仅仅是创建文件
                    pass
            except:
                pass
    
    def updateResultsFile(self, list): # 未进行检测直接写入检测结果到硬盘
        with open(self.resultsFile, mode='a') as srf:
            s = ",".join(list)
            srf.write(s + '\n')

    def loadResultsFile(self):  # 加载检测结果
        with open(self.resultsFile, mode='r') as srf:
            r = srf.readlines()
            return r

    def isResultDetected(self, s, uid): # 当前模块检测结果是否保存
        for res in s:
            if uid in res:
                return True, s.index(res)
        return None, None

    def changeResultsFile(self, uid): # 覆盖当前模块已保存的检测结果
        res = self.loadResultsFile() # 加载检测结果
        detSta, index = self.isResultDetected(res, uid)
        if detSta != None and index != None:
            tmplist = self.resultList
            tmplist[14] = tmplist[14] + '\n'
            s = ','.join(tmplist)
            res[index] = s # 覆盖检测结果  
        with open(self.resultsFile, mode='a+') as srf: # 修改内容后重新写入到检测结果文件
            srf.seek(0)
            srf.truncate()
            for t in range(len(res)):
                srf.write(res[t])
            srf.flush() # 立即更新到硬盘
    
    def deviceNoResponse(self):
        if not self.isDeviceResponsed:
            self.userTextBrowserAppend("测试仪无响应，请重新选择串口或检查连线！")
        self.devResponseTimer.stop()    
    
    def showOperationFile(self, path):
        self.pathLabel.setText("操作文件：" + path)

    def enableFucnBtn(self):
        self.pushBtn_deviceEncoding.setEnabled(True)
        self.pushBtn_deviceDetection.setEnabled(True)
        self.pushBtn_deviceEncodingDetection.setEnabled(True)
        self.pushBtn_queryCode.setEnabled(True)

    def disableFucnBtn(self):
        self.pushBtn_deviceEncoding.setEnabled(False)
        self.pushBtn_deviceDetection.setEnabled(False)
        self.pushBtn_deviceEncodingDetection.setEnabled(False)
        self.pushBtn_queryCode.setEnabled(False)

#----------------------------------------数据显示上下文菜单----------------------------------------#      
    def tvSaveSelected(self):
        if len(self.tvRowList) != 0:
            self.userTextBrowserAppend('保存选中数据')
        else:
            self.userTextBrowserAppend('无显示数据，请选中数据显示区域或进行检测')

    def tvSaveAll(self):
        if len(self.tvRowList) != 0:
            self.userTextBrowserAppend('保存全部数据')
        else:
            self.userTextBrowserAppend('无显示数据，请选中数据显示区域或进行检测')

    def tvDropSelected(self):
        l = len(self.tvRowList)
        if l != 0:
            if self.confirmDetection:
                choice = QMessageBox.critical(self, "删除视图数据", "是否删除视图数据，此操作会造成数据丢失", QMessageBox.Yes | QMessageBox.Cancel)
                if choice == QMessageBox.Yes:
                    for n in self.tvRowList:
                        self.tableViewModel.removeRow(n)
                    self.tableRow = self.tableRow - l
                    self.userTextBrowserAppend('删除选中数据')
                else:
                    self.confirmDetection = False
                    self.userTextBrowserAppend('取消删除数据')
            else:
                self.userTextBrowserAppend('请确认检测完毕后决定是否删除数据')
        else:
            self.userTextBrowserAppend('无显示数据，请选中数据显示区域或进行检测')
        
    def tvDropAll(self):
        if len(self.tvRowList) != 0:
            self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())
            self.userTextBrowserAppend('删除全部数据')
        else:
            self.userTextBrowserAppend('无显示数据，请选中数据显示区域或进行检测')

    def tvCustomContextMenuRequested(self, p):
        self.tvIndex = self.tableView_result.selectionModel().selectedRows()
        self.tvRowList = []
        for i in self.tvIndex:
            self.tvRowList.append(i.row())
        self.tvRowList.sort(key=int, reverse=True)
        print(self.tvRowList)
        self.tvMenu.exec_(self.tableView_result.mapToGlobal(p))
#----------------------------------------数据显示上下文菜单----------------------------------------#      
    
    def isResultsExcelFileOpened(self):
        if os.path.exists('~$' + self.excelFile):
            # print('excel已被打开')
            return True
        else:
            # print('excel未被打开')
            return False

#----------------------------------------UID输入完成槽函数----------------------------------------#
    @QtCore.pyqtSlot()
    def on_lineEdit_op_name_editingFinished(self):
        self.userTextBrowserAppend('输入姓名：' + self.lineEdit_op_name.text())
#----------------------------------------UID输入完成槽函数----------------------------------------#

#----------------------------------------按钮槽函数----------------------------------------#  
    @QtCore.pyqtSlot()
    def on_pushBtn_protocolSetting_clicked(self):
        self.protocolWin.show()
        self.lineEdit_uidInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushBtn_thresholdSetting_clicked(self):
        self.thresholdWin.show()
        self.lineEdit_uidInput.setFocus()
    
    @QtCore.pyqtSlot()
    def on_pushBtn_deviceSelfCheck_clicked(self):
        if self.protocolWin.prvSerial.isOpen() == True:
            self.protocolWin.comIndex = self.protocolWin.comDescriptionList.index(self.protocolWin.comDescription)
            self.portInfo = QSerialPortInfo(self.protocolWin.comPortList[self.protocolWin.comIndex].device)  # 该串口信息
            self.portStatus = self.portInfo.isBusy()  # 该串口状态
            if self.portStatus == True:  # 该串口空闲
                self.userTextBrowserAppend("测试仪自检")
                self.getSelfCheckParameters()
                self.lineEdit_uidInput.setFocus()
        else:
            QMessageBox.information(self, "串口信息", "串口未打开，请打开串口", QMessageBox.Yes)

    @QtCore.pyqtSlot()
    def on_pushBtn_clearUidInput_clicked(self):
        self.lineEdit_uidInput.clear()
    
    @QtCore.pyqtSlot()
    def on_pushBtn_queryCode_clicked(self):
        self.encDetEncdetQue = 3
        print("/*$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$*/")
        print("Querying......")
        self.userTextBrowserAppend("执行查询")
        self.isPureQueryCode = True
        if self.protocolWin.prvSerial.isOpen():
            self.disableFucnBtn()
            self.protocolWin.data = b''
            self.protocolWin.rxCheck = 0
            self.protocolWin.prvSerial.flushOutput()
            self.protocolWin.serialSendData(Func.f_DevQueryCurrentCode, '', '')
            self.isDeviceResponsed = False
            self.devResponseTimer.start(2000)
        else:
            self.userTextBrowserAppend("串口未打开")

    def encoding(self, uid):
        self.protocolWin.data = b''
        self.protocolWin.rxCheck = 0
        if self.protocolWin.prvSerial.isOpen():
            self.protocolWin.prvSerial.flushOutput()
        self.protocolWin.serialSendData(Func.f_DevEncoding, uid, '')

    @QtCore.pyqtSlot()
    def on_pushBtn_deviceEncoding_clicked(self):
        self.encDetEncdetQue = 0
        if self.workMode["encoding"] == "1":
            print("/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/")
            print("Encoding......")
            self.userTextBrowserAppend("执行编码")
            if self.protocolWin.prvSerial.isOpen():
                name = self.lineEdit_op_name.text()
                if name != '':
                    self.uid = self.lineEdit_uidInput.text()
                    if self.uid != '':
                        self.disableFucnBtn()
                        self.isEncodeOK = False
                        self.userTextBrowserAppend("输入编码：" + self.lineEdit_uidInput.text())
                        self.protocolWin.data = b''
                        self.protocolWin.rxCheck = 0
                        self.protocolWin.prvSerial.flushOutput()
                        self.protocolWin.serialSendData(Func.f_DevQueryCurrentCode, '', '')
                        self.isPureQueryCode = False
                        QApplication.processEvents()
                        self.sleepUpdate(3)
                        QApplication.processEvents()
                        self.devicesState = self.loadDevicesStateFile()
                        if self.devicesState != None:# 检测记录不为空
                            if self.uid in self.devicesState:
                                encSta = self.devicesState[self.uid].get('enc')
                                if encSta != None:
                                    if self.queryCode == self.uid: # 当前模块进行过编码，输入的UID和当前模块UID相同
                                        choice = QMessageBox.information(self, "执行编码", "覆盖模块编码？", QMessageBox.Yes | QMessageBox.Cancel)
                                        if choice == QMessageBox.Yes:
                                            self.encoding(self.uid)
                                        else:
                                            self.userTextBrowserAppend("取消覆盖模块编码")
                                            self.enableFucnBtn()
                                    else:
                                        self.encoding(self.uid)
                            else:
                                if self.workMode["encoding"] == "1":
                                    self.devicesState[self.uid] = { 'enc':None, 'det':None, 'res':[] }
                                    self.encoding(self.uid)
                        else:
                            self.devicesState = {}
                            self.devicesState[self.uid] = { 'enc':None, 'det':None, 'res':[] }
                            self.encoding(self.uid)
                    else:
                        self.userTextBrowserAppend("请输入编码！")
                else:
                    self.userTextBrowserAppend("请输入姓名！")
            else:
                self.userTextBrowserAppend("串口未打开")
        elif self.workMode["encoding"] == "X":
            self.userTextBrowserAppend("编码【未知】")
        else:
            self.userTextBrowserAppend("编码【未开启】")

    def detection(self, uid):
        self.detectionTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.protocolWin.data = b""
        self.protocolWin.rxCheck = 0
        self.protocolWin.prvSerial.flushOutput()
        self.protocolWin.serialSendData(Func.f_DevDetection, uid, '')

    @QtCore.pyqtSlot()
    def on_pushBtn_deviceDetection_clicked(self):
        for t in range(len(self.detResCode)):
            self.detResCode[t] = -1
        self.encDetEncdetQue = 1
        if self.workMode["detection"] == "1":
            self.isLVLCOK = False
            print("/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/")
            print("Detecting......")
            self.userTextBrowserAppend("执行检测")
            if self.protocolWin.prvSerial.isOpen():
                self.uid = self.lineEdit_uidInput.text()
                name = self.lineEdit_op_name.text()
                if name != '':
                    if self.uid != "":
                        self.disableFucnBtn()
                        self.userTextBrowserAppend("输入编码：" + self.uid)
                        res = self.loadResultsFile() # 加载检测结果
                        resSta, index = self.isResultDetected(res, self.uid)
                        self.devicesState = self.loadDevicesStateFile()
                        if self.devicesState != None:
                            if not self.uid in self.devicesState: # 还未进行过编码操作
                                if resSta == None and index == None: # 确实未编码且未检测，必需先执行编码
                                    self.devicesState[self.uid] = { 'enc':None, 'det':None, 'res':[]}
                                    self.userTextBrowserAppend("该模块未编码，请执行编码！")
                                    self.enableFucnBtn()
                            else: # 进行过编码，是否检测过未知
                                detsta = self.devicesState[self.uid].get('det')
                                if detsta == None and resSta == None: # 该模块在此次工作中未进行过检测
                                    self.devicesState[self.uid]['det'] = None
                                    self.detection(self.uid)
                                    self.detectionState = 1
                                elif (detsta == None or detsta == True or detsta == False) and (resSta != None and index != None): # 该模块在此次工作中已进行过检测，结果已经保存
                                    choice = QMessageBox.information(self, "执行检测", "已有检测结果，重新检测模块？", QMessageBox.Yes | QMessageBox.Cancel)
                                    if choice == QMessageBox.Yes:
                                        self.devicesState[self.uid]['det'] = None
                                        self.detection(self.uid)
                                        self.detectionState = 2                                        
                                    else:
                                        self.userTextBrowserAppend("取消重新检测")
                                        self.enableFucnBtn()
                        else:
                            self.devicesState = {}
                            self.devicesState[self.uid] = { 'enc':None, 'det':None, 'res':[]}
                            self.userTextBrowserAppend("未有任何模块编码，请执行编码！")
                            self.enableFucnBtn()
                    else:
                        self.userTextBrowserAppend("请输入编码！")
                elif name == '':
                    self.userTextBrowserAppend("请输入姓名！")
            else:
                self.userTextBrowserAppend("串口未打开")
        elif self.workMode["detection"] == "X":
            self.userTextBrowserAppend("检测【未知】")
        else:
            self.userTextBrowserAppend("检测【未开启】")
    
    def encodingDetection(self, uid):
        self.on_pushBtn_deviceEncoding_clicked()
        while True:
            QApplication.processEvents()
            time.sleep(0.01)
            if self.protocolWin.data != b'':
                if self.protocolWin.data[2] != 50:
                    continue
                else:
                    break
        tmp = self.protocolWin.data.decode('utf-8')
        if tmp.find('UIDOK', 0, len(tmp)) != -1:
            self.on_pushBtn_deviceDetection_clicked()
        else:
            self.enableFucnBtn()
            self.userTextBrowserAppend("编码未通过，无法执行检测！")
    
    @QtCore.pyqtSlot()
    def on_pushBtn_deviceEncodingDetection_clicked(self):
        for t in range(len(self.detResCode)):
            self.detResCode[t] = -1
        self.encDetEncdetQue = 2
        self.userTextBrowserAppend("执行编码和检测")
        if self.workMode["encoding"] == "1" and self.workMode["detection"] == "1":
            if self.protocolWin.prvSerial.isOpen():
                self.detectionTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                self.uid = self.lineEdit_uidInput.text()
                self.isPureQueryCode = True
                self.encodingDetection(self.uid)
            else:
                self.userTextBrowserAppend("串口未打开")
        elif self.workMode["encoding"] == "1" and self.workMode["detection"] == "0":
            self.userTextBrowserAppend("编码【已开启】，检测【未开启】") 
        elif self.workMode["encoding"] == "0" and self.workMode["detection"] == "1":
            self.userTextBrowserAppend("编码【未开启】，检测【已开启】") 
        elif self.workMode["encoding"] == "0" and self.workMode["detection"] == "0":
            self.userTextBrowserAppend("编码【未开启】，检测【未开启】") 
        elif self.workMode["encoding"] == "X" and self.workMode["detection"] == "X":
            self.userTextBrowserAppend("编码【未知】，检测【未知】") 
    
    @QtCore.pyqtSlot()
    def on_pushBtn_confirmDetection_clicked(self):
        choice = QMessageBox.warning(self, "检测结果确认", "确认检测完毕？", QMessageBox.Yes | QMessageBox.Cancel)
        if choice == QMessageBox.Yes:
            self.pushBtn_saveResults.setEnabled(True)
            self.pushBtn_saveResultsAs.setEnabled(True)
            self.userTextBrowserAppend("确认检测完成")
            self.confirmDetection = True
        else:
            self.userTextBrowserAppend("检测还未完成")
            self.confirmDetection = False

    @QtCore.pyqtSlot()
    def on_pushBtn_saveResults_clicked(self):
        self.savedOrSavedAsClicked = True
        self.excelOpenState = self.isResultsExcelFileOpened()
        if self.excelOpenState:
            self.userTextBrowserAppend(self.excelFile + '已被打开, 请关闭文件后再写入')
        else:
            if self.isExcelSavedFirst and self.isExcelSaved == False:
                self.firstsaveResults()
            elif self.isExcelSavedFirst == False and self.isExcelSaved:
                self.saveResults()
        self.showOperationFile(self.excelFilePath) 
        self.lineEdit_uidInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushBtn_saveResultsAs_clicked(self):
        self.openExcelRecord()
        self.savedOrSavedAsClicked = False
        self.excelAsOpenState = self.isResultsExcelFileOpened()
        if self.excelAsOpenState:
            self.userTextBrowserAppend(self.excelAsFilePath + '已被打开, 请关闭文件后再写入')
        else:
            if self.isExcelAsSavedFirst == True:
                file = './recording'
                self.excelAsFilePath, isAccept =  QFileDialog.getSaveFileName(self, "保存检测结果另存为", '', "recorded data(*.xlsx)")
                if isAccept:
                    if self.excelAsFilePath:
                        self.excelAsFile = os.path.split(self.excelAsFilePath)[1]
                        self.excel_sheet = "Sheet Of Records"
                        self.excel.initWorkBook(self.excelAsFile, self.excel_sheet)
                        self.excel.loadSheet(self.excelAsFile)
                        self.excel.wrtieRow(self.tableHeadline) # 添加表头
                        self.excel.saveSheet()
                        self.excel.closeSheet()
                        self.userTextBrowserAppend("创建数据记录表成功")
                        self.userTextBrowserAppend("@保存至\"" + str(self.excelAsFilePath) + "\"")
                        self.isExcelAsSavedFirst = False
                        self.isExcelAsSaved = True
                        self.saveExcelRecord()
                        self.openExcelRecord()
                        if self.saveDataOfView() == True:
                            self.userTextBrowserAppend("已保存" + str(self.tableViewModel.rowCount()) + "条数据记录，请进行下一次检测")
                            self.resultLastList = self.resultList.copy()
                            self.tableViewModel.removeRows(0, self.tableViewModel.rowCount()) # 清除表格视图
                            self.tableRow = 0
                            self.lineEdit_uidInput.setFocus() 
                            self.pushBtn_saveResults.setEnabled(False)
                            self.pushBtn_saveResultsAs.setEnabled(False)
                        self.showOperationFile(self.excelAsFilePath) 
                    else:
                        pass
                self.saveExcelRecord()
            else:
                if os.path.isfile(self.excelAsFilePath):
                    if self.saveDataOfView() == True:
                        self.userTextBrowserAppend("已保存" + str(self.tableViewModel.rowCount()) + "条数据记录，请进行下一次检测")
                        self.resultLastList = self.resultList.copy()
                        self.tableViewModel.removeRows(0, self.tableViewModel.rowCount()) # 清除表格视图
                        self.tableRow = 0
                        self.pushBtn_saveResults.setEnabled(False)
                        self.pushBtn_saveResultsAs.setEnabled(False)
                        self.showOperationFile(self.excelAsFilePath) 
                        self.lineEdit_uidInput.setFocus()
                        self.isExcelAsSavedFirst = False
                        self.isExcelAsSaved = True
                else:
                    self.isExcelAsSavedFirst = True
                    self.isExcelAsSaved = False
                    self.showOperationFile('') 
                    self.userTextBrowserAppend("文件已被删除或移动，请重新创建文件！")
        self.saveExcelRecord()
        self.lineEdit_uidInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushBtn_showResults_clicked(self):
        isOpenState = self.isResultsExcelFileOpened()
        if isOpenState:
            self.userTextBrowserAppend(self.excelFile + '已打开')
        else:
            self.openExcelRecord()
            recordsfile, _ = QFileDialog.getOpenFileName(self, "打开记录文件", './', 'records (*.xlsx)')
            if recordsfile:
                if recordsfile == self.excelFilePath:
                    self.isConfigSaved = True
                    self.showOperationFile(self.excelFilePath)
                elif recordsfile == self.excelAsFilePath:
                    self.showOperationFile(self.excelAsFilePath)
                    self.isConfigAsSaved = True
                os.startfile(recordsfile)
            self.saveExcelRecord()
            
        self.lineEdit_uidInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushBtn_clearResults_clicked(self):
        if self.tableViewModel.rowCount() != 0:
            if self.confirmDetection:
                choice = QMessageBox.critical(self, "清除结果", "清除检测结果？", QMessageBox.Yes | QMessageBox.Cancel)
                if choice == QMessageBox.Yes:
                    self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())
                    self.tableRow = 0
                    self.pushBtn_saveResults.setEnabled(False)
                    self.pushBtn_saveResultsAs.setEnabled(False)
                    self.lineEdit_uidInput.setFocus()
                else:
                    self.userTextBrowserAppend("取消清除检测结果")
            else:
                self.userTextBrowserAppend('请确认检测完毕后决定是否删除数据')
        else:
            self.userTextBrowserAppend('无显示数据，请进行检测')
        
    @QtCore.pyqtSlot()
    def on_pushBtn_cleanMsgArea_clicked(self):
        if self.textBrowser.toPlainText() != "":
            self.textBrowser.clear()
#----------------------------------------按钮槽函数----------------------------------------#    
    
    def serialRecvData(self, data):
        self.protocolWin.data = data
        if data.decode("utf-8") == "接收数据失败":
            self.userTextBrowserAppend("接收数据失败")
        else:
            tmp = data.decode("utf-8")
            if tmp[0] == "U":
                if self.protocolWin.rxFrameCheck() == State.s_RxFrameCheckOK:
                    if tmp[2] == Func.f_DevSettingThreshold:
                        self.parseSettingThreshold()
                    elif tmp[2] == Func.f_DevGetSelfPara:
                        self.parseGetSelfCheckParameters()
                    elif tmp[2] == Func.f_DevEncoding:
                        self.parseEncodingResults()
                    elif tmp[2] == Func.f_DevDetection:
                        self.parseDetectionResults()
                    elif tmp[2] == Func.f_DevEncodingDetection:
                        self.parseDetectionResults()
                    elif tmp[2] == Func.f_DevQueryCurrentCode:
                        self.parseQueryCodeResults()
                else:
                    self.userTextBrowserAppend("接收帧错误")
            elif tmp[0] == "R":
                if tmp[1] == "M":
                    self.reportSystemPower(tmp)
                else:
                    self.updateWorkMode(tmp)
    
    def reportSystemPower(self, str):
        print("In reportSystemPower...............")
        if str == "RMPO\r\n":
            self.enableFucnBtn()
            self.userTextBrowserAppend("测试仪已上电，线路供电接通")
            self.on_pushBtn_deviceSelfCheck_clicked() # 进行一次测试仪自检
            self.powerOnParaTimer.start(4000)
        else:
            self.userTextBrowserAppend("测试仪已上电，线路供电断开")
   
    def setWorkMode(self, tmp):
        self.workMode["encoding" ] = "0" if tmp[len(tmp) - 6] == 48 else "1"
        self.workMode["detection"] = "0" if tmp[len(tmp) - 5] == 48 else "1"

    def getWorkMode(self):
        return self.workMode
    
    def updateWorkMode(self, str):
        # print("In updateWorkMode...............")
        endc = str[2]
        dete = str[3]
        self.workMode["encoding" ] = "0" if endc == "0" else "1"
        self.workMode["detection"] = "0" if dete == "0" else "1"
        if str[1] == "X":
            if endc == "0":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/OFF)}")
                self.userTextBrowserAppend("编码发生改变，编码【关闭】")
            elif endc == "1":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/ON)}")
                self.userTextBrowserAppend("编码发生改变，编码【开启】")
        elif str[1] == "Y":
            if dete == "0":
                self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/OFF)}")
                self.userTextBrowserAppend("检测发生改变，检测【关闭】")
            elif dete == "1":
                self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/ON)}")
                self.userTextBrowserAppend("检测发生改变，检测【开启】")
        elif str[1] == "Z":
            if endc == "1" and dete == "1":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/ON)}")
                self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/ON)}")
                self.userTextBrowserAppend("编码检测发生改变，编码【开启】 检测【开启】")
            elif endc == "1" and dete == "0":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/ON)}")
                self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/OFF)}")
                self.userTextBrowserAppend("编码检测发生改变，编码【开启】 检测【关闭】")
            elif endc == "0" and dete == "1":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/OFF)}")
                self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/ON)}")
                self.userTextBrowserAppend("编码检测发生改变，编码【关闭】 检测【开启】")
            elif endc == "0" and dete == "0":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/OFF)}")
                self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/OFF)}")
                self.userTextBrowserAppend("编码检测发生改变，编码【关闭】 检测【关闭】")

    def parseWorkMode(self):
        wm = self.getWorkMode()
        # print("In parseWorkMode...............")
        endc = wm["encoding"]
        dete = wm["detection"]
        if endc == "1" and dete == "1":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/ON)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/ON)}")
            self.userTextBrowserAppend("编码【开启】 检测【开启】")
        elif endc == "1" and dete == "0":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/ON)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/OFF)}")
            self.userTextBrowserAppend("编码【开启】 检测【关闭】")
        elif endc == "0" and dete == "1":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/OFF)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/ON)}")
            self.userTextBrowserAppend("编码【关闭】 检测【开启】")
        elif endc == "0" and dete == "0":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/OFF)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/OFF)}")
            self.userTextBrowserAppend("编码【关闭】 检测【关闭】")
            self.userTextBrowserAppend("无法进行【编码】和【检测】，请按下功能按键！")
    
    def getSelfCheckParameters(self):
        print("/*+++++++++++++++++++++++++++++++++++++++++++++*/")
        print("Checking device parameters ......")
        self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/NONE)}")
        self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/NONE)}")
        self.label_selfLineVoltage.setText("-")
        self.label_selfLineCurrent.setText("-")
        self.label_selfComVoltage.setText("-")
        self.label_selfComCurrent.setText("-")
        self.label_selfFireVoltage.setText("-")
        self.label_selfFireCurrent.setText("-")
        self.workMode = {"encoding": "X",  "detection": "X"} # 未知状态
        if self.protocolWin.prvSerial.isOpen:
            self.protocolWin.data = b''
            self.protocolWin.rxCheck = 0
            try:
                self.protocolWin.prvSerial.flush()
            except:
                pass
            self.protocolWin.serialSendData(Func.f_DevGetSelfPara, '', '')
            self.isDeviceResponsed = False
            self.devResponseTimer.start(3500)
        else:
            self.userTextBrowserAppend("串口未打开")
    
    def autoSendParameters(self):
        if len(self.protocolWin.comDescriptionList) != 0:
            if self.protocolWin.prvSerial.isOpen():
                self.thresholdWin.getUserPara()
                cnt = 0
                self.thresholdWin.para = ""
                for k, v in self.thresholdWin.paraDict.items():
                    if cnt < 10:
                        self.thresholdWin.para = self.thresholdWin.para + ("P" + str(cnt) + v)
                    elif cnt == 10:
                        self.thresholdWin.para = self.thresholdWin.para + ("PA" + v)
                    elif cnt == 0:
                        self.thresholdWin.para = self.thresholdWin.para + ("PB" + v)
                    elif cnt == 12:
                        self.thresholdWin.para = self.thresholdWin.para + ("PC" + v)
                    elif cnt == 13:
                        self.thresholdWin.para = self.thresholdWin.para + ("PD" + v)
                    elif cnt == 14:
                        self.thresholdWin.para = self.thresholdWin.para + ("PE" + v)
                    elif cnt == 15:
                        self.thresholdWin.para = self.thresholdWin.para + ("PF" + v)
                    cnt += 1
                if self.protocolWin.isAutoConnectDetectorOK == True: # 测试仪在线
                    self.thresholdWin.saveThreshold(self.thresholdWin.para)
        else:
            pass
        
    def parseGetSelfCheckParameters(self):
        self.setWorkMode(self.protocolWin.data)
        tmp = self.protocolWin.data.decode("utf-8")
        l = len(tmp)
        if tmp[3:10] != "NOPOWER":
            PwrVol  = tmp[tmp.find("V1", 0, l) + 2 : tmp.find("A1", 0, l)]
            PwrCur  = tmp[tmp.find("A1", 0, l) + 2 : tmp.find("V2", 0, l)]
            ComVol  = tmp[tmp.find("V2", 0, l) + 2 : tmp.find("A2", 0, l)]
            ComCur  = tmp[tmp.find("A2", 0, l) + 2 : tmp.find("V3", 0, l)]
            FireVol = tmp[tmp.find("V3", 0, l) + 2 : tmp.find("A3", 0, l)]
            FireCur = tmp[tmp.find("A3", 0, l) + 2 : tmp.find("M" , 0, l)]
            self.label_selfLineVoltage.setText(PwrVol)
            self.label_selfLineCurrent.setText(PwrCur)
            self.label_selfComVoltage.setText(ComVol)
            self.label_selfComCurrent.setText(ComCur)
            self.label_selfFireVoltage.setText(FireVol)
            self.label_selfFireCurrent.setText(FireCur)
            self.userTextBrowserAppend("已获取测试仪自检参数")
            self.parseWorkMode()
            self.enableFucnBtn()
            self.isDeviceResponsed = True
        else:
            self.userTextBrowserAppend("请接通测试仪电源")
    
    def parseSettingThreshold(self):
        tmp = self.protocolWin.data.decode("utf-8")
        res = tmp[3:(len(tmp)-4)]
        if res == "PARAOK":
            # self.sleepUpdate(2) 导致主窗口卡顿的地方
            if self.thresholdWin.isActiveWindow():
                self.thresholdWin.close()
            if self.powerOnParaTimer.isActive():
                self.powerOnParaTimer.stop()
            if self.startParaTimer.isActive():
                self.startParaTimer.stop()
            self.userTextBrowserAppend("测试仪接收参数成功")
        elif res == "PARAERR":
            self.userTextBrowserAppend("测试仪接收参数失败")
        elif res == "PARALESS":
            self.userTextBrowserAppend("测试仪接收参数缺失")

    def parseQueryCodeResults(self):
        tmp = self.protocolWin.data.decode("utf-8")
        self.queryCode = tmp[tmp.find("UID", 0, len(tmp)) + 3 : len(tmp) - 4]
        QApplication.processEvents()
        if self.queryCode == 'NODET':
            self.isModuleExist = False
            self.userTextBrowserAppend("无模块连接，请检查接线")
        else:
            if self.isPureQueryCode:
                self.isModuleExist = True
                self.userTextBrowserAppend("当前模块编号：" + self.queryCode)
            else:
                pass
        if self.encDetEncdetQue == 3 and self.isPureQueryCode == True:
            self.pushBtn_deviceEncoding.setEnabled(True)
            self.pushBtn_deviceDetection.setEnabled(True)
            self.pushBtn_deviceEncodingDetection.setEnabled(True)
            self.pushBtn_queryCode.setEnabled(True)
        self.isDeviceResponsed = True
        self.isPureQueryCode = None
        self.lineEdit_uidInput.setFocus()
     
    def parseEncodingResults(self):
        res = ""
        tmp = self.protocolWin.data.decode("utf-8")
        l = len(tmp)
        res = tmp[3:(len(tmp) - 4)]
        if tmp.find("UID", 3, l) != -1:
            if res == "UIDOK":
                self.isModuleExist = True
                if self.uid in self.devicesState:
                    self.devicesState[self.uid]['enc'] = True
                    self.updateDevicesStateFile()
                    self.isEncodeOK = True
                    self.userTextBrowserAppend("写入[" + self.uid + "]成功！")
            elif res == "UIDERR":
                self.isModuleExist = False
                self.devicesState[self.uid]['enc'] = False
                self.devicesState.pop(self.uid)
                self.isEncodeOK = False
                self.userTextBrowserAppend("写入[" + self.uid + "]失败，请重新写入或更换模块！")
        elif tmp.find("FACULTY", 3, l) != -1:
            self.isModuleExist = False
            self.isEncodeOK = False
            self.userTextBrowserAppend("模块已出故障，请检查连线或更换模块！")
            if self.uid in self.devicesState:
                self.devicesState.pop(self.uid)
        elif tmp.find("UIDNODE", 3, l) != -1:
            self.isModuleExist = False
        elif tmp.find("NCODE", 3, l) != -1:
            self.isEncodeOK = False
            self.workMode["encoding"] = "0"
            self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/close)}")
            self.userTextBrowserAppend("无法进行编码，请检查编码按键！")
        if self.encDetEncdetQue == 0:
            self.pushBtn_deviceEncoding.setEnabled(True)
            self.pushBtn_deviceDetection.setEnabled(True)
            self.pushBtn_deviceEncodingDetection.setEnabled(True)
            self.pushBtn_queryCode.setEnabled(True)
        self.lineEdit_uidInput.setFocus()

    def checkLVLC(self, rxData, UNOK):
        l = len(rxData)
        if UNOK == True:
            if rxData.find("LVER", 0, l) != -1 and rxData.find("LCER", 0, l) != -1:
                lv = rxData[rxData.find("LVER", 0, l) + 4 : rxData.find("LCER", 0, l)]
                lc = rxData[rxData.find("LCER", 0, l) + 4 : rxData.find("DA", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 超限，线路电流：" + lc + "mA 超限")
            elif rxData.find("LVOK", 0, l) != -1 and rxData.find("LCER", 0, l) != -1:
                lv = rxData[rxData.find("LVOK", 0, l) + 4 : rxData.find("LCER", 0, l)]
                lc = rxData[rxData.find("LCER", 0, l) + 4 : rxData.find("DA", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 正常，线路电流：" + lc + "mA 超限")
            elif rxData.find("LVER", 0, l) != -1 and rxData.find("LCOK", 0, l) != -1:
                lv = rxData[rxData.find("LVER", 0, l) + 4 : rxData.find("LCOK", 0, l)]
                lc = rxData[rxData.find("LCOK", 0, l) + 4 : rxData.find("DA", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 超限，线路电流：" + lc + "mA 正常")
            elif rxData.find("LVOK", 0, l) != -1 and rxData.find("LCOK", 0, l) != -1:
                lv = rxData[rxData.find("LVOK", 0, l) + 4 : rxData.find("LCOK", 0, l)]
                lc = rxData[rxData.find("LCOK", 0, l) + 4 : rxData.find("DA", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 正常，线路电流：" + lc + "mA 正常")
                self.isLVLCOK = True
        else:
            if rxData.find("LVER", 0, l) != -1 and rxData.find("LCER", 0, l) != -1:
                lv = rxData[rxData.find("LVER", 0, l) + 4 : rxData.find("LCER", 0, l)]
                lc = rxData[rxData.find("LCER", 0, l) + 4 : rxData.find("UNERROR", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 超限，线路电流：" + lc + "mA 超限")
            elif rxData.find("LVOK", 0, l) != -1 and rxData.find("LCER", 0, l) != -1:
                lv = rxData[rxData.find("LVOK", 0, l) + 4 : rxData.find("LCER", 0, l)]
                lc = rxData[rxData.find("LCER", 0, l) + 4 : rxData.find("UNERROR", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 正常，线路电流：" + lc + "mA 超限")
            elif rxData.find("LVER", 0, l) != -1 and rxData.find("LCOK", 0, l) != -1:
                lv = rxData[rxData.find("LVER", 0, l) + 4 : rxData.find("LCOK", 0, l)]
                lc = rxData[rxData.find("LCOK", 0, l) + 4 : rxData.find("UNERROR", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 超限，线路电流：" + lc + "mA 正常")
            elif rxData.find("LVOK", 0, l) != -1 and rxData.find("LCOK", 0, l) != -1:
                lv = rxData[rxData.find("LVOK", 0, l) + 4 : rxData.find("LCOK", 0, l)]
                lc = rxData[rxData.find("LCOK", 0, l) + 4 : rxData.find("UNERROR", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 正常，线路电流：" + lc + "mA 正常")
                self.resultList[0] = self.lineEdit_op_name.text()
                self.resultList[1] = self.detectionTime

    def drainWorkCurrentCheck(self, dawa):
        l = len(dawa)
        self.DA = dawa[dawa.find("DA", 0, l) + 2 : dawa.find("WA", 0, l)]
        if self.DA != '0':
            self.resultList[2] = self.DA[0 : len(self.DA) - 1] + "." + self.DA[len(self.DA)-1]
        else:
            self.resultList[2] = '0.0'
        self.WA = dawa[dawa.find("WA", 0, l) + 2 : dawa.find("UN" + self.uid, 0, l)]
        if self.WA != '0':             
            self.resultList[3] = self.WA[0 : len(self.WA) - 1] + "." + self.WA[len(self.WA)-1]
        else:
            self.resultList[3] = '0.0'
        if float(self.resultList[2]) <= float(self.thresholdWin.paraDict['th_DrainCurrent_Up']) and \
            float(self.resultList[3]) <= float(self.thresholdWin.paraDict['th_WorkCurrent_Up']):
            self.userTextBrowserAppend("漏电流：" + self.resultList[2] + "μA，工作电流：" + self.resultList[3] + "μA")
            self.detResCode[0] = 1
            self.detResCode[1] = 1
        elif float(self.resultList[2]) > float(self.thresholdWin.paraDict['th_DrainCurrent_Up']) and \
                float(self.resultList[3]) <= float(self.thresholdWin.paraDict['th_WorkCurrent_Up']):
            self.userTextBrowserAppend("漏电流：" + self.resultList[2] + "μA 超限，工作电流：" + self.resultList[3] + "μA")
            self.resultList[14] = '失败'
            self.detResCode[0] = 0
            self.detResCode[1] = 1
        elif float(self.resultList[2]) <= float(self.thresholdWin.paraDict['th_DrainCurrent_Up']) and \
                float(self.resultList[3]) > float(self.thresholdWin.paraDict['th_WorkCurrent_Up']):
            self.userTextBrowserAppend("漏电流：" + self.resultList[2] + "μA，" + self.resultList[3] + "μA 超限")
            self.resultList[14] = '失败'
            self.detResCode[0] = 1
            self.detResCode[1] = 0
        elif float(self.resultList[2]) > float(self.thresholdWin.paraDict['th_DrainCurrent_Up']) and \
                float(self.resultList[3]) > float(self.thresholdWin.paraDict['th_WorkCurrent_Up']):
            self.userTextBrowserAppend("漏电流：" + self.resultList[2] +  "μA 超限，工作电流：" + self.resultList[3] + "μA 超限")
            self.detResCode[0] = 0
            self.detResCode[1] = 0
            self.resultList[14] = '失败'

    def parseDetectionResults(self):
        self.resultList[0] = self.lineEdit_op_name.text()
        self.resultList[1] = self.detectionTime
        tmp = self.protocolWin.data.decode("utf-8")
        l = len(tmp)
        if tmp.find("UIDNODE", 0, l) != -1:
            self.userTextBrowserAppend("无模块连接，请检查接线")
            self.enableFucnBtn()
        else:
            if tmp.find("UNERROR", 0, l) != -1:
                self.resultList[4] = "失败"
                self.resultList[5] = "离线"
                self.resultList[6] = "-"
                self.resultList[7] = "-"
                self.resultList[8] = "-"
                self.resultList[9] = "-"
                self.resultList[14] = "失败"
                self.detResCode[2] = 0
                self.checkLVLC(tmp, False)
                if self.uid in self.devicesState:
                    self.devicesState.pop(self.uid)
                self.userTextBrowserAppend("编码核对失败，请检查输入编码！")
                self.enableFucnBtn()
            else:
                self.resultList[4] = "成功"
                self.checkLVLC(tmp, True)
                if self.isLVLCOK == True:
                    self.isLVLCOK = False
                    self.drainWorkCurrentCheck(tmp)
                    self.detResCode[2] = 1
                    if tmp.find("PIOK", 0, l) != -1:
                        if tmp.find("POOK", 0, l) != -1:
                            self.resultList[6] = tmp[tmp.find("UN",  0,  l) + 2 : tmp.find("PIOK", 0, l)] # UID
                            # 被测模块
                            if tmp.find("UNNON", 0, l) == -1:
                                if tmp.find("UNREC", 0, l) != -1:
                                    self.detResCode[3] = 1
                                    self.resultList[5] = "在线"
                                    fc = tmp[tmp.find("UNA", l - 10, l) + 3 : l - 4] # 引爆电流
                                    self.resultList[7] = fc
                                    fv = tmp[tmp.find("UNV", l - 20, l) + 3 : tmp.find("UNA", l - 10, l)] # 引爆电压
                                    self.detResCode[5] = 1
                                    self.resultList[8] = fv[0 : len(fv) - 1] + '.' + fv[len(self.DA) - 1]
                                    if float(fc) > float(self.thresholdWin.paraDict['th_FireCurrent_Down']) and float(fc) < float(self.thresholdWin.paraDict['th_FireCurrent_Up']):
                                        self.detResCode[4] = 1
                                        self.resultList[9] = "正常"
                                        self.resultList[14] = '通过'
                                        self.devicesState[self.uid]['det'] = True
                                        self.devicesState[self.uid]['res'] = self.resultList.copy()
                                    else:
                                        self.detResCode[4] = 0
                                        self.resultList[9] = "超限"
                                        self.resultList[14] = '失败'
                                        self.devicesState[self.uid]['det'] = False
                                        self.devicesState[self.uid]['res'] = self.resultList.copy()
                                elif tmp.find("UNREJ", 0, l) != -1:
                                    self.detResCode[3] = 1
                                    self.resultList[7] = "-"
                                    self.resultList[8] = "-"
                                    self.resultList[9] = "-"
                                    self.userTextBrowserAppend("被测模块确认引爆代码匹配失败")
                                    self.enableFucnBtn()
                                    self.resultList[14] = '失败'
                            elif tmp.find("UNNON", 0, l) != -1:
                                self.detResCode[3] = 0
                                self.resultList[5] = "离线"
                                self.resultList[7] = "-"
                                self.resultList[8] = "-"
                                self.resultList[9] = "-"
                                self.resultList[14] = '失败'
                                self.userTextBrowserAppend("引爆被测模块前无法检测到模块")
                                self.devicesState[self.uid]['det'] = False
                                self.devicesState[self.uid]['res'] = self.resultList.copy()
                            # 内置模块
                            if tmp.find("UFREC", 0, l) != -1:
                                self.detResCode[5] = 1
                                self.resultList[10] = tmp[tmp.find("POOKUF",   0, l) + 6 : tmp.find("UFRE", 0, l)]
                                if tmp.find("UNREC", 0, l) != -1:
                                    fci = tmp[tmp.find("UFA",  0, l) + 3 : tmp.find("UNREC", 0, l)] #引爆电流
                                elif tmp.find("UNNON", 0, l) != -1:
                                    fci = tmp[tmp.find("UFA",  0, l) + 3 : tmp.find("UNNON", 0, l)] #引爆电流
                                self.resultList[11] = fci
                                if float(fci) > float(self.thresholdWin.paraDict['th_FireCurrent_Down']) and float(fci) < float(self.thresholdWin.paraDict['th_FireCurrent_Up']):
                                    self.detResCode[6] = 1
                                    self.resultList[13] = "正常"
                                else:
                                    self.detResCode[6] = 0
                                    self.resultList[13] = "超限"
                                fvi = tmp[tmp.find("UFV",  0, l) + 3 : tmp.find("UFA", 0, l)]
                                self.resultList[12] = fvi[0 : len(fvi) - 1] + '.' + fvi[len(fvi) - 1]
                            elif tmp.find("UFREJ", 0, l) != -1:
                                self.detResCode[5] = 0
                                self.resultList[10] = tmp[tmp.find("UF",   0, l) + 2 : tmp.find("UFRE", 0, l)]
                                self.resultList[11] = "-"
                                self.resultList[12] = "-"
                                self.resultList[13] = "-"
                                self.resultList[14] = '失败'
                                self.userTextBrowserAppend("无法和内置模块通信，请检查接通下一级接线")
                        else:
                            self.detResCode[3] = 0
                            self.resultList[5] = "离线"
                            self.resultList[6] = "-"# UID
                            self.resultList[7] = "-"
                            self.resultList[8] = "-"
                            self.resultList[9] = "-"
                            # 结论
                            self.resultList[14] = '失败'
                            self.userTextBrowserAppend("断开火工，火工部存在, 被测模块火工部异常")
                    elif tmp.find("PIER", 0, l) != -1:
                        self.detResCode[3] = 0
                        self.resultList[4] = "失败"
                        self.resultList[5] = "离线"
                        self.resultList[6] = "-"
                        self.resultList[7] = "-"
                        self.resultList[8] = "-"
                        self.resultList[9] = "-"
                        self.devicesState[self.uid]['det'] = -1
                        # 结论
                        self.resultList[14] = '失败'
                        self.userTextBrowserAppend("接入火工，火工部不存在, 被测模块火工部异常")
                    s = 0
                    for t in range(len(self.detResCode)):
                        s = s + self.detResCode[t]
                    if s != 7:
                        self.resultList[14] = '失败'
                    self.devicesState[self.uid]['res'] = self.resultList.copy()
                    if self.detectionState == 1:
                        self.updateResultsFile(self.resultList)
                    elif self.detectionState == 2: # 已保存
                        self.changeResultsFile(self.uid)
                    rowcnt = self.tableViewModel.rowCount()
                    if rowcnt == 0: # 表格式图无显示数据
                        for col in range(15):
                            if col == 14:
                                item = QStandardItem(self.resultList[col][0:2])
                            else:
                                item = QStandardItem(self.resultList[col])
                            self.tableViewModel.setItem(self.tableRow, col, item)
                    else: # 表格式图已有显示数据
                        dupResRow = -1
                        for r in range(rowcnt):
                            if self.tableViewModel.item(r, 6).text() == self.resultList[6]: # 编码查重，发现当前记录和前一次记录重复，覆盖前一次记录即可
                                for i in range(15):
                                    if i != 14:
                                        self.tableViewModel.setItem(r, i, QStandardItem(self.resultList[i]))
                                    else:
                                        self.tableViewModel.setItem(r, i, QStandardItem(self.resultList[i][0:2]))
                                dupResRow = r
                        if dupResRow == -1: # 无重复检测记录
                            for col in range(15):
                                if col == 14:
                                    item = QStandardItem(self.resultList[col][0:2])
                                else:
                                    item = QStandardItem(self.resultList[col])
                                self.tableViewModel.setItem(rowcnt, col, item)
                            self.tableRow = rowcnt + 1
                        else:
                            self.tableRow = rowcnt
                    self.resultLastList = self.resultList.copy()
                    self.lineEdit_uidInput.clear()
                    self.updateDevicesStateFile()
                else:
                    pass
        self.enableFucnBtn()
        self.lineEdit_uidInput.setFocus()

    def updateDuplicateRow(self):
        rows = self.tableViewModel.rowCount()
        cols = self.tableViewModel.columnCount() 

    def saveDataOfView(self):
        rows = self.tableViewModel.rowCount()
        cols = self.tableViewModel.columnCount()
        self.openExcelRecord()
        if self.savedOrSavedAsClicked == True:
            self.excel.loadSheet(self.excelFilePath)
            self.showOperationFile(self.excelFilePath)
        elif self.savedOrSavedAsClicked == False:
            self.excel.loadSheet(self.excelAsFilePath)
            self.showOperationFile(self.excelAsFilePath)
        QApplication.processEvents()
        if rows != 0 and cols != 0:
            l = []
            self.savedOrSavedAsClicked = None
            for row in range(rows):
                l.clear()
                for col in range(cols):
                    index = self.tableViewModel.index(row, col)
                    Val = self.tableViewModel.data(index)
                    l.append(Val)
                if self.excel.updateCodeRowData(l[6], l) == True:
                    continue
                else:
                    self.excel.wrtieRow(l)
            self.excel.closeSheet()
            self.excel.saveSheet()
            self.saveExcelRecord()
            self.userTextBrowserAppend("保存数据记录表成功")
            return True
        else:
            self.userTextBrowserAppend("无检测结果，请进行检测！")
            self.pushBtn_saveResults.setEnabled(False)
            self.pushBtn_saveResultsAs.setEnabled(False)
            self.saveExcelRecord()
            return False

    def firstsaveResults(self):
        if not os.path.isfile(self.excelFilePath):
            if self.isExcelSavedFirst:
                # file = './recording'
                self.excelFilePath, isAccept =  QFileDialog.getSaveFileName(self, "保存检测结果", '', "recorded data(*.xlsx)")
                if isAccept:
                    if self.excelFilePath:
                        self.excelFile = os.path.split(self.excelFilePath)[1]
                        self.excel_sheet = "Sheet Of Records"
                        self.excel.initWorkBook(self.excelFile, self.excel_sheet)
                        self.excel.loadSheet(self.excelFile)
                        self.excel.wrtieRow(self.tableHeadline) # 添加表头
                        self.excel.saveSheet()
                        self.excel.closeSheet()
                        self.userTextBrowserAppend("创建数据记录表成功")
                        self.userTextBrowserAppend("@保存至\"" + str(self.excelFilePath) + "\"")
                        self.isExcelSavedFirst = False
                        self.isExcelSaved = True
                        self.saveExcelRecord()
                        self.openExcelRecord()
                        if self.saveDataOfView() == True:
                            self.userTextBrowserAppend("已保存" + str(self.tableViewModel.rowCount()) + "条数据记录，请进行下一次检测")
                            self.resultLastList = self.resultList.copy()
                            self.tableViewModel.removeRows(0, self.tableViewModel.rowCount()) # 清除表格视图
                            self.tableRow = 0
                            self.lineEdit_uidInput.setFocus() 
                            self.pushBtn_saveResults.setEnabled(False)
                            self.pushBtn_saveResultsAs.setEnabled(False)
                        self.showOperationFile(self.excelFilePath)
                    else:
                        pass
                self.saveExcelRecord()

    def saveResults(self):
        self.openExcelRecord()
        if os.path.isfile(self.excelFilePath):
            if self.saveDataOfView() == True:
                self.userTextBrowserAppend("已保存" + str(self.tableViewModel.rowCount()) + "条数据记录，请进行下一次检测")
                self.resultLastList = self.resultList.copy()
                self.tableViewModel.removeRows(0, self.tableViewModel.rowCount()) # 清除表格视图
                self.tableRow = 0
                self.lineEdit_uidInput.setFocus() 
                self.pushBtn_saveResults.setEnabled(False)
                self.pushBtn_saveResultsAs.setEnabled(False)
                self.showOperationFile(self.excelAsFilePath)
                self.isExcelSaved = True
        else:
            self.isExcelSavedFirst = True
            self.isExcelSaved = False
            self.showOperationFile('') 
            self.userTextBrowserAppend(self.excelFilePath + "文件已被删除或移动，请重新创建文件！")
        self.saveExcelRecord()

    def sleepUpdate(self, sec):
        cnt = 0
        while True:
            QApplication.processEvents()
            time.sleep(1)
            cnt = cnt + 1
            if cnt == sec:
                break

    def closeEvent(self, QCloseEvent):
        choice = QMessageBox.warning(self, "关闭程序", "是否退出程序？", QMessageBox.Yes | QMessageBox.Cancel)
        if choice == QMessageBox.Yes:
            QCloseEvent.accept()
            if self.protocolWin.prvSerial.isOpen():
                self.protocolWin.prvSerial.close()
            app = QApplication.instance()
            app.quit()
        elif choice == QMessageBox.Cancel:
            QCloseEvent.ignore()

if __name__ == "__main__":
    MainApp = QApplication(sys.argv)
    # MainApp.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainTerminal = MainWin()
    MainTerminal.show()
    sys.exit(MainApp.exec_()) 