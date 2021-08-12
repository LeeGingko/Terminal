# -*- coding: utf-8 -*-
from UserImport import *


class MainWin(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MainWin, self).__init__()  # 继承父类的所有属性
        # 获取应用程序当前工作路径
        self.currentWorkDirectory = ''
        self.currentWorkDirectory = os.getcwd()
        self.configFolder = os.path.join(os.getcwd(), 'configurations')
        self.createConfigurationsFolder()
        # 初始化UI
        self.initUi()

    def __del__(self):
        self.protocolWin.serialManager.wait()
        self.protocolWin.serialMonitor.wait()
        self.timsRefresh.wait()
        print("{} 退出主线程".format(__file__))

    def initUi(self):
        # 初始化主窗口
        self.setupUi(self)
        # 设置窗口居中显示
        self.desktop = QApplication.desktop()
        self.screenCnt = self.desktop.screenCount()
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
        iconPath = os.path.join(self.currentWorkDirectory, './resources/icons/IDDD.ico')
        self.setWindowIcon(QIcon(iconPath))
        self.setIconSize(QSize(256, 256))
        self.geo = self.geometry()
        #*---------------------------------------------------------------------------------------------------------------*#
        self.switchInputMethod('English')
        # 状态栏初始化
        self.myStatusBar = QStatusBar()
        self.myStatusBar.setFont(QFont("Times New Roman", 16, QFont.Weight.Light))
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
        self.devicesStateFilePath = os.path.join(self.configFolder, self.devicesStateFile) # 每获取一个编号，则将其编码以及编码检测操作结果信息存入到硬盘
        # 检测结果记录存储文件，防止意外断电导致检测数据丢失
        self.resultsFile = 'results.txt'
        self.resultsFilePath = os.path.join(self.currentWorkDirectory, self.resultsFile)
        # 分别创建文件
        self.createConfigFile()
        self.createDevicesStateFile()
        self.createResultsFile()
        # 阈值设置界面类实例
        self.thresholdWin = ThresholdWin()
        self.thresholdWin.thresholdAppendSignal.connect(self.userTextBrowserAppend)
        self.thresholdWin.openFileSignal.connect(self.showOperationFile)
        # 阈值设置实例传入到全局对象，供通信设置实例访问
        GetSetObj.set(2, self.thresholdWin)        
        # 通信配置界面类实例
        self.protocolWin = ProtocolWin()
        self.protocolWin.protocolAppendSignal.connect(self.userTextBrowserAppend)
        # 串口通信实例传入到全局对象，供阈值设置实例访问
        GetSetObj.set(1, self.protocolWin)
        # 串口接收线程处理函数
        self.protocolWin.serialManager.recvSignal.connect(self.serialRecvData)
        # 工作模式初始化
        self.workMode = { "encoding": "X",  "detection": "X" } # 未知状态
        # 检测以及编码默认状态设置
        self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/NONE)}")
        self.label_detection.setStyleSheet("QLabel{border-image: url(./resources/icons/NONE)}")
        # 操作人员姓名录入
        self.name = "操作员007" # 默认操作员姓名
        nameRegValidator = QRegularExpressionValidator(self)
        nameReg = QRegularExpression("^(?![\\《\\》\\，\\、\\。\\；\\：\\‘\\’\\“\\”\\？\\【\\】\\（\\）\\-\\—])[a-zA-Z0-9\u4e00-\u9fa5]+$")
        nameRegValidator.setRegularExpression(nameReg)
        self.le_Name.setValidator(nameRegValidator)
        self.le_Name.setMaxLength(7)
        # 本地时间更新线程
        self.timsRefresh = LocalTimeThread()
        self.timsRefresh.secondSignal.connect(self.showDaetTime)
        self.timsRefresh.start()
        # 检测数据Excel文件初始化
        self.excel = PrivateOpenPyxl() # 实例化Excel对象
        self.isExcelSavedFirst = True # 是否是第一次保存Excel
        self.isExcelSaved = False # 是否是已经保存Excel
        self.excelFilePath = "" # Excel文件路径
        self.excelFile = "" # Excel文件
        self.excelOpenState = False
        # 另存为文件
        self.isExcelAsSavedFirst = True # 是否是第一次另存为Excel
        self.isExcelAsSaved = False # 是否是已经另存为Excel
        self.excelAsFilePath = "" # Excel另存为文件路径
        self.excelAsFile = "" # Excel另存为文件
        self.excelAsOpenState = False
        self.excelRecordFile = os.path.join(self.configFolder, 'excelSaveRecord.txt')
        self.createExcelRecordFile()
        # 默认检测结果
        initTime = time.strftime("%Y年%m月%d日 %H:%M:%S", time.localtime()) # 检测时间
        self.resultDefaultList = [
            "name",  initTime,
            "-",    "-",
            "失败", "离线",
            "EEEEE",   "-",     "-",    "-",
            "EEEEE",   "-",     "-",    "-", 
            '失败' ]
        # 检测结果，初始为默认检测结果
        self.resultList = self.resultDefaultList.copy()
        # 单次测试检测结果备份
        self.resultLastList = self.resultList.copy()
        #*------------------------------- 表格显示控件之模型、委托、视图初始化 MVC--------------------------------*#
        # 1 表格模型初始化
        self.tableViewModel = QStandardItemModel(0, 15, self)
        self.tableviewRowIndex = 0 # 表格视图写入数据行索引
        self.tableHeadline = [
            "检测员",   "检测时间",   "漏电流(μA)", "工作电流(μA)",  "ID核对",
            "在线检测", "被测选发",   "电流(mA)",   "电压(V)",      "电流判断",
            "内置选发", "电流(mA)",  "电压(V)",    "电流判断",      "结论" ]
        # tableHeadlineitem = QStandardItem(self.tableHeadline)
        # tableHeadlineitem.setBackground(QBrush(QColor(205, 0, 0)))
        # tableHeadlineitem.setFont(QFont("幼圆", 12, QFont.Light))
        self.tableViewModel.setHorizontalHeaderLabels(self.tableHeadline) # 设置表头
        # 2 表格委托初始化
        self.tableViewDelegate = PrivateTableViewDelegate()
        # 3 表格视图初始化
        self.tv_Results.setModel(self.tableViewModel)
        self.tv_Results.horizontalHeader().setStretchLastSection(True)
        self.tv_Results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tv_Results.setItemDelegate(self.tableViewDelegate)
        self.tv_Results.horizontalHeader().setFont(QFont("幼圆", 12, QFont.Light))
        self.tv_Results.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tv_Results.verticalHeader().hide()
        self.tv_Results.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tv_Results.setEditTriggers (QAbstractItemView.NoEditTriggers)
        # 3.1 表格视图上下文菜单
        self.tvMenu = QMenu(self.tv_Results)
        self.saveSelected = QAction()
        self.saveAll = QAction()
        self.dropSelected = QAction()
        self.dropAll = QAction()
        self.openFTP = QAction()
        self.saveSelected.setText('保存选中行')
        self.saveAll.setText('保存全部行')
        self.dropSelected.setText('删除选中行')
        self.dropAll.setText('删除全部行')
        self.openFTP.setText('打开FTP')
        self.saveSelected.triggered.connect(self.tvSaveSelected)
        self.saveAll.triggered.connect(self.tvSaveAll)
        self.dropSelected.triggered.connect(self.tvDropSelected)
        self.dropAll.triggered.connect(self.tvDropAll)
        self.openFTP.triggered.connect(self.tvOpenFTP)
        # self.tvMenu.addAction(self.saveSelected)
        # self.tvMenu.addAction(self.saveAll)
        self.tvMenu.addAction(self.dropSelected)
        # self.tvMenu.addAction(self.dropAll)
        self.tvMenu.addAction(self.openFTP)
        self.tv_Results.customContextMenuRequested.connect(self.tvCustomContextMenuRequested)
        #*------------------------------- 表格显示控件之模型、委托、视图初始化 MVC--------------------------------*#
        # 编码输入验证器设置
        regValidator = QRegularExpressionValidator(self)
        reg = QRegularExpression("[A-E0-9]+$") # 字母范围A~E, 数字0~9
        regValidator.setRegularExpression(reg)
        # UID输入编辑栏初始化
        self.le_Encoding.setMaxLength(10)
        self.le_Encoding.setValidator(regValidator)
        self.le_Encoding.setToolTip("字母范围A~E, 数字0~9")
        self.le_Encoding.setAttribute(Qt.WA_InputMethodEnabled, False) # UID输入框屏蔽中文输入法，解决扫描输入UID乱序问题
        self.le_Encoding.setFocus()
        # 配置文件路径
        self.thresholdWin.configPath = self.configFilePath
        # 检测状态
        self.detectionState = None # 未知状态
        # 确认检测完毕
        self.confirmDetection = False
        # 失能保存和另存为
        self.btn_SaveResults.setEnabled(False)
        self.btn_SaveResultsAs.setEnabled(False)
        # 查询命令返回编码
        self.queryCode = 'EEEEE'
        # 是否只是查询编码
        self.justQueryCode = None
        # 点击了保存还是另存为
        self.savedOrSavedAsClicked = None
        # 先加载保存记录
        self.loadExcelOperationRecord()
        # 是否是主窗口发起的自动参数下发
        self.isMainSendPara = True # 开启软件默认就是主窗口发送，无需关闭参数下发窗口
        # 1 搜索并连接控制仪串口
        self.disableBtnFunc()
        self.actTimer = QTimer.singleShot(100, self.protocolWin.autoConnectDetector)
        self.enableBtnFunc()
        self.le_Name.setFocus()
        self.isLVLCOK = False
        self.encDetEncdetQuery = 0 # 编码 检测 编码检测 查询 -> 0 1 2 3
        self.detResCode = [ -1, -1, -1, -1, -1, -1, -1] # 检测响应代码，均为1代表检测成功
        self.uidLengthCheckTimer = QTimer()
        self.uidLengthCheckTimer.timeout.connect(self.monitorInputUID)
        self.uidLengthCheckTimer.start(10)
        # FTP操作界面
        self.ftpStation = FTPStationlWin()
        GetSetObj.set(3, self.ftpStation)
        self.setMouseTracking(True)
   
    def showUiLocation(self):
        self.geo = self.geometry()
        # print('Location:X', self.geo.left(), 'Location:Y', self.geo.top())
        # print('Screen 0 Width:', self.desktop.screenGeometry(0).width(), 'Screen 0 Height:', self.desktop.screenGeometry(0).height())
        # print('Screen 1 Width:', self.desktop.screenGeometry(1).width(), 'Screen 1 Height:', self.desktop.screenGeometry(1).height())
        # print('ScreenNumber:', self.desktop.screenNumber(self))
        # print('PrimaryScreen:', self.desktop.primaryScreen())
        print('Available 0 Geometry:', self.desktop.availableGeometry(0).width(),self.desktop.availableGeometry(0).height(),)
        print('Available 1 Geometry:', self.desktop.availableGeometry(1).width(),self.desktop.availableGeometry(1).height(),)

    def switchInputMethod(self, lang='English'):
        LANG = {
            'Chinese': 0x0804,
            'English': 0x0409
        }
        hwnd = win32gui.GetForegroundWindow()
        language = LANG[lang]
        result = win32api.SendMessage(
            hwnd,
            WM_INPUTLANGCHANGEREQUEST,
            0,
            language
        )
        if not result:
            # print('设置' + lang + '键盘成功！')
            return True

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
            self.loadExcelOperationRecord()
        else:
            pass

    def loadExcelOperationRecord(self):
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
    
    def saveExcelOperationRecord(self):
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
    
    def loadResultsFile(self):  # 加载检测结果
        with open(self.resultsFile, mode='r') as srf:
            r = srf.readlines()
            return r

    def isResultDetected(self, s, uid): # 当前模块检测结果是否保存
        for res in s:
            if uid in res:
                return True, s.index(res)
        return None, None
   
    def updateResultsFile(self, list): # 直接写入检测结果到硬盘
        with open(self.resultsFile, mode='a') as srf:
            s = ",".join(list)
            srf.write(s + '\n')

    def changeResultsFile(self, uid): # 覆盖当前模块已保存的检测结果
        res = self.loadResultsFile() # 加载检测结果
        detSta, row = self.isResultDetected(res, uid)
        tmplist = self.resultList
        tmplist[14] = tmplist[14] + '\n'
        s = ','.join(tmplist)
        if detSta != None and row != None: # 发现有重复结果
            res[row] = s # 覆盖检测结果
        elif detSta == None and row == None:
            res.append(s)
        with open(self.resultsFile, mode='a+') as srf: # 修改内容后重新写入到检测结果文件
            srf.seek(0)
            srf.truncate()
            for t in range(len(res)):
                srf.write(res[t])
            srf.flush() # 立即更新到硬盘 
    
    def showOperationFile(self, path):
        self.pathLabel.setText("操作文件：" + path)

    def enableBtnFunc(self):
        self.btn_DeviceEncoding.setEnabled(True)
        self.btn_DeviceDetection.setEnabled(True)
        self.btn_DeviceEncodingDetection.setEnabled(True)
        self.btn_QueryCode.setEnabled(True)
        self.le_Encoding.setEnabled(True)
        self.le_Name.setEnabled(True)
        self.btn_ClearInputUid.setEnabled(True)
        self.btn_ProtocolSetting.setEnabled(True)
        self.btn_ThresholdSetting.setEnabled(True)
        self.btn_ControllerSelfCheck.setEnabled(True)
        self.le_Encoding.setFocus()

    def disableBtnFunc(self):
        self.btn_DeviceEncoding.setEnabled(False)
        self.btn_DeviceDetection.setEnabled(False)
        self.btn_DeviceEncodingDetection.setEnabled(False)
        self.btn_QueryCode.setEnabled(False)
        self.le_Encoding.setEnabled(False)
        self.le_Name.setEnabled(False)
        self.btn_ClearInputUid.setEnabled(False)
        self.btn_ProtocolSetting.setEnabled(False)
        self.btn_ThresholdSetting.setEnabled(False)
        self.btn_ControllerSelfCheck.setEnabled(False)

    def checkControllerState(self):
        self.protocolWin.prvSerial.write(bytes("Terminal\r\n", encoding="utf-8"))
        startTiming = dt.datetime.now()
        endTiming = startTiming
        while True: # 等待测试仪回应
            QApplication.processEvents()
            time.sleep(0.01)
            num = self.protocolWin.prvSerial.inWaiting()
            endTiming = dt.datetime.now()
            if (endTiming - startTiming).seconds <= 1:
                QApplication.processEvents()
                # print('endTiming - startTiming:' + str((endTiming - startTiming).seconds))
                if num >= 5:
                    data = self.protocolWin.prvSerial.read(num)
                    if data.decode("utf-8") == "STM32":
                        self.flushTheSerialBuffer()
                        return True
                elif (num >= 0 and num <= 4):
                    continue
            else:
                self.flushTheSerialBuffer()
                return False

#------------------------------------START--------------------数据显示上下文菜单------------------------------------START--------------------#      
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
        if self.tableViewModel.rowCount() != 0:
            if l != 0:
                if self.confirmDetection:
                    choice = QMessageBox.critical(self, "删除视图数据", "是否删除视图数据，此操作会造成数据丢失", QMessageBox.Yes | QMessageBox.Cancel)
                    if choice == QMessageBox.Yes:
                        self.tableviewRowIndex = self.tableViewModel.rowCount() - l
                        for n in self.tvRowList:
                            self.tableViewModel.removeRow(n)
                        # if self.tableviewRowIndex == -1:
                        #     self.tableviewRowIndex = 0
                        self.userTextBrowserAppend('删除' + str(l) + '条选中数据')
                        if self.tableViewModel.rowCount() == 0:
                            self.userTextBrowserAppend('已无显示数据')
                            self.confirmDetection = False
                            self.btn_SaveResults.setEnabled(False)
                            self.btn_SaveResultsAs.setEnabled(False)
                    else:
                        self.userTextBrowserAppend('取消删除数据')
                else:
                    self.userTextBrowserAppend('请确认检测完毕后决定是否删除数据')
            else:
                self.userTextBrowserAppend('请选中显示区域数据')
        else:
            self.userTextBrowserAppend('无显示数据，请进行检测')     
    
    def tvDropAll(self):
        if len(self.tvRowList) != 0:
            self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())
            self.userTextBrowserAppend('删除全部数据')
        else:
            self.userTextBrowserAppend('无显示数据，请选中数据显示区域或进行检测')

    def tvOpenFTP(self):
        if not self.ftpStation.isVisible():
            QMessageBox.about(self, "使用须知", "1、使用前请先选择服务类型\n2、当前版本下，服务类型选择后无法更改，请注意！\n3、请不要反复打开关闭服务")
            self.ftpStation.show()
            self.ftpStation.setWindowModality(Qt.WindowModality.ApplicationModal)
            # self.ftpStation.tbMessageAppend("使用须知\n1、使用前请先选择服务类型\n2、当前版本下，服务类型选择后无法更改，请注意！\n3、请不要反复打开关闭服务")
        else:
            QMessageBox.about(self, "FTP工具", "已打开FTP操作界面")

    def tvCustomContextMenuRequested(self, p):
        self.tvIndex = self.tv_Results.selectionModel().selectedRows()
        self.tvRowList = []
        for i in self.tvIndex:
            self.tvRowList.append(i.row())
        self.tvRowList.sort(key=int, reverse=True)
        print(self.tvRowList)
        self.tvMenu.exec_(self.tv_Results.mapToGlobal(p))
#------------------------------------END----------------------数据显示上下文菜单------------------------------------END----------------------#    

#------------------------------------START---------------------输入完成槽函数-----------------------------------START--------------------#       
    @QtCore.pyqtSlot()
    def on_le_Name_editingFinished(self):
        self.userTextBrowserAppend('操作员：' + self.le_Name.text())

    def monitorInputUID(self): # 输入字符监控
        l = len(self.le_Encoding.text())
        if l >= 6:
            print(self.le_Encoding.text())
            self.le_Encoding.setText(self.le_Encoding.text()[l-5:l])

    @QtCore.pyqtSlot()
    def on_le_Encoding_editingFinished(self):
        l = len(self.le_Encoding.text())
        self.userTextBrowserAppend('模块编码：' + self.le_Encoding.text()[l-5:l])
#------------------------------------END----------------------输入完成槽函数------------------------------------END----------------------#    

#------------------------------------START--------------------按钮槽函数------------------------------------START--------------------#
    @QtCore.pyqtSlot()
    def on_btn_ProtocolSetting_clicked(self): # 打开通信设置界面
        if not self.protocolWin.isVisible():
            self.protocolWin.show()
            self.le_Encoding.setFocus()
        else:
            QMessageBox.about(self, "通信设置", "已打开通信设置界面")

    @QtCore.pyqtSlot()
    def on_btn_ThresholdSetting_clicked(self): # 打开阈值设置界面
        if not self.protocolWin.isVisible():
            self.thresholdWin.show()
            self.le_Encoding.setFocus()
        else:
            QMessageBox.about(self, "阈值设置", "已打开阈值设置界面")

    def flushTheSerialBuffer(self): # 清除串口缓冲
        if self.protocolWin.prvSerial.isOpen():
            self.protocolWin.prvSerial.reset_output_buffer()
            self.protocolWin.prvSerial.reset_input_buffer()    
    
    def autoSendParameters(self): # 参数下发
        # print("In autoSendParameters...............")
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
                self.thresholdWin.saveThreshold(self.thresholdWin.para)
        else:
            pass

    def executeControllerSelfCheck(self): # 执行设备参数自检
        if self.protocolWin.prvSerial.isOpen() == True:
            self.protocolWin.comIndex = self.protocolWin.comDescriptionList.index(self.protocolWin.comDescription)
            self.portInfo = QSerialPortInfo(self.protocolWin.comPortList[self.protocolWin.comIndex].device)  # 该串口信息
            self.portStatus = self.portInfo.isBusy()  # 该串口状态
            if self.portStatus == True:  # 该串口空闲
                self.disableBtnFunc()
                self.userTextBrowserAppend("测试仪自检")
                if self.checkControllerState() == True:
                    self.getSelfCheckParameters()
                    QTimer.singleShot(3000, self.autoSendParameters)
                    self.le_Encoding.setFocus()
                else:
                    self.enableBtnFunc()
                    self.userTextBrowserAppend("测试仪无响应，请重新选择串口或检查连线！")
        else:
            QMessageBox.information(self, "串口信息", "串口未打开，请打开串口", QMessageBox.Yes)
    
    @QtCore.pyqtSlot()
    def on_btn_ControllerSelfCheck_clicked(self): # 槽：设备参数自检 
        self.executeControllerSelfCheck()

    @QtCore.pyqtSlot()
    def on_btn_ClearInputUid_clicked(self): # 清除输入编码
        self.le_Encoding.clear()
    
    def encodingFunc(self, uid): # 编码功能
        self.protocolWin.data = b''
        self.protocolWin.rxCheck = 0
        if self.protocolWin.prvSerial.isOpen():
            self.protocolWin.prvSerial.flushOutput()
        self.protocolWin.serialSendData(Func.f_DevEncoding, uid, '')

    def executeTheEncoding(self): # 执行编码
        if self.workMode["encoding"] == "1":
            print("/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/")
            print("Encoding......")
            self.userTextBrowserAppend("执行编码")
            if self.protocolWin.prvSerial.isOpen():
                name = self.le_Name.text()
                if name != '':
                    self.uid = self.le_Encoding.text()
                    if self.uid != '' and self.uid != '55555':
                        self.flushTheSerialBuffer()
                        self.userTextBrowserAppend("输入编码：" + self.le_Encoding.text())
                        if len(self.uid) == 5:
                            if self.checkControllerState() == True:
                                self.disableBtnFunc()
                                self.justQueryCode = True
                                self.protocolWin.serialSendData(Func.f_DevQueryCurrentCode, '', '')
                                QApplication.processEvents()
                                self.sleepUpdate(2)
                                QApplication.processEvents()
                                self.devicesState = self.loadDevicesStateFile()
                                if self.devicesState != None: # 检测记录不为空
                                    if self.uid in self.devicesState:
                                        if self.queryCode == self.uid: # 当前模块进行过编码，且输入编码和当前模块编码相同
                                            choice = QMessageBox.information(self, "执行编码", "覆盖模块编码？", QMessageBox.Yes | QMessageBox.Cancel)
                                            if choice == QMessageBox.Yes:
                                                self.encodingFunc(self.uid)
                                            else:
                                                self.enableBtnFunc()
                                                self.userTextBrowserAppend("取消覆盖模块编码")
                                        else:
                                            self.encodingFunc(self.uid)
                                    else:
                                        self.devicesState[self.uid] = { 'enc':None, 'det':None, 'res':[] }
                                        self.encodingFunc(self.uid)
                                else:
                                    self.devicesState = {}
                                    self.devicesState[self.uid] = { 'enc':None, 'det':None, 'res':[] }
                                    if self.queryCode == self.uid: # 当前模块进行过编码，输入的UID和当前模块UID相同
                                        choice = QMessageBox.information(self, "执行编码", "覆盖模块编码？", QMessageBox.Yes | QMessageBox.Cancel)
                                        if choice == QMessageBox.Yes:
                                            self.encodingFunc(self.uid)
                                        else:
                                            self.userTextBrowserAppend("取消覆盖模块编码")
                                            self.enableBtnFunc()
                                    else:
                                        self.encodingFunc(self.uid)
                            else:
                                self.userTextBrowserAppend("测试仪无响应，请重新选择串口或检查连线！")
                        elif len(self.uid) < 5:
                            self.userTextBrowserAppend("输入编码小于五位，请输入五位编码")
                    elif self.uid == '55555':
                        self.userTextBrowserAppend("此编号无法编码，请重新输入！")
                        self.le_Encoding.clear()
                    elif self.uid == '':
                        self.userTextBrowserAppend("请输入编码！")
                elif name == '':
                    self.userTextBrowserAppend("请输入姓名！")
            else:
                self.userTextBrowserAppend("串口未打开")
        elif self.workMode["encoding"] == "X":
            self.userTextBrowserAppend("编码【未知】")
        else:
            self.userTextBrowserAppend("编码【未开启】")

    @QtCore.pyqtSlot()
    def on_btn_DeviceEncoding_clicked(self): # 槽：编码按钮
        self.encDetEncdetQuery = 0
        self.executeTheEncoding()
    
    @QtCore.pyqtSlot()
    def on_btn_QueryCode_clicked(self): # 查询编码
        if self.protocolWin.prvSerial.isOpen() == True:
            print("/*$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$*/")
            print("Querying......")
            self.userTextBrowserAppend("执行查询")
            if self.checkControllerState() == True:
                self.disableBtnFunc()
                self.encDetEncdetQuery = 3
                self.justQueryCode = True
                self.protocolWin.data = b''
                self.protocolWin.rxCheck = 0
                self.protocolWin.prvSerial.flushOutput()
                self.protocolWin.serialSendData(Func.f_DevQueryCurrentCode, '', '')
            else:
                self.userTextBrowserAppend("测试仪无响应，请重新选择串口或检查连线！")
        else:
            self.userTextBrowserAppend("串口未打开")  

    def detectionFunc(self, uid): # 检测功能
        self.detectionTime = time.strftime("%Y年%m月%d日 %H:%M:%S", time.localtime()) # 检测时间
        self.resultList = [
            "name",  self.detectionTime,    "-",    "-",   "-",
            "-",   "EEEEE",     "-",    "-",   "-",
            "EEEEE",    "-",      "-",    "-", '-' ]
        self.protocolWin.data = b""
        self.protocolWin.rxCheck = 0
        if self.protocolWin.prvSerial.isOpen():
            self.protocolWin.prvSerial.flushOutput()
        self.protocolWin.serialSendData(Func.f_DevDetection, uid, '')

    def executeTheDetection(self): # 执行检测
        for t in range(len(self.detResCode)):
            self.detResCode[t] = -1
        if self.protocolWin.prvSerial.isOpen():
            self.protocolWin.prvSerial.reset_output_buffer()
        if self.workMode["detection"] == "1":
            self.isLVLCOK = False
            print("/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/")
            print("Detecting......")
            self.userTextBrowserAppend("执行检测")
            if self.protocolWin.prvSerial.isOpen():
                self.uid = self.le_Encoding.text()
                name = self.le_Name.text()
                if name != '':
                    if self.uid != '' and self.uid != '55555':
                        self.flushTheSerialBuffer()
                        if len(self.uid) == 5:
                            self.userTextBrowserAppend("输入编码：" + self.uid)
                            if self.checkControllerState() == True:
                                self.disableBtnFunc()
                                res = self.loadResultsFile() # 加载检测结果
                                resSta, index = self.isResultDetected(res, self.uid)
                                self.devicesState = self.loadDevicesStateFile()
                                if self.devicesState != None:
                                    if not self.uid in self.devicesState: # 还未进行过编码操作
                                        if resSta == None and index == None: # 确实未编码且未检测，必需先执行编码
                                            self.devicesState[self.uid] = { 'enc':None, 'det':None, 'res':[]}
                                            self.userTextBrowserAppend("该模块未编码，请执行编码！")
                                            self.enableBtnFunc()
                                    else: # 进行过编码，是否检测过未知
                                        detsta = self.devicesState[self.uid].get('det')
                                        if (detsta == None) and (resSta == None): # 该模块在此次工作中未进行过检测
                                            self.devicesState[self.uid]['det'] = None
                                            self.detectionFunc(self.uid)
                                            self.detectionState = 1
                                        elif (detsta == True or detsta == False) and (resSta != None and index != None): # 该模块在此次工作中已进行过检测，结果已经保存
                                            choice = QMessageBox.information(self, "执行检测", "已有检测结果，重新检测模块？", QMessageBox.Yes | QMessageBox.Cancel)
                                            if choice == QMessageBox.Yes:
                                                self.devicesState[self.uid]['det'] = None
                                                self.detectionFunc(self.uid)
                                                self.detectionState = 2                                        
                                            else:
                                                self.userTextBrowserAppend("取消重新检测")
                                                self.enableBtnFunc()
                                        elif (detsta == True) and (resSta == None): # 该模块在此次工作中未进行过检测
                                            self.detectionFunc(self.uid)
                                            self.detectionState = 1        
                                        elif (detsta == None) and (resSta == True): # 该模块在此次工作中未进行过检测
                                            self.detectionFunc(self.uid)
                                            self.detectionState = 1
                                else:
                                    self.devicesState = {}
                                    self.devicesState[self.uid] = { 'enc':None, 'det':None, 'res':[]}
                                    self.userTextBrowserAppend("未有任何模块编码，请执行编码！")
                                    self.enableBtnFunc()
                            else:
                                self.userTextBrowserAppend("测试仪无响应，请重新选择串口或检查连线！")
                        elif len(self.uid) < 5:
                            self.userTextBrowserAppend("输入编码小于五位，请输入五位编码")
                    elif self.uid == '55555':
                        self.le_Encoding.clear()
                        self.userTextBrowserAppend("此编号无法检测，请重新输入！")
                    elif self.uid == '':
                        self.userTextBrowserAppend("请输入编码！")
                elif name == '':
                    self.userTextBrowserAppend("请输入姓名！")
            else:
                self.userTextBrowserAppend("串口未打开")
        elif self.workMode["detection"] == "0":
            self.userTextBrowserAppend("检测【未开启】")
        elif self.workMode["detection"] == "X":
            self.userTextBrowserAppend("检测【未知】")        

    @QtCore.pyqtSlot()
    def on_btn_DeviceDetection_clicked(self): # 槽：检测按钮
        self.executeTheDetection()
    
    def executeEncodingDetection(self): # 执行编码检测
        self.executeTheEncoding()
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
            self.executeTheDetection()
        else:
            self.enableBtnFunc()
            self.userTextBrowserAppend("编码未通过，无法执行检测！")
    
    @QtCore.pyqtSlot()
    def on_btn_DeviceEncodingDetection_clicked(self): # 槽：一键编码检测按钮
        for t in range(len(self.detResCode)):
            self.detResCode[t] = -1
        self.encDetEncdetQuery = 2
        self.userTextBrowserAppend("执行编码和检测")
        if self.workMode["encoding"] == "1" and self.workMode["detection"] == "1":
            if self.protocolWin.prvSerial.isOpen():
                self.detectionTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                self.uid = self.le_Encoding.text()
                self.justQueryCode = False
                self.executeEncodingDetection()
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
    def on_btn_ConfirmDetection_clicked(self): # 确认检测完成
        if self.tableViewModel.rowCount() != 0:
            choice = QMessageBox.warning(self, "检测结果确认", "确认检测完毕？", QMessageBox.Yes | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                self.btn_SaveResults.setEnabled(True)
                self.btn_SaveResultsAs.setEnabled(True)
                self.confirmDetection = True
                self.userTextBrowserAppend("确认检测完成")
            else:
                self.userTextBrowserAppend("检测还未完成")
                self.confirmDetection = False
        else:
            self.userTextBrowserAppend('无显示数据，请进行检测')
    
    def saveDataOfView(self): # 保存视图检测结果
        rows = self.tableViewModel.rowCount()
        cols = self.tableViewModel.columnCount()
        if self.savedOrSavedAsClicked == True:
            self.excel.loadSheet(self.excelFilePath)
            self.showOperationFile(self.excelFilePath)
        elif self.savedOrSavedAsClicked == False:
            self.excel.loadSheet(self.excelAsFilePath)
            self.showOperationFile(self.excelAsFilePath)
        self.loadExcelOperationRecord()
        if rows != 0 and cols != 0:
            l = []
            self.savedOrSavedAsClicked = None
            for row in range(rows):
                l.clear()
                # 从视图中取出单行检测结果，保存时进行重复判断
                for col in range(cols):
                    index = self.tableViewModel.index(row, col)
                    Val = self.tableViewModel.data(index)
                    l.append(Val)
                self.excel.updateRowDataByUID(l)
            self.excel.saveSheet()
            self.excel.closeSheet()
            self.saveExcelOperationRecord()
            self.userTextBrowserAppend("保存数据记录表成功")
            return True
        elif rows == 0 and cols == 0:
            self.closeSheet()
            self.btn_SaveResults.setEnabled(False)
            self.btn_SaveResultsAs.setEnabled(False)
            self.saveExcelOperationRecord()
            self.userTextBrowserAppend("无检测结果，请进行检测！")
            return False

    def firstsaveResults(self): # 首次保存结果
        self.loadExcelOperationRecord()
        # if not os.path.isfile(self.excelFilePath):
        if self.isExcelSavedFirst:
            self.saveTime = time.strftime("%Y年%m月%d日_%H时%M分%S秒", time.localtime()) # 保存时间
            self.saveCnts = str(self.tableViewModel.rowCount()) # 保存条数
            self.saveFileName = self.saveTime + '_' + self.saveCnts + '条_' + self.le_Name.text()
            self.excelFilePath, isAccept =  QFileDialog.getSaveFileName(self, "保存检测结果", self.saveFileName, "recorded data(*.xlsx)")
            if isAccept:
                if self.excelFilePath:
                    self.excelFile = os.path.split(self.excelFilePath)[1]
                    if self.usualTools.isExcelFileOpen(self.excelFile) == False:
                        self.excel_sheet = "Sheet Of Records"
                        self.excel.initWorkBook(self.excelFile, self.excel_sheet)
                        self.excel.setStyledHeader(self.tableHeadline)
                        self.isExcelSavedFirst = False
                        self.isExcelSaved = True
                        self.saveExcelOperationRecord()
                        self.userTextBrowserAppend("创建数据记录表成功")
                        self.userTextBrowserAppend('@保存至\"' + str(self.excelFilePath) + '\"')
                        self.loadExcelOperationRecord()
                        if self.saveDataOfView() == True:
                            self.userTextBrowserAppend("已保存" + str(self.tableViewModel.rowCount()) + "条数据记录至[" + self.excelFile + "]，请进行下一次检测")
                            self.resultLastList = self.resultList.copy()
                            self.tableViewModel.removeRows(0, self.tableViewModel.rowCount()) # 清除表格视图
                            self.tableviewRowIndex = 0
                            self.confirmDetection = False
                            self.le_Encoding.setFocus() 
                            self.btn_SaveResults.setEnabled(False)
                            self.btn_SaveResultsAs.setEnabled(False)
                        self.showOperationFile(self.excelFilePath)
                    else:
                        self.userTextBrowserAppend(self.excelFile + "已被打开，无法保存，若要覆盖此文件，请先关闭")
                else:
                    self.userTextBrowserAppend("保存文件出错！")
        self.saveExcelOperationRecord()

    def saveResults(self): # 保存结果
        self.loadExcelOperationRecord()
        if os.path.isfile(self.excelFilePath):
            if self.saveDataOfView() == True:
                self.userTextBrowserAppend("已保存" + str(self.tableViewModel.rowCount()) + "条数据记录至[" + self.excelFile + "]，请进行下一次检测")
                self.resultLastList = self.resultList.copy()
                self.tableViewModel.removeRows(0, self.tableViewModel.rowCount()) # 清除表格视图
                self.tableviewRowIndex = 0
                self.confirmDetection = False
                self.le_Encoding.setFocus() 
                self.btn_SaveResults.setEnabled(False)
                self.btn_SaveResultsAs.setEnabled(False)
                self.showOperationFile(self.excelAsFilePath)
                self.isExcelSaved = True
        else:
            self.isExcelSavedFirst = True
            self.isExcelSaved = False
            self.showOperationFile('') 
            self.userTextBrowserAppend(self.excelFilePath + "文件已被【删除】或【移动】或【重命名】，请点击【保存】按钮重新创建文件！")
        self.saveExcelOperationRecord()

    @QtCore.pyqtSlot()
    def on_btn_SaveResults_clicked(self): # 保存检测结果
        self.savedOrSavedAsClicked = True
        self.loadExcelOperationRecord()
        sta = self.usualTools.isExcelFileOpen(self.excelFile)
        if sta == True:
            self.userTextBrowserAppend(self.excelFile + '已被打开, 请关闭文件后再写入')
        else:
            if self.tableViewModel.rowCount() != 0:
                if (self.isExcelSavedFirst == True) and (self.isExcelSaved == False):
                    self.firstsaveResults()
                elif (self.isExcelSavedFirst == False) and (self.isExcelSaved == True):
                    self.saveResults()
                self.showOperationFile(self.excelFilePath) 
            else:
                self.userTextBrowserAppend('无显示数据，请进行检测')
        self.le_Encoding.setFocus()

    @QtCore.pyqtSlot()
    def on_btn_SaveResultsAs_clicked(self): # 另存检测结果
        if self.tableViewModel.rowCount() != 0:
            self.savedOrSavedAsClicked = False
            self.saveTime = time.strftime("%Y年%m月%d日_%H时%M分%S秒", time.localtime()) # 保存时间
            self.saveCnts = str(self.tableViewModel.rowCount()) # 保存条数
            self.saveFileName = self.saveTime + '_' + self.saveCnts + '条_' + self.le_Name.text()
            self.excelAsFilePath, isAccept =  QFileDialog.getSaveFileName(self, "保存检测结果另存为", self.saveFileName, "recorded data(*.xlsx)")
            if isAccept:
                if self.excelAsFilePath:
                    if not self.usualTools.isExcelFileOpen(self.excelAsFile):
                        self.excelAsFile = os.path.split(self.excelAsFilePath)[1]
                        self.saveExcelOperationRecord()
                        self.excel_sheet = "Sheet Of Records"
                        self.excel.initWorkBook(self.excelAsFile, self.excel_sheet)
                        self.excel.setStyledHeader(self.tableHeadline)
                        self.userTextBrowserAppend("创建数据记录表成功")
                        self.userTextBrowserAppend("@保存至\"" + str(self.excelAsFilePath) + "\"")
                        self.loadExcelOperationRecord()
                        if self.saveDataOfView() == True:
                            self.userTextBrowserAppend("已保存" + str(self.tableViewModel.rowCount()) + "条数据记录至[" + self.excelAsFile + "]，请进行下一次检测")
                            self.resultLastList = self.resultList.copy()
                            self.tableViewModel.removeRows(0, self.tableViewModel.rowCount()) # 清除表格视图
                            self.tableviewRowIndex = 0
                            self.btn_SaveResults.setEnabled(False)
                            self.btn_SaveResultsAs.setEnabled(False)
                    else:
                        self.userTextBrowserAppend(self.excelAsFile + '已被打开, 请关闭文件后再写入')
                    self.showOperationFile(self.excelAsFilePath)
                else:
                    self.userTextBrowserAppend("保存文件出错！")
            else:
                self.userTextBrowserAppend("取消保存当前记录")
        else:
                self.userTextBrowserAppend('无显示数据，请进行检测')
        self.le_Encoding.setFocus()

    @QtCore.pyqtSlot()
    def on_btn_ShowResults_clicked(self): # 查看Excel表格
        self.loadExcelOperationRecord()
        recordsfile, _ = QFileDialog.getOpenFileName(self, "打开记录文件", './', 'records (*.xlsx)')
        if recordsfile:
            self.showOperationFile(recordsfile)
            os.startfile(recordsfile)
        self.saveExcelOperationRecord()
        self.le_Encoding.setFocus()

    @QtCore.pyqtSlot()
    def on_btn_ClearResults_clicked(self): # 清除检测结果
        if self.tableViewModel.rowCount() != 0:
            if self.confirmDetection:
                choice = QMessageBox.critical(self, "清除结果", "清除检测结果？", QMessageBox.Yes | QMessageBox.Cancel)
                if choice == QMessageBox.Yes:
                    self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())
                    self.tableviewRowIndex = 0
                    self.confirmDetection = False
                    self.btn_SaveResults.setEnabled(False)
                    self.btn_SaveResultsAs.setEnabled(False)
                    self.le_Encoding.setFocus()
                else:
                    self.userTextBrowserAppend("取消清除检测结果")
            else:
                self.userTextBrowserAppend('请确认检测完毕后决定是否删除数据')
        else:
            self.userTextBrowserAppend('无显示数据，请进行检测')
        
    @QtCore.pyqtSlot()
    def on_btn_ClearMsgArea_clicked(self): # 清除消息提示框
        if self.textBrowser.toPlainText() != "":
            self.textBrowser.clear()
#------------------------------------END----------------------按钮槽函数------------------------------------END----------------------#
 
#------------------------------------START--------------------数据解析------------------------------------START--------------------#
    def serialRecvData(self, data): # 串口接收数据处理
        self.protocolWin.data = data
        if data.decode("utf-8") == "接收数据失败":
            self.userTextBrowserAppend("接收数据失败")
        else:
            tmp = data.decode("utf-8") # tmp[0] 帧头，帧功能
            if tmp[0] == "U":
                if self.protocolWin.rxFrameCheck() == State.s_RxFrameCheckOK:
                    if tmp[2] == Func.f_DevSettingThreshold:
                        self.parseSettingThreshold()
                    elif tmp[2] == Func.f_DevGetSelfPara:
                        self.parseControllerSelfCheck()
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
        self.flushTheSerialBuffer()
    
    def reportSystemPower(self, str): # 电源接通响应，设备自检
        print("In reportSystemPower...............")
        if str == "RMPO\r\n":
            # self.enableBtnFunc()
            self.userTextBrowserAppend("测试仪已上电，线路供电接通")
            self.executeControllerSelfCheck() # 进行一次测试仪自检
        elif str == "RMPE\r\n":
            self.userTextBrowserAppend("测试仪已上电，线路供电断开") # 电源断开，JLink连接时才会出现此回应
   
    def setWorkMode(self, tmp): # 设置工作模式
        self.workMode["encoding" ] = "0" if tmp[len(tmp) - 6] == 48 else "1"
        self.workMode["detection"] = "0" if tmp[len(tmp) - 5] == 48 else "1"

    def getWorkMode(self): # 获取工作模式
        return self.workMode
    
    def updateWorkMode(self, str): # 更新工作模式
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

    def parseWorkMode(self): # 解析工作模式
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
    
    def getSelfCheckParameters(self): # 获取自检参数
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
        else:
            self.userTextBrowserAppend("串口未打开")
          
    def parseControllerSelfCheck(self): # 解析设备自检参数
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
            self.userTextBrowserAppend("已获取测试仪自检参数")
        else:
            self.userTextBrowserAppend("请接通测试仪电源")
        self.enableBtnFunc()
        self.flushTheSerialBuffer()
    
    def parseSettingThreshold(self): # 解析阈值设置结果
        tmp = self.protocolWin.data.decode("utf-8")
        res = tmp[3:(len(tmp)-4)]
        if res == "PARAOK":
            if self.isMainSendPara == False:
                if self.thresholdWin.isVisible():
                    self.thresholdWin.close()
            else:
                self.isMainSendPara = False
            self.userTextBrowserAppend("测试仪接收参数成功")
        elif res == "PARAERR":
            self.userTextBrowserAppend("测试仪接收参数失败")
        elif res == "PARALESS":
            self.userTextBrowserAppend("测试仪接收参数缺失")
        self.flushTheSerialBuffer()

    def parseQueryCodeResults(self): # 解析查询结果
        tmp = self.protocolWin.data.decode("utf-8")
        self.queryCode = tmp[tmp.find("UID", 0, len(tmp)) + 3 : len(tmp) - 4]
        if self.queryCode == 'NODET':
            self.enableBtnFunc()
            self.userTextBrowserAppend("无模块连接，请检查接线")
            self.justQueryCode = None
            self.le_Encoding.setFocus()
        else:
            if self.queryCode != '55555':
                self.userTextBrowserAppend("当前模块编号：" + self.queryCode)
        if self.encDetEncdetQuery == 3 and self.justQueryCode == True:
            self.enableBtnFunc()
        self.justQueryCode = None
        self.flushTheSerialBuffer()
        self.le_Encoding.setFocus()
     
    def parseEncodingResults(self): # 解析编码结果
        res = ""
        tmp = self.protocolWin.data.decode("utf-8")
        l = len(tmp)
        res = tmp[3:(len(tmp) - 4)]
        if tmp.find("UID", 3, l) != -1:
            if res == "UIDOK":
                if self.uid in self.devicesState:
                    self.devicesState[self.uid]['enc'] = True
                    self.userTextBrowserAppend("写入[" + self.uid + "]成功！")
            elif res == "UIDERR":
                self.devicesState[self.uid]['enc'] = False
                self.devicesState.pop(self.uid)
                self.enableBtnFunc()
                self.userTextBrowserAppend("写入[" + self.uid + "]失败，请重新写入或更换模块！")
        elif tmp.find("FACULTY", 3, l) != -1:
            self.userTextBrowserAppend("模块已出故障，请检查连线或更换模块！")
            if self.uid in self.devicesState:
                self.devicesState.pop(self.uid)
            self.enableBtnFunc()
        elif tmp.find("UIDNODET", 3, l) != -1:
            self.userTextBrowserAppend("无模块连接！")
        elif tmp.find("NCODE", 3, l) != -1:
            self.workMode["encoding"] = "0"
            self.label_encoding.setStyleSheet("QLabel{border-image: url(./resources/icons/close)}")
            self.userTextBrowserAppend("无法进行编码，请检查编码按键！")
        if self.encDetEncdetQuery == 0:
            self.enableBtnFunc()
        self.updateDevicesStateFile()
        self.flushTheSerialBuffer()
        self.le_Encoding.setFocus()

    def lineVoltageCurrentCheck(self, rxData, codeCheckOK): # 线路电压电流判断
        l = len(rxData)
        if codeCheckOK == True: # 编码核对成功
            if (rxData.find("LVER", 0, l) != -1) and (rxData.find("LCER", 0, l) != -1):
                lv = rxData[rxData.find("LVER", 0, l) + 4 : rxData.find("LCER", 0, l)]
                lc = rxData[rxData.find("LCER", 0, l) + 4 : l - 4]
                self.userTextBrowserAppend("线路电压：" + lv + "V 超限，线路电流：" + lc + "mA 超限")
            elif (rxData.find("LVOK", 0, l) != -1) and (rxData.find("LCER", 0, l) != -1):
                lv = rxData[rxData.find("LVOK", 0, l) + 4 : rxData.find("LCER", 0, l)]
                lc = rxData[rxData.find("LCER", 0, l) + 4 : l - 4]
                self.userTextBrowserAppend("线路电压：" + lv + "V 正常，线路电流：" + lc + "mA 超限")
            elif (rxData.find("LVER", 0, l) != -1) and (rxData.find("LCOK", 0, l) != -1):
                lv = rxData[rxData.find("LVER", 0, l) + 4 : rxData.find("LCOK", 0, l)]
                lc = rxData[rxData.find("LCOK", 0, l) + 4 : l - 4]
                self.userTextBrowserAppend("线路电压：" + lv + "V 超限，线路电流：" + lc + "mA 正常")
            elif (rxData.find("LVOK", 0, l) != -1) and (rxData.find("LCOK", 0, l) != -1):
                lv = rxData[rxData.find("LVOK", 0, l) + 4 : rxData.find("LCOK", 0, l)]
                lc = rxData[rxData.find("LCOK", 0, l) + 4 : rxData.find("DA", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 正常，线路电流：" + lc + "mA 正常")
                self.isLVLCOK = True
        else:
            if (rxData.find("LVER", 0, l) != -1) and (rxData.find("LCER", 0, l) != -1):
                lv = rxData[rxData.find("LVER", 0, l) + 4 : rxData.find("LCER", 0, l)]
                lc = rxData[rxData.find("LCER", 0, l) + 4 : rxData.find("UNERROR", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 超限，线路电流：" + lc + "mA 超限")
            elif (rxData.find("LVOK", 0, l) != -1) and (rxData.find("LCER", 0, l) != -1):
                lv = rxData[rxData.find("LVOK", 0, l) + 4 : rxData.find("LCER", 0, l)]
                lc = rxData[rxData.find("LCER", 0, l) + 4 : rxData.find("UNERROR", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 正常，线路电流：" + lc + "mA 超限")
            elif (rxData.find("LVER", 0, l) != -1) and (rxData.find("LCOK", 0, l) != -1):
                lv = rxData[rxData.find("LVER", 0, l) + 4 : rxData.find("LCOK", 0, l)]
                lc = rxData[rxData.find("LCOK", 0, l) + 4 : rxData.find("UNERROR", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 超限，线路电流：" + lc + "mA 正常")
            elif (rxData.find("LVOK", 0, l) != -1) and (rxData.find("LCOK", 0, l) != -1):
                lv = rxData[rxData.find("LVOK", 0, l) + 4 : rxData.find("LCOK", 0, l)]
                lc = rxData[rxData.find("LCOK", 0, l) + 4 : rxData.find("UNERROR", 0, l)]
                self.userTextBrowserAppend("线路电压：" + lv + "V 正常，线路电流：" + lc + "mA 正常")

    def drainWorkCurrentCheck(self, dawa): # 漏电流工作电流判断
        self.DA = ''
        self.WA = ''
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
        if (float(self.resultList[2]) <= float(self.thresholdWin.paraDict['th_DrainCurrent_Up']))and \
           (float(self.resultList[3]) <= float(self.thresholdWin.paraDict['th_WorkCurrent_Up'])):
            self.userTextBrowserAppend("漏电流：" + self.resultList[2] + "μA，工作电流：" + self.resultList[3] + "μA")
            self.detResCode[0] = 1
            self.detResCode[1] = 1
        elif (float(self.resultList[2]) >  float(self.thresholdWin.paraDict['th_DrainCurrent_Up'])) and \
             (float(self.resultList[3]) <= float(self.thresholdWin.paraDict['th_WorkCurrent_Up'])):
            self.userTextBrowserAppend("漏电流：" + self.resultList[2] + "μA 超限，工作电流：" + self.resultList[3] + "μA")
            self.detResCode[0] = 0
            self.detResCode[1] = 1
        elif (float(self.resultList[2]) <= float(self.thresholdWin.paraDict['th_DrainCurrent_Up'])) and \
             (float(self.resultList[3]) >  float(self.thresholdWin.paraDict['th_WorkCurrent_Up'])):
            self.userTextBrowserAppend("漏电流：" + self.resultList[2] + "μA，" + self.resultList[3] + "μA 超限")
            self.detResCode[0] = 1
            self.detResCode[1] = 0
        elif (float(self.resultList[2]) > float(self.thresholdWin.paraDict['th_DrainCurrent_Up'])) and \
             (float(self.resultList[3]) > float(self.thresholdWin.paraDict['th_WorkCurrent_Up'])):
            self.userTextBrowserAppend("漏电流：" + self.resultList[2] +  "μA 超限，工作电流：" + self.resultList[3] + "μA 超限")
            self.detResCode[0] = 0
            self.detResCode[1] = 0

    def markAndShowTheResults(self, col): # 标记检测项
        if col != 14:
            item = QStandardItem(self.resultList[col])
            if self.resultList[col] == '成功':
                item.setForeground(QBrush(QColor(0, 0, 255)))
            elif self.resultList[col] == '失败':
                item.setForeground(QBrush(QColor(255, 0, 0)))
            if self.resultList[col] == '在线':
                item.setForeground(QBrush(QColor(0, 0, 255)))
            elif self.resultList[col] == '离线':
                item.setForeground(QBrush(QColor(255, 0, 0)))
            if self.resultList[col] == '正常':
                item.setForeground(QBrush(QColor(0, 0, 255)))
            elif self.resultList[col] == '超限':
                item.setForeground(QBrush(QColor(255, 0, 0)))
            if col == 2 and self.resultList[col] != '-':
                if float(self.resultList[col]) > float(self.thresholdWin.paraDict['th_DrainCurrent_Up']):
                    item.setForeground(QBrush(QColor(255, 0, 0)))
                elif float(self.resultList[col]) < float(self.thresholdWin.paraDict['th_DrainCurrent_Up']):
                    item.setForeground(QBrush(QColor(0, 0, 255)))
            elif col == 3 and self.resultList[col] != '-':
                if float(self.resultList[col]) > float(self.thresholdWin.paraDict['th_WorkCurrent_Up']):
                    item.setForeground(QBrush(QColor(255, 0, 0)))
                elif float(self.resultList[col]) < float(self.thresholdWin.paraDict['th_WorkCurrent_Up']):
                    item.setForeground(QBrush(QColor(0, 0, 255)))
            elif col == 7 and self.resultList[col] != '-':
                if float(self.resultList[col]) > float(self.thresholdWin.paraDict['th_FireCurrent_Up']):
                    item.setForeground(QBrush(QColor(255, 0, 0)))
                elif float(self.resultList[col]) < float(self.thresholdWin.paraDict['th_FireCurrent_Up']):
                    item.setForeground(QBrush(QColor(0, 0, 255)))
            elif col == 11 and self.resultList[col] != '-':
                if float(self.resultList[col]) > float(self.thresholdWin.paraDict['th_FireCurrent_Up']):
                    item.setForeground(QBrush(QColor(255, 0, 0)))
                elif float(self.resultList[col]) < float(self.thresholdWin.paraDict['th_FireCurrent_Up']):
                    item.setForeground(QBrush(QColor(0, 0, 255)))
        else:
            item = QStandardItem(self.resultList[col][0:2])
            if self.resultList[col][0:2] == '通过':
                item.setBackground(QBrush(QColor(0, 168, 243)))
            elif self.resultList[col][0:2] == '失败':
                item.setBackground(QBrush(QColor(205, 0, 0)))
        item.setFont(QFont('Times New Roman', 15, QFont.Weight.Light))

        return item

    def parseDetectionResults(self): # 解析检测结果
        self.resultList[0] = self.le_Name.text()
        self.resultList[1] = self.detectionTime
        tmp = self.protocolWin.data.decode("utf-8")
        l = len(tmp)
        if tmp.find("UIDNODET", 0, l) != -1:
            self.userTextBrowserAppend("无模块连接，请检查接线")
            self.enableBtnFunc()
        else:
            self.resultList[6] = self.uid
            if tmp.find("UNERROR", 0, l) != -1: # 核对编码失败
                self.resultList[4] = "失败"
                self.resultList[5] = "离线"
                self.resultList[6] = self.uid
                self.resultList[7] = "-"
                self.resultList[8] = "-"
                self.resultList[9] = "-"
                self.resultList[14] = "失败"
                self.detResCode[2] = 0
                self.lineVoltageCurrentCheck(tmp, False)
                if self.uid in self.devicesState:
                    self.devicesState.pop(self.uid)
                self.userTextBrowserAppend("核对编码失败，请检查输入编码！")
                self.enableBtnFunc()
            else:
                self.resultList[4] = "成功"
                self.detResCode[2] = 1
                self.lineVoltageCurrentCheck(tmp, True)
                if self.isLVLCOK == True:
                    self.isLVLCOK = False
                    self.drainWorkCurrentCheck(tmp)
                    if tmp.find("PIOK", 0, l) != -1:
                        if tmp.find("POOK", 0, l) != -1:
                            self.detResCode[3] = 1
                            self.resultList[5] = "在线"
                            self.resultList[6] = tmp[tmp.find("UN",  0,  l) + 2 : tmp.find("PIOK", 0, l)] # UID
                            # 内置模块
                            if tmp.find("UFERROR", 0, l) == -1:
                                self.detResCode[5] = 1
                                self.resultList[10] = tmp[tmp.find("POOKUF",   0, l) + 6 : tmp.find("UFRE", 0, l)]
                                if tmp.find("UFREC", 0, l) != -1:
                                    fvi = tmp[tmp.find("UFV",  0, l) + 3 : tmp.find("UFA", 0, l)]
                                    self.resultList[12] = fvi[0 : len(fvi) - 1] + '.' + fvi[len(fvi) - 1]
                                    if tmp.find("UNREC", 0, l) != -1:
                                        fci = tmp[tmp.find("UFA",  0, l) + 3 : tmp.find("UNREC", 0, l)] #引爆电流
                                    elif tmp.find("UNREJ", 0, l) != -1:
                                        fci = tmp[tmp.find("UFA",  0, l) + 3 : tmp.find("UNREJ", 0, l)] #引爆电流
                                    elif tmp.find("UNNON", 0, l) != -1:
                                        fci = tmp[tmp.find("UFA",  0, l) + 3 : tmp.find("UNNON", 0, l)] #引爆电流
                                    if (float(fci) > float(self.thresholdWin.paraDict['th_FireCurrent_Down'])) and (float(fci) < float(self.thresholdWin.paraDict['th_FireCurrent_Up'])):
                                        self.detResCode[6] = 1
                                        self.resultList[13] = "正常"
                                    else:
                                        self.detResCode[6] = 0
                                        self.resultList[13] = "超限"
                                    # 被测模块
                                    if tmp.find("UNNON", 0, l) == -1:
                                        if tmp.find("UNREC", 0, l) != -1:
                                            self.detResCode[3] = 1
                                            self.resultList[5] = "在线"
                                            fv = tmp[tmp.find("UNV", l - 40, l) + 3 : tmp.find("UNA", l - 10, l)] # 引爆电压
                                            self.resultList[8] = fv[0 : len(fv) - 1] + '.' + fv[len(fv) - 1]
                                            fc = tmp[tmp.find("UNA", l - 10, l) + 3 : l - 4] # 引爆电流
                                            self.resultList[7] = fc
                                            if (float(fc) > float(self.thresholdWin.paraDict['th_FireCurrent_Down'])) and (float(fc) < float(self.thresholdWin.paraDict['th_FireCurrent_Up'])):
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
                                            self.resultList[5] = "离线"
                                            self.resultList[7] = "-"
                                            self.resultList[8] = "-"
                                            self.resultList[9] = "-"
                                            self.userTextBrowserAppend("被测模块确认引爆代码匹配失败，请检查")
                                            self.enableBtnFunc()
                                            self.resultList[14] = '失败'
                                    elif tmp.find("UNNON", 0, l) != -1:
                                        self.detResCode[3] = 0
                                        self.resultList[5] = "离线"
                                        self.resultList[7] = "-"
                                        self.resultList[8] = "-"
                                        self.resultList[9] = "-"
                                        self.resultList[14] = '失败'
                                        self.userTextBrowserAppend("引爆被测模块前无法检测到被测模块，请检查")
                                        self.devicesState[self.uid]['det'] = False
                                        self.devicesState[self.uid]['res'] = self.resultList.copy()
                                    self.resultList[11] = fci
                                elif tmp.find("UFREJ", 0, l) != -1:
                                    self.userTextBrowserAppend("内置模块引爆代码匹配失败，请检查")
                            else:
                                self.detResCode[5] = 0
                                self.resultList[10] = 'EEEEE'
                                self.resultList[11] = "-"
                                self.resultList[12] = "-"
                                self.resultList[13] = "-"
                                self.resultList[14] = '失败'
                                self.userTextBrowserAppend("查询内置模块编码失败，请检查")
                        else:
                            self.detResCode[3] = 0
                            self.resultList[5] = "离线"
                            self.resultList[6] = self.uid
                            self.resultList[7] = "-"
                            self.resultList[8] = "-"
                            self.resultList[9] = "-"
                            # 结论
                            self.resultList[14] = '失败'
                            self.userTextBrowserAppend("断开火工，火工部存在, 被测模块火工检测异常")
                    elif tmp.find("PIER", 0, l) != -1:
                        self.detResCode[3] = 0
                        self.resultList[5] = "离线"
                        self.resultList[6] = self.uid
                        self.resultList[7] = "-"
                        self.resultList[8] = "-"
                        self.resultList[9] = "-"
                        self.devicesState[self.uid]['det'] = False
                        # 结论
                        self.resultList[14] = '失败'
                        self.userTextBrowserAppend("接入火工，火工部不存在, 被测模块火工检测异常")
                    s = 0
                    for t in range(len(self.detResCode)):
                        s = s + self.detResCode[t]
                    if s != 7:
                        self.resultList[14] = '失败'
                    self.devicesState[self.uid]['res'] = self.resultList.copy()
                    self.changeResultsFile(self.uid)
                    self.updateDevicesStateFile()                    
                    rowcnt = self.tableViewModel.rowCount()
                    if rowcnt == 0: # 表格视图无显示数据
                        for col in range(15):
                            item = self.markAndShowTheResults(col)
                            self.tableViewModel.setItem(self.tableviewRowIndex, col, item)
                        self.tableviewRowIndex = 1
                    else: # 表格视图已有显示数据
                        dupResRow = -1
                        for r in range(rowcnt):
                            if self.tableViewModel.item(r, 6).text() == self.resultList[6]: # 编码查重，发现当前记录和视图显示记录重复，覆盖记录
                                for col in range(15):
                                    item = self.markAndShowTheResults(col)
                                    self.tableViewModel.setItem(r, col, item)
                                dupResRow = r
                        if dupResRow == -1: # 无重复检测记录
                            for col in range(15):
                                item = self.markAndShowTheResults(col)
                                self.tableViewModel.setItem(rowcnt, col, item)
                            self.tableviewRowIndex = rowcnt + 1
                        else:
                            self.tableviewRowIndex = rowcnt
                    self.resultLastList = self.resultList.copy()
                else:
                    pass
        self.enableBtnFunc()
        self.flushTheSerialBuffer()
        self.le_Encoding.setFocus()
#------------------------------------END----------------------数据解析------------------------------------END----------------------#

    def sleepUpdate(self, sec):
        cnt = 0
        while True:
            QApplication.processEvents()
            time.sleep(0.01)
            cnt = cnt + 1
            if cnt == sec*100:
                break

    def closeEvent(self, QCloseEvent):
        if self.tableViewModel.rowCount() != 0:
            choice = QMessageBox.critical(self, "关闭程序", "检测结果尚未保存，是否保存？\n", QMessageBox.Yes|QMessageBox.No| QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                if self.protocolWin.prvSerial.isOpen():
                    self.protocolWin.prvSerial.close()
                self.on_btn_SaveResultsAs_clicked()
                app = QApplication.instance()
                app.quit()
            elif choice == QMessageBox.No:
                QCloseEvent.accept()
            elif choice == QMessageBox.Cancel:
                QCloseEvent.ignore()
        else:
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
    MainTerminal = MainWin()
    MainTerminal.show()
    sys.exit(MainApp.exec_())
