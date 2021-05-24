# -*- coding: utf-8 -*-
from UserImport import *

class MainWin(QtWidgets.QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        super(MainWin, self).__init__()  # 继承父类的所有属性
        # 初始化UI
        self.initUi()
        # for col in range(15):
        #     item = QStandardItem(self.resultList[col])
        #     self.tableViewModel.setItem(self.tableRow, col, item)
        # self.tableRow = self.tableRow + 1
        # time.sleep(1)
        # self.resultList[1] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # for col in range(15):
        #     item = QStandardItem(self.resultList[col])
        #     self.tableViewModel.setItem(self.tableRow, col, item)
        # self.tableRow = self.tableRow + 1
        # time.sleep(1)
        # self.resultList[1] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # for col in range(15):
        #     item = QStandardItem(self.resultList[col])
        #     self.tableViewModel.setItem(self.tableRow, col, item)
        # self.tableRow = self.tableRow + 1
        # time.sleep(1)
        # self.resultList[1] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # for col in range(15):
        #     item = QStandardItem(self.resultList[col])
        #     self.tableViewModel.setItem(self.tableRow, col, item)
        # self.tableRow = self.tableRow + 1
        # time.sleep(1)
        # self.resultList[1] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # for col in range(15):
        #     item = QStandardItem(self.resultList[col])
        #     self.tableViewModel.setItem(self.tableRow, col, item)
        # self.tableRow = self.tableRow + 1
    
    def __del__(self):
        self.protocolWin.serialManager.wait()
        self.protocolWin.serialMonitor.wait()
        self.timsRefresh.wait()
        print("{} 退出主窗口".format(__file__))

    def initUi(self):
        self.setupUi(self)
        # 自定义工具实例化
        self.usualTools = Tools()
        # 设置窗口居中显示
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()
        # print("Your screen's size is:", self.width, "X", self.height)
        self.resize(self.width, self.height)
        self.Wsize = self.geometry()
        centerX = int((self.width - self.Wsize.width()) / 2)
        centerY = int((self.height - self.Wsize.height()) / 2)
        self.move(centerX, centerY)
        self.setWindowTitle("Detector")
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setWindowState(Qt.WindowMaximized) 
        # 消息提示窗口初始化
        self.textBrowser.setFontFamily("微软雅黑")
        self.textBrowser.setFontPointSize(14)
        # 状态栏初始化
        self.myStatusBar = QStatusBar()
        self.myStatusBar.setFont(QFont("Times New Roman", 16, QFont.Light))
        self.setStatusBar(self.myStatusBar)
        # 配置界面类实例
        self.protocolWin = ProtocolWin()
        self.protocolWin.protocolAppendSignal.connect(self.userTextBrowserAppend)
        GetSetObj.set(self.protocolWin)
        self.protocolWin.serialManager.recvSignal.connect(self.serialRecvData) # 串口线程实例
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
        # 消息保存
        self.isMessageSavedFirst = True
        self.isMessageSaved = True
        self.messagePath = ""
        # 测试数据Excel文件保存变量的初始化
        self.excel = PrivateOpenPyxl() # Excel实例化全局对象
        self.isExcelSavedFirst = True # 是否是第一次保存
        self.isExcelSaved = True # 是否是已经保存 
        self.excelFilePath = "" # 文件路径
        self.excelFile = "" # 文件
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
        # 表格模型初始化
        self.tableRow = 0 # 填入表格的行数
        self.tableHeadline = [
            "测试员",   "时间",      "漏电流(uA)", "工作电流(uA)",  "ID核对",
            "在线检测", "被测选发",   "电流(mA)",   "电压(V)",      "电流判断",
            "内置选发", "电流(mA)",  "电压(V)",    "电流判断",      "结论" ]   
        self.tableViewModel = QStandardItemModel(0, 15, self)
        self.tableViewModel.setHorizontalHeaderLabels(self.tableHeadline) # 表头
        # 表格视图委托初始化
        self.tableViewDelegate = PrivateTableViewDelegate()
        # 检测数据显示表格模型初始化
        self.tableView_result.setModel(self.tableViewModel)
        self.tableView_result.horizontalHeader().setStretchLastSection(True)
        self.tableView_result.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView_result.setItemDelegate(self.tableViewDelegate)
        self.tableView_result.horizontalHeader().setFont(QFont("微软雅黑", 12, QFont.Light))
        self.tableView_result.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView_result.verticalHeader().hide()
        self.tableView_result.setContextMenuPolicy(Qt.CustomContextMenu)
        # 表格视图上下文菜单
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
        self.tvMenu.addAction(self.saveSelected)
        self.tvMenu.addAction(self.saveAll)
        self.tvMenu.addAction(self.dropSelected)
        self.tvMenu.addAction(self.dropAll)
        # 检测以及编码默认状态设置
        self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")
        self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")
        # UID输入验证器设置
        regValidator = QRegExpValidator(self)
        reg = QRegExp("[a-fA-F0-9]+$")
        regValidator.setRegExp(reg)
        # UID输入编辑栏初始化
        self.lineEdit_uidInput.setMaxLength(5)
        self.lineEdit_uidInput.setValidator(regValidator)
        self.lineEdit_uidInput.setToolTip("字母范围a~f, A~F, 数字0~9")
        self.lineEdit_uidInput.setFocus()
        self.setMouseTracking(True)
        # 编号记录列表
        self.codeList = []

    def tvSaveSelected(self):
        if len(self.tvRowList) != 0:
            self.userTextBrowserAppend('保存选中数据')
        else:
            self.userTextBrowserAppend('数据已清空')

    def tvSaveAll(self):
        if len(self.tvRowList) != 0:
            self.userTextBrowserAppend('保存全部数据')
        else:
            self.userTextBrowserAppend('数据已清空')

    def tvDropSelected(self):
        if len(self.tvRowList) != 0:
            for n in self.tvRowList:
                self.tableViewModel.removeRow(n)
            self.userTextBrowserAppend('删除选中数据')
        else:
            self.userTextBrowserAppend('数据已清空')
        
    def tvDropAll(self):
        if len(self.tvRowList) != 0:
            self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())
            self.userTextBrowserAppend('删除全部数据')
        else:
            self.userTextBrowserAppend('数据已清空')

    def tvCustomContextMenuRequested(self, p):
        self.tvIndex = self.tableView_result.selectionModel().selectedRows()
        self.tvRowList = []
        for i in self.tvIndex:
            self.tvRowList.append(i.row())
        self.tvRowList.sort(key=int, reverse=True)
        print(self.tvRowList)
        self.tvMenu.exec_(self.tableView_result.mapToGlobal(p))

    @QtCore.pyqtSlot()
    def on_pushBtn_protocolSetting_clicked(self):
        self.protocolWin.show()
        self.lineEdit_uidInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushBtn_thresholdSetting_clicked(self):
        self.thresholdWin.show()
        self.lineEdit_uidInput.setFocus()

    def userTextBrowserAppend(self, str):
        t = self.usualTools.getTimeStamp()
        self.textBrowser.append(t + str)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
    
    def openMessageRecord(self):
        try:
            with open("message_save_record.txt", "rb") as msrf:
                omr = pk.load(msrf) # 将二进制文件对象转换成Python对象
            self.isMessageSavedFirst = omr[0][0]
            self.isMessageSaved = omr[0][1]
            self.messagePath = omr[1]
        except:
            pass

    def saveMessageRecord(self):
        self.saved_info = ([self.isMessageSavedFirst, self.isMessageSaved],  self.messagePath)
        with open("message_save_record.txt", "wb") as fsmf:
            pk.dump(self.saved_info, fsmf) # 用dump函数将Python对象转成二进制对象文件

    @QtCore.pyqtSlot()
    def on_pushBtn_cleanMsgArea_clicked(self):
        if self.textBrowser.toPlainText() != "":
            choice = QMessageBox.question(
                self, "窗口消息", "确认清除消息？", QMessageBox.Yes | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                self.textBrowser.clear()
            elif choice == QMessageBox.Cancel:
                pass
        else:
            pass

    def firstSaveMessage(self):
        if self.messagePath == "":
            self.messagePath, isAccept =  QFileDialog.getSaveFileName(self, "保存文件", "./message", "messagefiles (*.log)")
            if isAccept:
                if self.messagePath:
                    if self.textBrowser.toPlainText() != "":
                        choice = QMessageBox.question(self, "窗口消息", "保存消息？", QMessageBox.Yes | QMessageBox.Cancel)
                        if choice == QMessageBox.Yes:
                            text = bytes(self.textBrowser.toPlainText(), encoding="utf-8")
                            with open(self.messagePath, "ab") as fsf:
                                fsf.write(text)
                        elif choice == QMessageBox.Cancel:
                            pass
                    else:
                        pass 
                    self.isMessageSavedFirst = False
                    self.isMessageSaved = True
                self.userTextBrowserAppend("消息保存成功")
                self.textBrowser.append("@保存至\"" + str(self.messagePath) + "\"")
                self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
                self.saveMessageRecord()
        else:
            self.userTextBrowserAppend("当前无消息")
        
    def saveMessage(self):
        if self.textBrowser.toPlainText() != "":
            text = bytes(self.textBrowser.toPlainText(), encoding="utf-8")
            with open(self.messagePath, "ab") as fsf:
                fsf.write(text)
            self.userTextBrowserAppend("消息保存成功")
            self.textBrowser.append("@保存至\"" + str(self.messagePath) + "\"")
            self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
            self.saveMessageRecord()
        else:
            self.userTextBrowserAppend("当前无消息")
    
    @QtCore.pyqtSlot()
    def on_pushBtn_saveMsgArea_clicked(self):
        self.openMessageRecord()
        if self.isMessageSavedFirst:
            self.firstSaveMessage()
        elif self.isMessageSaved:
            self.saveMessage()

    def showDaetTime(self, timeStr):
        self.myStatusBar.showMessage(timeStr)
       
    @QtCore.pyqtSlot()
    def on_lineEdit_setDrainCurrentTop_textChanged(self):
        if self.lineEdit_setDrainCurrentTop.text() != self.thresholdWin.paraDict["th_DrainCurrent_Up"]:
            self.isConfigSaved = False
        else:
            self.isConfigSaved = True
        self.saveConfigRecord()
 
    def parseSettingThreshold(self):
        tmp = self.protocolWin.data.decode("utf-8")
        res = tmp[3:(len(tmp)-4)]
        if res == "PARAOK":
            # self.sleepUpdate(2) 导致主窗口卡顿的地方
            if self.thresholdWin.isActiveWindow():
                self.thresholdWin.close()
            self.userTextBrowserAppend("测试仪接收参数成功")
        elif res == "PARAERR":
            self.userTextBrowserAppend("测试仪接收参数失败")
        elif res == "PARALESS":
            self.userTextBrowserAppend("测试仪接收参数缺失")
        self.lineEdit_uidInput.setFocus()
    
    def updateWorkMode(self, str):
        print("In updateWorkMode...............")
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

    def setWorkMode(self, tmp):
        # 2021年3月30日 09:29:36 工作模式获取整合到参数获取中
        if tmp[len(tmp) - 6] == 48:
            self.workMode["encoding"] = "0"
        else:
            self.workMode["encoding"] = "1"
        if tmp[len(tmp) - 5] == 48:
            self.workMode["detection"] = "0"
        else:
            self.workMode["detection"] = "1"

    def getWorkMode(self):
        return self.workMode

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

    def parseDevicPara(self):
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
        else:
            self.userTextBrowserAppend("请接通测试仪电源")
        
    def getDevicePara(self):
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
        else:
            self.userTextBrowserAppend("串口未打开")

    def reportSystemPower(self, str):
        print("In reportSystemPower...............")
        if str == "RMPO\r\n":
            self.userTextBrowserAppend("测试仪已上电，线路供电接通")
            time.sleep(1)
            self.on_pushBtn_deviceSelfCheck_clicked() # 进行一次测试仪自检
        else:
            self.userTextBrowserAppend("测试仪已上电，线路供电断开")

    def serialRecvData(self, data):
        QApplication.processEvents()
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
                        self.parseDevicPara()
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

    @QtCore.pyqtSlot()
    def on_pushBtn_deviceSelfCheck_clicked(self):
        if self.protocolWin.prvSerial.isOpen() == True:
            self.userTextBrowserAppend("测试仪自检")
            self.getDevicePara()
            self.lineEdit_uidInput.setFocus()
        else:
            QMessageBox.information(self, "串口信息", "串口未打开\n请打开串口", QMessageBox.Yes)
    
    def parseQueryCodeResults(self):
        tmp = self.protocolWin.data.decode("utf-8")
        tmp = tmp[tmp.find("UID", 0, len(tmp)) + 3 : len(tmp) - 4]
        if tmp == 'NODET':
            self.userTextBrowserAppend("无模块连接")
        else:
            self.userTextBrowserAppend("当前模块编号：" + tmp)
        self.lineEdit_uidInput.setFocus()

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
        else:
            self.userTextBrowserAppend("串口未打开")
    
    def parseEncodingResults(self):
        res = ""
        tmp = self.protocolWin.data.decode("utf-8")
        # print("tmp:" + tmp)
        res = tmp[3:(len(tmp) - 4)]
        if tmp.find("UID"):
            if res == "UIDOK":
                self.userTextBrowserAppend("写入UID成功")
            elif res == "UIDERR":
                self.userTextBrowserAppend("写入UID失败")
        elif tmp.find("FACULTY"):
            self.userTextBrowserAppend("模块已出故障，请更换模块！")
        elif tmp.find("NCODE"):
            self.workMode["encoding"] = "0"
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/close)}")
            self.userTextBrowserAppend("无法进行编码，请检查编码按键")
        self.lineEdit_uidInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushBtn_deviceEncoding_clicked(self):
        if self.workMode["encoding"] == "1":
            print("/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/")
            print("Encoding......")
            self.userTextBrowserAppend("执行编码")
            if self.protocolWin.prvSerial.isOpen():
                uid = self.lineEdit_uidInput.text()
                if uid != "":
                    self.userTextBrowserAppend("输入UID：" + self.lineEdit_uidInput.text())
                    self.protocolWin.data = b''
                    self.protocolWin.rxCheck = 0
                    self.protocolWin.prvSerial.flushOutput()
                    self.protocolWin.serialSendData(Func.f_DevEncoding, uid, '')
                else:
                    self.userTextBrowserAppend("输入编号为空！")
            else:
                self.userTextBrowserAppend("串口未打开")
        else:
            self.userTextBrowserAppend("编码【未开启】")

    def parseDetectionResults(self):
        res = ""
        tmp = self.protocolWin.data.decode("utf-8")
        l = len(tmp)
        res = tmp[3:11]
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
                self.userTextBrowserAppend("UID核对失败，请检查输入编码！")
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
                        else:
                            self.resultList[9] = "超限"
                            self.resultList[14] = "未通过"
                    else:
                        self.resultList[5] = "离线"
                        self.resultList[6] = tmp[tmp.find("U1",  11, 25) + 2 : tmp.find("PIOK", 11, l)] # UID
                        self.resultList[7] = "-"
                        self.resultList[8] = "-"
                        self.resultList[9] = "-"
                else:
                    self.resultList[4] = "失败"
                    self.resultList[5] = "离线"
                # 内置模块
                self.resultList[10] = tmp[tmp.find("U2",   11, l) + 2 : tmp.find("U2RE", 11, l)]
                self.resultList[11] = tmp[tmp.find("U2A",  11, l) + 3 : tmp.find("U1RE", 11, l)]
                iv = tmp[tmp.find("U2V",  11, l) + 3 : tmp.find("U2A", 11, l)]
                self.resultList[12] = iv[0 : len(iv) - 1] + '.' + iv[len(iv) - 1]
                self.resultList[13] = "正常"
                # 更新model
                for col in range(15):
                    item = QStandardItem(self.resultList[col])
                    self.tableViewModel.setItem(self.tableRow, col, item)
                self.tableRow = self.tableRow + 1
                self.lineEdit_uidInput.clear()
        self.lineEdit_uidInput.setFocus()
        # elif tmp[3:8] == "NDETE":
        #     self.workMode["detection"] = "0"
        #     self.userTextBrowserAppend("无法进行检测，请检查检测按键")

    @QtCore.pyqtSlot()
    def on_pushBtn_deviceDetection_clicked(self):
        if self.workMode["detection"] == "1":
            print("/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/")
            print("Detecting......")
            self.detectionTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.userTextBrowserAppend("执行检测")
            if self.protocolWin.prvSerial.isOpen():
                uid = self.lineEdit_uidInput.text()
                if uid != "":
                    self.userTextBrowserAppend("输入UID：" + self.lineEdit_uidInput.text())
                    self.protocolWin.data = b""
                    self.protocolWin.rxCheck = 0
                    self.protocolWin.prvSerial.flushOutput()
                    self.protocolWin.serialSendData(Func.f_DevDetection, uid, '')
                else:
                    self.userTextBrowserAppend("输入编号为空！")
            else:
                self.userTextBrowserAppend("串口未打开")
        else:
            self.userTextBrowserAppend("检测【未开启】")

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
            pk.dump( self.saved_info, esrf) # 用dump函数将Python对象转成二进制对象文件
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
            
    def firstsaveResults(self):
        if self.excelFilePath == "":
            self.excelFilePath, isAccept =  QFileDialog.getSaveFileName(self, "保存文件", "./recording", "recorded data(*.xlsx)")
            if isAccept:
                if self.excelFilePath:
                    self.excelFile = os.path.split(self.excelFilePath)[1]
                    self.excel_sheet = "Sheet Of Records"
                    self.excel.initWorkBook(self.excelFile, self.excel_sheet)
                    self.isExcelSavedFirst = False
                    self.isExcelSaved = True
                    self.excel.wrtieRow(self.excelFile, self.tableHeadline) # 添加表头
                    self.userTextBrowserAppend("创建数据记录表成功")
                    self.textBrowser.append("@保存至\"" + str(self.excelFilePath) + "\"")
                    self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
                    res = self.compareResult()
                    if res == 1:
                        self.excel.wrtieRow(self.excelFile, self.resultList)
                        self.isExcelSaved = True
                        self.currentResultSaved = True
                        self.saveExcelRecord()
                    elif res == 0:
                        self.userTextBrowserAppend("当前检测结果已记录，请重新进行编码和检测")  
                    elif res == -1:
                        self.userTextBrowserAppend("未有检测结果，请进行编码和检测")
                    self.resultLastList = self.resultList.copy()
                    QApplication.processEvents() 
                    self.lineEdit_uidInput.setFocus()
                else:
                    pass
        else:
            pass

    def saveResults(self):
        self.openExcelRecord()
        res = self.compareResult()
        if res == 1:
            self.excel.wrtieRow(self.excelFile, self.resultList)
            self.userTextBrowserAppend("保存数据记录表成功")
            self.isExcelSaved = True
            self.currentResultSaved = True
            self.saveExcelRecord()
        elif res == 0:
            self.userTextBrowserAppend("当前检测结果已记录，请重新进行编码和检测")  
        elif res == -1:
            self.userTextBrowserAppend("未有检测结果，请进行编码和检测")
        self.resultLastList = self.resultList.copy()
        self.lineEdit_uidInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushBtn_clearResults_clicked(self):
        self.tableRow = 0
        self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())
        self.lineEdit_uidInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushBtn_saveResults_clicked(self):
        self.openExcelRecord()
        if self.isExcelSavedFirst:
            self.firstsaveResults()
        elif self.isExcelSaved:
            self.saveResults()
        self.lineEdit_uidInput.setFocus()

    @QtCore.pyqtSlot()
    def on_pushBtn_showResults_clicked(self):
        self.openExcelRecord()
        recordsfile, _ = QFileDialog.getOpenFileName(self, "打开记录文件", './', 'records (*.xlsx)')
        if recordsfile:
            os.startfile(recordsfile)
            self.isConfigSaved = True
        self.saveExcelRecord()   
        self.lineEdit_uidInput.setFocus()  

    @QtCore.pyqtSlot()
    def on_pushBtn_deviceEncodingDetection_clicked(self):
        self.userTextBrowserAppend("执行编码和检测")
        if self.workMode["encoding"] == "1" and self.workMode["detection"] == "1":
            if self.protocolWin.prvSerial.isOpen():
                self.detectionTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                uid = self.lineEdit_uidInput.text()
                if uid != "":
                    self.userTextBrowserAppend("输入UID：" + self.lineEdit_uidInput.text())
                    self.protocolWin.data = b""
                    self.protocolWin.rxCheck = 0
                    self.protocolWin.prvSerial.flushOutput()
                    print("/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/")
                    print("Encoding......")
                    self.userTextBrowserAppend("模块编码")
                    self.protocolWin.prvSerial.flushOutput()
                    self.protocolWin.serialSendData(Func.f_DevEncoding, uid, '')
                    while True:
                        QApplication.processEvents()
                        time.sleep(0.01)
                        if self.protocolWin.data != b"":
                            if self.protocolWin.data[2] != 50:
                                continue
                            else:
                                break
                    print("/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/")
                    print("Detecting......")
                    self.userTextBrowserAppend("模块检测")
                    self.protocolWin.prvSerial.flushOutput()
                    self.protocolWin.serialSendData(Func.f_DevDetection, uid, '')
                else:
                    self.userTextBrowserAppend("输入编号为空！")
            else:
                self.userTextBrowserAppend("串口未打开")
        else:
            self.userTextBrowserAppend("编码和检测未开启")
        
    @QtCore.pyqtSlot()
    def on_pushBtn_clearUidInput_clicked(self):
        self.lineEdit_uidInput.clear()

    def sleepUpdate(self, sec):
        cnt = 0
        while True:
            QApplication.processEvents()
            time.sleep(1)
            cnt = cnt + 1
            if cnt == sec:
                break
    
    def mousePressEvent(self, e):
        if e.buttons() == QtCore.Qt.LeftButton:
            # print('鼠标单击')
            self.lineEdit_uidInput.setFocus()
    
    def closeEvent(self, QCloseEvent):
        if not self.thresholdWin.isConfigSaved:
            choice = QMessageBox.question(self, "保存文件", "是否保存配置文件", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                QCloseEvent.accept()
                self.firstSaveThreshold()
            elif choice == QMessageBox.No:
                QCloseEvent.accept()
            else:
                QCloseEvent.ignore()
        else:
            choice = QMessageBox.question(self, "关闭窗口", "是否关闭窗口？", QMessageBox.Yes | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                QCloseEvent.accept()
                app = QApplication.instance()
                app.quit()
            elif choice == QMessageBox.Cancel:
                QCloseEvent.ignore()

def auto():
    MainTerminal.protocolWin.autoConnectDetector()
    if len(MainTerminal.protocolWin.comDescriptionList) != 0:
        if MainTerminal.protocolWin.prvSerial.isOpen():
            MainTerminal.sleepUpdate(3)
            # MainTerminal.thresholdWin.on_pushBtn_saveSettingsRecord_clicked()
            MainTerminal.thresholdWin.getUserPara()
            cnt = 0
            MainTerminal.thresholdWin.para = ""
            for k, v in MainTerminal.thresholdWin.paraDict.items():
                if cnt < 10:
                    MainTerminal.thresholdWin.para = MainTerminal.thresholdWin.para + ("P" + str(cnt) + v)
                elif cnt == 10:
                    MainTerminal.thresholdWin.para = MainTerminal.thresholdWin.para + ("PA" + v)
                elif cnt == 11:
                    MainTerminal.thresholdWin.para = MainTerminal.thresholdWin.para + ("PB" + v)
                elif cnt == 12:
                    MainTerminal.thresholdWin.para = MainTerminal.thresholdWin.para + ("PC" + v)
                elif cnt == 13:
                    MainTerminal.thresholdWin.para = MainTerminal.thresholdWin.para + ("PD" + v)
                elif cnt == 14:
                    MainTerminal.thresholdWin.para = MainTerminal.thresholdWin.para + ("PE" + v)
                elif cnt == 15:
                    MainTerminal.thresholdWin.para = MainTerminal.thresholdWin.para + ("PF" + v)
                cnt += 1
            MainTerminal.thresholdWin.openConfigRecord()
            if MainTerminal.thresholdWin.isConfigSavedFirst == True:
                MainTerminal.thresholdWin.firstSaveThreshold(MainTerminal.thresholdWin.para)
            elif MainTerminal.thresholdWin.isConfigSaved:
                MainTerminal.thresholdWin.settingThreshold()
    else:
        pass

class autoConnectThread(QThread):
    def __init__(self):
        super(autoConnectThread, self).__init__()

    def run(self):
        auto()

if __name__ == "__main__":
    MainApp = QApplication(sys.argv)
    MainApp.setWindowIcon(QIcon("./resources/icons/robot.ico"))
    MainTerminal = MainWin()
    MainTerminal.show()
    AutoInitProcedure = autoConnectThread()
    AutoInitProcedure.start()
    sys.exit(MainApp.exec_()) 