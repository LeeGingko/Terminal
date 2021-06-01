# -*- coding: utf-8 -*-
from os import error
from UserImport import *

class MainWin(QtWidgets.QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        super(MainWin, self).__init__()  # 继承父类的所有属性
        # 获取程序当前工作路径
        self.currentWorkDirectory = ''
        self.currentWorkDirectory = os.getcwd()
        # 初始化UI
        self.initUi()

    def __del__(self):
        self.protocolWin.serialManager.wait()
        self.protocolWin.serialMonitor.wait()
        self.timsRefresh.wait()
        print("{} 退出主线程".format(__file__))

    def initUi(self):
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
        # 状态栏初始化
        self.myStatusBar = QStatusBar()
        self.myStatusBar.setFont(QFont("Times New Roman", 16, QFont.Light))
        self.setStatusBar(self.myStatusBar)
        # 消息提示窗口初始化
        self.textBrowser.setFontFamily("微软雅黑")
        self.textBrowser.setFontPointSize(14)
        # 自定义工具实例化
        self.usualTools = Tools()
        # 配置文件路径
        self.configFile = 'config.txt'
        self.configFilePath = os.path.join(self.currentWorkDirectory, self.configFile)
        # 模块状态记录
        self.devicesState = {}
        self.devicesStateFile = 'devicesState.txt'
        self.devicesStateFilePath = os.path.join(self.currentWorkDirectory, self.devicesStateFile) # 每获取一个编号，则存入到硬盘
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
        # 通信实例传入到全局对象，供阈值设置实例访问
        GetSetObj.set(self.protocolWin)
        self.protocolWin.serialManager.recvSignal.connect(self.serialRecvData)
        # 阈值设置界面类实例
        self.thresholdWin = ThresholdWin()
        self.thresholdWin.thresholdAppendSignal.connect(self.userTextBrowserAppend)
        # 工作模式初始化
        self.workMode = {"encoding": "X",  "detection": "X"} # 未知状态
        # 操作人员姓名录入
        self.is_name_input = False
        self.name = "操作员01" # 默认操作员姓名
        self.lineEdit_op_name.setText(self.name)
        # 自定义本地时间更新线程
        self.timsRefresh = LocalTimeThread()
        self.timsRefresh.secondSignal.connect(self.showDaetTime)
        self.timsRefresh.start()
        # 测试数据Excel文件保存变量的初始化
        self.excel = PrivateOpenPyxl() # Excel实例化全局对象
        self.isExcelSavedFirst = True # 是否是第一次保存Excel
        self.isExcelSaved = True # 是否是已经保存 Excel
        self.excelFilePath = "" # Excel文件路径
        self.excelFile = "" # Excel文件
        self.excelOpenState = False
        # 默认检测结果
        initTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.resultDefaultList = [
            "name",  initTime,    "F",    "F",   "失败",
            "离线",   "FFFFF",     "F",    "F",   "异常",
            "SSSSS",    "F",      "F",    "异常", "拒绝" ]
        # 测试检测结果，初始为默认检测结果
        self.resultList = self.resultDefaultList.copy()
        # 测试检测结果备份，进行重复检测结果判断
        self.resultLastList = self.resultList.copy()
        # 当前记录是否已经被保存，防止重复保存
        self.currentResultSaved = False 
        # 表格之模型、委托、视图初始化
        # 1 表格模型初始化
        self.tableRow = 0 # 填入表格的行数
        self.tableHeadline = [
            "测试员",   "时间",      "漏电流(uA)", "工作电流(uA)",  "ID核对",
            "在线检测", "被测选发",   "电流(mA)",   "电压(V)",      "电流判断",
            "内置选发", "电流(mA)",  "电压(V)",    "电流判断",      "结论" ]   
        self.tableViewModel = QStandardItemModel(0, 15, self)
        self.tableViewModel.setHorizontalHeaderLabels(self.tableHeadline) # 表头
        # 2 表格委托初始化
        self.tableViewDelegate = PrivateTableViewDelegate()
        # 3 表格视图初始化
        self.tableView_result.setModel(self.tableViewModel)
        self.tableView_result.horizontalHeader().setStretchLastSection(True)
        self.tableView_result.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView_result.setItemDelegate(self.tableViewDelegate)
        self.tableView_result.horizontalHeader().setFont(QFont("微软雅黑", 12, QFont.Light))
        self.tableView_result.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_result.verticalHeader().hide()
        self.tableView_result.setContextMenuPolicy(Qt.CustomContextMenu)
        # 3.1 表格视图上下文菜单
        self.tableView_result.customContextMenuRequested.connect(self.tvCustomContextMenuRequested)
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
        # 检测以及编码默认状态设置
        self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")
        self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")
        # UID输入验证器设置
        regValidator = QRegExpValidator(self)
        reg = QRegExp("[A-F0-9]+$") # 字母范围a~f, A~F, 数字0~9
        regValidator.setRegExp(reg)
        # UID输入编辑栏初始化
        self.lineEdit_uidInput.setMaxLength(5)
        self.lineEdit_uidInput.setValidator(regValidator)
        self.lineEdit_uidInput.setToolTip("字母范围A~F, 数字0~9")
        self.lineEdit_uidInput.setFocus()
        self.setMouseTracking(True)
        # 配置文件路径
        self.thresholdWin.configPath = self.configFilePath
        # 发送命令响应
        self.isDeviceResponsed = False
        # 检测状态
        self.detectionState = None # 未知状态
        ## 界面显示前初始化
        # 1 连接控制仪串口
        self.protocolWin.autoConnectDetector()
        # 2 下发参数阈值
        self.autoTimer = QTimer() # 使用定时器，防止主界面卡在步骤1中
        self.autoTimer.timeout.connect(self.autoSendParameters)
        self.autoTimer.start(2000) # 两秒后执行参数下发
        # 测试仪响应定时器
        self.devResponseTimer = QTimer()
        self.devResponseTimer.timeout.connect(self.deviceNoResponse)
        # 接通电源参数下发定时器
        self.paraTimer = QTimer() 
        self.paraTimer.timeout.connect(self.autoSendParameters)

    def showDaetTime(self, timeStr):
        self.myStatusBar.showMessage(timeStr)        
    
    def userTextBrowserAppend(self, str):
        t = self.usualTools.getTimeStamp()
        self.textBrowser.append(t + str)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)         
    
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
        if os.path.isfile(self.devicesStateFile): # 文件已存在
            pass
        else: # 创建文件
            try:
                with open(self.devicesStateFilePath, encoding="utf-8", mode="w") as sdsf:
                    sdsf.write(self.devicesState)
            except:
                pass
    
    def updateDevicesStateFile(self):
        with open(self.devicesStateFile, mode='wb') as sdsf:
            pk.dump(self.devicesState, sdsf)
        
    def loadDevicesStateFile(self):
        with open(self.devicesStateFile, mode='rb') as sdsf:
            r = pk.load(sdsf)
            # print(r)
        return r

    def createResultsFile(self):
        if os.path.isfile(self.resultsFile): # 文件已存在
            pass
        else: # 创建文件
            try:
                with open(self.resultsFilePath, encoding="utf-8", mode="w") as srfp:
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

    def isResultDetected(self, uid): # 当前模块检测结果是否保存
        s = self.loadResultsFile() # 返回list
        for res in s:
            if uid in res:
                return True, s.index(res)
        return None, None

    def changeResultsFile(self, uid): # 覆盖当前模块已保存的检测结果
        res = self.loadResultsFile() # 加载检测结果
        detSta, index = self.isResultDetected(uid)
        if detSta != None and index != None:
            res[index] = self.resultList.copy() # 覆盖检测结果
        with open(self.resultsFile, mode='w') as srf: # 修改内容后重新写入到检测结果文件
           srf.write(str(res))
           srf.flush() # 立即更新到硬盘
    
    def deviceNoResponse(self):
        if not self.isDeviceResponsed:
            self.userTextBrowserAppend("测试仪无响应，请执行操作")
        self.devResponseTimer.stop()    
    
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
            for n in self.tvRowList:
                self.tableViewModel.removeRow(n)
            self.tableRow = self.tableRow - l
            self.userTextBrowserAppend('删除选中数据')
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
    
    def isExcelResultsFileOpened(self):
        if os.path.exists('~$' + self.excelFile):
            # print('excel已被打开')
            return True
        else:
            # print('excel未被打开')
            return False

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
            self.userTextBrowserAppend("测试仪自检")
            self.selfCheckGetParameters()
            self.lineEdit_uidInput.setFocus()
        else:
            QMessageBox.information(self, "串口信息", "串口未打开\n请打开串口", QMessageBox.Yes)

    @QtCore.pyqtSlot()
    def on_pushBtn_clearUidInput_clicked(self):
        self.lineEdit_uidInput.clear()
    
    @QtCore.pyqtSlot()
    def on_pushBtn_queryCode_clicked(self):
        print("/*$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$*/")
        print("Querying......")
        self.userTextBrowserAppend("执行查询")
        if self.protocolWin.prvSerial.isOpen(): 
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
        self.protocolWin.prvSerial.flushOutput()
        self.protocolWin.serialSendData(Func.f_DevEncoding, uid, '')

    @QtCore.pyqtSlot()
    def on_pushBtn_deviceEncoding_clicked(self):
        if self.workMode["encoding"] == "1":
            print("/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/")
            print("Encoding......")
            self.userTextBrowserAppend("执行编码")
            if self.protocolWin.prvSerial.isOpen():
                self.uid = self.lineEdit_uidInput.text()
                if self.uid != "":
                    self.userTextBrowserAppend("输入编号：" + self.lineEdit_uidInput.text())
                    if not self.uid in self.devicesState:
                        self.devicesState[self.uid] = { 'enc':None, 'det':None, 'res':[] }
                        self.devicesState[self.uid]['enc'] = None
                        self.encoding(self.uid)
                    else:
                        if self.devicesState[self.uid].get('enc') == None: # 说明该编号在此次工作中未进行过编码
                            self.encoding(self.uid)
                        else: # 说明该编号在此次工作中已进行过编码
                            choice = QMessageBox.question(self, "执行编码", "覆盖模块编码？", QMessageBox.Yes | QMessageBox.Cancel)
                            if choice == QMessageBox.Yes:
                                self.encoding(self.uid)
                            else:
                                self.userTextBrowserAppend("取消覆盖模块编码")
                else:
                    self.userTextBrowserAppend("请输入编号！")
            else:
                self.userTextBrowserAppend("串口未打开")
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
        if self.workMode["detection"] == "1":
            print("/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/")
            print("Detecting......")
            self.userTextBrowserAppend("执行检测")
            if self.protocolWin.prvSerial.isOpen():
                self.uid = self.lineEdit_uidInput.text()
                if self.uid != "":
                    self.userTextBrowserAppend("输入编号：" + self.uid)
                    # if not self.uid in self.devicesState:
                    #     self.userTextBrowserAppend("该模块还未进行编码，请先执行编码！")
                    # else:
                    self.devicesState = self.loadDevicesStateFile()
                    detsta = self.devicesState[self.uid].get('det')
                    resSta, index = self.isResultDetected(self.uid)
                    if detsta == None and resSta == None: # 该模块在此次工作中未进行过检测
                        self.detection(self.uid)
                        self.detectionState = 1
                    elif (detsta == True or detsta == False) and (resSta == None and index == None): # 该模块在此次工作中已进行过检测，结果还未保存
                        choice = QMessageBox.question(self, "执行检测", "检测结果未保存，重新检测模块？", QMessageBox.Yes | QMessageBox.Cancel)
                        if choice == QMessageBox.Yes:
                            self.detection(self.uid)
                            self.detectionState = 2
                        else:
                            self.userTextBrowserAppend("取消重新检测")
                    elif (detsta == True or detsta == False) and (resSta != None and index != None): # 该模块在此次工作中已进行过检测，结果已经保存
                        choice = QMessageBox.question(self, "执行检测", "检测结果已保存，重新检测模块？", QMessageBox.Yes | QMessageBox.Cancel)
                        if choice == QMessageBox.Yes:
                            self.detection(self.uid)
                            self.detectionState = 3
                        else:
                            self.userTextBrowserAppend("取消重新检测")
                else:
                    self.userTextBrowserAppend("请输入编号！")
            else:
                self.userTextBrowserAppend("串口未打开")
        else:
            self.userTextBrowserAppend("检测【未开启】")
    
    def encodingDetection(self, uid):
        print("/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/")
        print("Encoding......")
        self.userTextBrowserAppend("执行编码")
        self.encoding(uid)
        while True:
            QApplication.processEvents()
            time.sleep(0.01)
            if self.protocolWin.data != b"":
                if self.protocolWin.data[2] != 50:
                    continue
                else:
                    break
        tmp = self.protocolWin.data.decode('utf-8')
        if tmp.find('UIDOK', 0, len(tmp)) != -1:
            print("/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/")
            print("Detecting......")
            self.userTextBrowserAppend("执行检测")
            self.detection(uid)
        else:
            self.userTextBrowserAppend("编码未通过，无法执行检测！")

    @QtCore.pyqtSlot()
    def on_pushBtn_deviceEncodingDetection_clicked(self):
        self.userTextBrowserAppend("执行编码和检测")
        if self.workMode["encoding"] == "1" and self.workMode["detection"] == "1":
            if self.protocolWin.prvSerial.isOpen():
                self.detectionTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                self.uid = self.lineEdit_uidInput.text()
                if self.uid != "":
                    self.userTextBrowserAppend("输入编号：" + self.lineEdit_uidInput.text())
                    if not self.uid in self.devicesState:
                        self.devicesState[self.uid] = { 'enc':None, 'det':None,'res':[]}
                        self.encodingDetection(self.uid)
                    else:
                        choice = QMessageBox.question(self, "执行编码及检测", "重新执行一键编码检测？", QMessageBox.Yes | QMessageBox.Cancel)
                        if choice == QMessageBox.Yes:
                            self.encodingDetection(self.uid)
                        else:
                            self.userTextBrowserAppend("取消执行一键编码检测")
                else:
                    self.userTextBrowserAppend("请输入编号！")
            else:
                self.userTextBrowserAppend("串口未打开")
        else:
            self.userTextBrowserAppend("编码和检测未开启") 

    @QtCore.pyqtSlot()
    def on_pushBtn_saveResults_clicked(self):
        self.openExcelRecord()
        self.excelOpenState = self.isExcelResultsFileOpened()
        if self.excelOpenState:
            self.userTextBrowserAppend(self.excelFilePath + '已被打开, 请关闭文件后再写入')
        else:
            if self.isExcelSavedFirst:
                self.firstsaveResults()
            elif self.isExcelSaved:
                self.saveResults()
        self.lineEdit_uidInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushBtn_saveResultsAs_clicked(self):
        self.openExcelRecord()
        self.excelOpenState = self.isExcelResultsFileOpened()
        if self.excelOpenState:
            self.userTextBrowserAppend(self.excelFilePath + '已被打开, 请关闭文件后再写入')
        else:
            if self.isExcelSavedFirst:
                self.firstsaveResults()
            elif self.isExcelSaved:
                self.saveResults()
        self.lineEdit_uidInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushBtn_showResults_clicked(self):
        isOpenState = self.isExcelResultsFileOpened()
        if isOpenState:
            self.userTextBrowserAppend(self.excelFilePath + '已打开')
        else:
            self.openExcelRecord()
            recordsfile, _ = QFileDialog.getOpenFileName(self, "打开记录文件", './', 'records (*.xlsx)')
            if recordsfile:
                os.startfile(recordsfile)
                self.isConfigSaved = True
            self.saveExcelRecord()   
        self.lineEdit_uidInput.setFocus()  

    @QtCore.pyqtSlot()
    def on_pushBtn_clearResults_clicked(self):
        self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())
        self.tableRow = 0
        self.lineEdit_uidInput.setFocus()
    
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
                        self.parseSelfCheckGetParameters()
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
            self.userTextBrowserAppend("测试仪已上电，线路供电接通")
            self.on_pushBtn_deviceSelfCheck_clicked() # 进行一次测试仪自检
            self.paraTimer.start(3000)
            # self.autoSendParameters() # 进行一次参数下发
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
                self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
                self.userTextBrowserAppend("编码发生改变，编码【关闭】")
            elif endc == "1":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
                self.userTextBrowserAppend("编码发生改变，编码【开启】")
        elif str[1] == "Y":
            if dete == "0":
                self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
                self.userTextBrowserAppend("检测发生改变，检测【关闭】")
            elif dete == "1":
                self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
                self.userTextBrowserAppend("检测发生改变，检测【开启】")
        elif str[1] == "Z":
            if endc == "1" and dete == "1":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
                self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
                self.userTextBrowserAppend("编码检测发生改变，编码【开启】 检测【开启】")
            elif endc == "1" and dete == "0":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
                self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
                self.userTextBrowserAppend("编码检测发生改变，编码【开启】 检测【关闭】")
            elif endc == "0" and dete == "1":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
                self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
                self.userTextBrowserAppend("编码检测发生改变，编码【关闭】 检测【开启】")
            elif endc == "0" and dete == "0":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
                self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
                self.userTextBrowserAppend("编码检测发生改变，编码【关闭】 检测【关闭】")

    def parseWorkMode(self):
        wm = self.getWorkMode()
        # print("In parseWorkMode...............")
        endc = wm["encoding"]
        dete = wm["detection"]
        if endc == "1" and dete == "1":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
            self.userTextBrowserAppend("编码【开启】 检测【开启】")
        elif endc == "1" and dete == "0":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
            self.userTextBrowserAppend("编码【开启】 检测【关闭】")
        elif endc == "0" and dete == "1":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
            self.userTextBrowserAppend("编码【关闭】 检测【开启】")
        elif endc == "0" and dete == "0":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
            self.userTextBrowserAppend("编码【关闭】 检测【关闭】")
            self.userTextBrowserAppend("无法进行【编码】和【检测】，请按下功能按键！")
    
    def selfCheckGetParameters(self):
        print("/*+++++++++++++++++++++++++++++++++++++++++++++*/")
        print("Checking device parameters ......")
        self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")
        self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")
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
            # self.protocolWin.prvSerial.flush()
            self.protocolWin.serialSendData(Func.f_DevGetSelfPara, '', '')
            self.isDeviceResponsed = False
            self.devResponseTimer.start(2000)
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
                    elif cnt == 11:
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
                # self.thresholdWin.openConfigRecord()
                # if self.thresholdWin.isConfigSavedFirst == True:
                self.thresholdWin.saveThreshold(self.thresholdWin.para)
                # elif self.thresholdWin.isConfigSaved:
                #     self.thresholdWin.settingThreshold()
            self.autoTimer.stop()
        else:
            pass
        
    def parseSelfCheckGetParameters(self):
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
            self.parseWorkMode()
            self.isDeviceResponsed = True
            self.userTextBrowserAppend("已获取测试仪自检参数")
        else:
            self.userTextBrowserAppend("请接通测试仪电源")      
    
    def parseSettingThreshold(self):
        tmp = self.protocolWin.data.decode("utf-8")
        res = tmp[3:(len(tmp)-4)]
        if res == "PARAOK":
            # self.sleepUpdate(2) 导致主窗口卡顿的地方
            if self.thresholdWin.isActiveWindow():
                self.thresholdWin.close()
            self.paraTimer.stop()
            self.userTextBrowserAppend("测试仪接收参数成功")
        elif res == "PARAERR":
            self.userTextBrowserAppend("测试仪接收参数失败")
        elif res == "PARALESS":
            self.userTextBrowserAppend("测试仪接收参数缺失")
        self.lineEdit_uidInput.setFocus()

    def parseQueryCodeResults(self):
        tmp = self.protocolWin.data.decode("utf-8")
        tmp = tmp[tmp.find("UID", 0, len(tmp)) + 3 : len(tmp) - 4]
        if tmp == 'NODET':
            self.userTextBrowserAppend("无模块连接")
        else:
            self.userTextBrowserAppend("当前模块编号：" + tmp)
        self.isDeviceResponsed = True
        self.lineEdit_uidInput.setFocus()
     
    def parseEncodingResults(self):
        res = ""
        tmp = self.protocolWin.data.decode("utf-8")
        l = len(tmp)
        res = tmp[3:(len(tmp) - 4)]
        if tmp.find("UID", 3, l) != -1:
            if res == "UIDOK":
                if self.uid in self.devicesState:
                    self.devicesState[self.uid]['enc'] = True
                    self.userTextBrowserAppend("写入UID成功！")
                    self.updateDevicesStateFile()
                    # time.sleep(1)
                    # self.loadDevicesStateFile()
            elif res == "UIDERR":
                self.devicesState[self.uid]['enc'] = False
                self.userTextBrowserAppend("写入UID失败，请重新写入或更换模块！")
                self.devicesState.pop(self.uid)
        elif tmp.find("FACULTY", 3, l) != -1:
            self.devicesState[self.uid]['enc'] = -1
            self.userTextBrowserAppend("模块已出故障，请检查连线或更换模块！")
            self.devicesState.pop(self.uid)
        elif tmp.find("NCODE", 3, l) != -1:
            self.workMode["encoding"] = "0"
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/close)}")
            self.userTextBrowserAppend("无法进行编码，请检查编码按键！")
        self.lineEdit_uidInput.setFocus()

    def parseDetectionResults(self):
        res = ""
        tmp = self.protocolWin.data.decode("utf-8")
        l = len(tmp)
        res = tmp[3:11]
        if tmp.find("OPENMULTIMETER", 0, l) != -1:
            self.userTextBrowserAppend("请打开电表RS232通信功能【REL △】,重新进行检测！")
            self.devicesState.pop(self.uid)
        else:
            if res == "LVERLCER":
                self.userTextBrowserAppend("线路电流超限，线路电压超限")
            elif res == "LVOKLCER":
                self.userTextBrowserAppend("线路电压正常，线路电流超限")
            elif res == "LVERLCOK":
                self.userTextBrowserAppend("线路电压超限，线路电流正常")
            elif res == "LVOKLCOK":
                self.userTextBrowserAppend("线路电压正常，线路电流正常")
                self.resultList[0] = self.lineEdit_op_name.text()
                self.resultList[1] = self.detectionTime
                if tmp.find("U1ERROR", 11, l) != -1:
                    self.userTextBrowserAppend("编码核对失败，请检查输入编码！")
                    self.devicesState.pop(self.uid)
                    self.lineEdit_uidInput.clear()
                else:
                    DA = tmp[tmp.find("DA", 11, l) + 2 : tmp.find("WA", 11, l)]
                    self.resultList[2] = DA[0 : len(DA) - 1] + "." + DA[len(DA)-1]
                    WA = tmp[tmp.find("WA", 11, l) + 2 : tmp.find("U1", 11, l)]
                    self.resultList[3] = WA[0 : len(WA) - 1] + "." + WA[len(WA)-1]
                    # 被测模块
                    if tmp[tmp.find("U1",  11, 25) + 2 : tmp.find("PIOK", 11, l)] != '':
                        self.resultList[4] = "成功"
                        if tmp[tmp.find("PIOK", 0, l)] != -1 and tmp[tmp.find("U1REC", 0, l)] != -1:
                            self.resultList[5] = "在线"
                            self.resultList[6] = tmp[tmp.find("U1",  11, 25) + 2 : tmp.find("PIOK", 11, l)] # UID
                            fc = tmp[tmp.find("U1A", l - 10, l) + 3 : l - 4] #引爆电流
                            self.resultList[7] = fc
                            fv = tmp[tmp.find("U1V", l - 20, l) + 3 : tmp.find("U1A", l - 10, l)] #引爆电压
                            self.resultList[8] = fv[0 : len(fv) - 1] + '.' + fv[len(DA) - 1]
                            if float(fc) > float(self.thresholdWin.paraDict['th_FireCurrent_Down']) and float(fc) < float(self.thresholdWin.paraDict['th_FireCurrent_Up']):
                                self.resultList[9] = "正常"
                                self.resultList[14] = "通过"
                                self.devicesState[self.uid]['det'] = True
                                self.devicesState[self.uid]['res'] = self.resultList.copy()
                            else:
                                self.resultList[9] = "超限"
                                self.resultList[14] = "未通过"
                                self.devicesState[self.uid]['det'] = False
                                self.devicesState[self.uid]['res'] = self.resultList.copy()
                        else:
                            self.resultList[5] = "离线"
                            self.resultList[6] = tmp[tmp.find("U1",  11, 25) + 2 : tmp.find("PIOK", 11, l)] # UID
                            self.resultList[7] = "-"
                            self.resultList[8] = "-"
                            self.resultList[9] = "-"
                    else:
                        self.resultList[4] = "失败"
                        self.resultList[5] = "离线"
                        self.devicesState[self.uid]['det'] = -1
                    # 内置模块
                    self.resultList[10] = tmp[tmp.find("U2",   11, l) + 2 : tmp.find("U2RE", 11, l)]
                    self.resultList[11] = tmp[tmp.find("U2A",  11, l) + 3 : tmp.find("U1RE", 11, l)]
                    iv = tmp[tmp.find("U2V",  11, l) + 3 : tmp.find("U2A", 11, l)]
                    self.resultList[12] = iv[0 : len(iv) - 1] + '.' + iv[len(iv) - 1]
                    self.resultList[13] = "正常"
                    self.devicesState[self.uid]['res'] = self.resultList.copy()
                    if self.detectionState == 1: # 未进行过检测，直接保存
                        # 直接更新model
                        for col in range(15):
                            item = QStandardItem(self.resultList[col])
                            self.tableViewModel.setItem(self.tableRow, col, item)
                        self.updateResultsFile(self.resultList)
                        self.detectionState = 2
                    elif self.detectionState == 2: # 未保存
                        # 更新model
                        for col in range(15):
                            item = QStandardItem(self.resultList[col])
                            self.tableViewModel.setItem(self.tableRow - 1, col, item)
                        self.updateResultsFile(self.resultList)
                        self.detectionState = 2
                    elif self.detectionState == 3: # 已保存
                        # 更新model
                        for col in range(15):
                            item = QStandardItem(self.resultList[col])
                            self.tableViewModel.setItem(self.tableRow - 1, col, item)
                        self.changeResultsFile(self.uid)
                    # self.detectionState = None
                    self.tableRow = self.tableRow + 1
                    
                    self.lineEdit_uidInput.clear()
            self.updateDevicesStateFile()
        self.lineEdit_uidInput.setFocus()

    def saveDataOfView(self):
        self.openExcelRecord()
        s = self.loadResultsFile()
        self.excel.loadSheet(self.excelFilePath)
        for i in range(len(s)):
            l = str(s[i])[1:len(s[i])-1].split(',')
            if not self.uid in l:
                self.excel.wrtieRow(l)
        self.excel.closeSheet()
        self.excel.saveSheet()
        self.saveExcelRecord()

    def firstsaveResults(self):
        if self.excelFilePath == "":
            file = './' + time.strftime("%Y年%m月%d日%H时%M分%S秒", time.localtime()) + '_recording'
            self.excelFilePath, isAccept =  QFileDialog.getSaveFileName(self, "保存检测结果", file, "recorded data(*.xlsx)")
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
                    self.isExcelSavedFirst = False
                    self.isExcelSaved = True
                    # res = self.compareResult()
                    # if res == 1:
                    self.isExcelSaved = True
                    self.currentResultSaved = True
                    self.saveDataOfView()
                    self.saveExcelRecord()
                    self.userTextBrowserAppend("@保存至\"" + str(self.excelFilePath) + "\"")
                    # elif res == 0:
                    #     self.userTextBrowserAppend("当前检测结果已记录，请重新进行编码和检测")  
                    # elif res == -1:
                    #     self.userTextBrowserAppend("未有检测结果，请进行编码和检测")
                    self.resultLastList = self.resultList.copy()
                    self.lineEdit_uidInput.setFocus()
                else:
                    pass
        else:
            pass

    def saveResults(self):
        self.openExcelRecord()
        self.isExcelSaved = True
        self.currentResultSaved = True
        self.saveDataOfView()
        self.saveExcelRecord()
        self.userTextBrowserAppend("保存数据记录表成功")
        self.resultLastList = self.resultList.copy()
        self.lineEdit_uidInput.setFocus()

    def openExcelRecord(self):
        try:
            with open("excel_save_record.txt", "rb") as esrf:
                oer = pk.load(esrf) # 将二进制文件对象转换成Python对象
            self.isExcelSavedFirst = oer[0][0]
            self.isExcelSaved = oer[0][1]
            self.excelFilePath = oer[1]
            self.excelFile = os.path.split(self.excelFilePath)[1]
        except:
            pass
    
    def saveExcelRecord(self):
        self.saved_info = ([self.isExcelSavedFirst, self.isExcelSaved],  self.excelFilePath)
        with open("excel_save_record.txt", "wb") as esrf:
            pk.dump(self.saved_info, esrf) # 用dump函数将Python对象转成二进制对象文件
        # print("saveExcelRecord:" + str(self.saved_info))

    def compareResult(self):
        diffDef = set(self.resultList).difference(set(self.resultDefaultList))
        diffDet = set(self.resultList).difference(set(self.resultLastList))
        if diffDef == set() and diffDet == set():
            return -1
        elif diffDef != set() and diffDet == set():
            return 0
        elif diffDef != set() and diffDet != set():
            return 1    
            
    def sleepUpdate(self, sec):
        cnt = 0
        while True:
            QApplication.processEvents()
            time.sleep(1)
            cnt = cnt + 1
            if cnt == sec:
                break

    def closeEvent(self, QCloseEvent):
        choice = QMessageBox.question(self, "关闭程序", "是否退出程序？", QMessageBox.Yes | QMessageBox.Cancel)
        if choice == QMessageBox.Yes:
            QCloseEvent.accept()
            app = QApplication.instance()
            app.quit()
        elif choice == QMessageBox.Cancel:
            QCloseEvent.ignore()

if __name__ == "__main__":
    MainApp = QApplication(sys.argv)
    MainApp.setWindowIcon(QIcon("./resources/icons/robot.ico"))
    MainTerminal = MainWin()
    MainTerminal.show()
    sys.exit(MainApp.exec_()) 