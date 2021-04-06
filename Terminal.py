# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from UserImport import *

class MainWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWin, self).__init__()  # 继承父类的所有属性   

        # 初始化UI
        self.initUi()
    
    def __del__(self):
        if self.prvSerial.isOpen():
            self.prvSerial.close()
        print("{} 程序结束，释放资源".format(__class__))

    def initUi(self):
        self.setupUi(self)

        # 自定义工具实例化
        self.usualTools = Tools()

        # set Window"s location
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()
        print("Your screen's size is:", self.width, "X", self.height)
        self.resize(self.width, self.height)
        self.Wsize = self.geometry()
        centerX = int((self.width-self.Wsize.width())/2)
        centerY = int((self.height-self.Wsize.height())/2)
        self.move(centerX, centerY)
        self.setWindowTitle("Detector")
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowState(Qt.WindowMaximized)     

        # 工作模式初始化
        self.workMode = {"encoding": "X",  "detection": "X"} # 未知状态
        self.data = b''

        # 操作人员姓名录入
        self.is_name_input = False
        self.name = "嬴政" # 默认操作员姓名
        
        # 自定义本地时间更新线程
        self.thread01 = TimeThread()
        self.thread01.secondSignal.connect(self.showDaetTime)
        self.thread01.start()

        # 阈值初始化
        global paraDict  # 参数字典
        paraDict = {
            "th_DrainCurrent_Up": "0", "th_DrainCurrent_Down": "0",
            "th_WorkCurrent_Up":  "0", "th_WorkCurrent_Down":  "0",
            "th_FireVoltage_Up":  "0", "th_FireVoltage_Down":  "0",
            "th_FireCurrent_Up":  "0", "th_FireCurrent_Down":  "0",
            "th_LineVoltage_Up":  "0", "th_LineVoltage_Down":  "0",
            "th_LineCurrent_Up":  "0", "th_LineCurrent_Down":  "0",
            "th_ComVoltage_Up":   "0", "th_ComVoltage_Down":   "0",
            "th_ComCurrent_Up":   "0", "th_ComCurrent_Down":   "0"}
        self.getUserPara()

        # 消息保存
        self.isMessageSavedFirst = True
        self.isMessageSaved = True
        self.messagePath = ""

        # 配置文件保存变量的初始化
        self.isConfigSavedFirst = True # 是否是第一次保存
        self.isConfigSaved = True # 是否是已经保存 
        self.configPath = "" # 文件路径

        # 测试数据Excel文件保存变量的初始化
        self.excel = PersonalExcel() # Excel实例化全局对象
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
        self.resultCurrentList = self.resultDefaultList.copy()
        # 测试检测结果备份，进行重复检测结果判断
        self.resultLastList = self.resultCurrentList.copy()
        # 当前记录是否已经被保存，防止重复保存
        self.currentResultSaved = False 

        # 检测数据显示表格模型初始化
        self.tableHeadline = [
            "测试员", "时间",      "漏电流(uA)", "工作电流(uA)", "ID核对",
            "在线检测", "被测选发",   "电流(mA)",  "电压(V)",      "电流判断",
            "内置选发", "电流(mA)",  "电压(V)",   "电流判断",      "结论" ]        
        self.tableViewModel = QStandardItemModel(3, 15, self)
        self.tableViewModel.setHorizontalHeaderLabels(self.tableHeadline)
        self.tableView_result.setModel(self.tableViewModel)
        self.tableView_result.horizontalHeader().setStretchLastSection(True)
        # self.tableView_result.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 拉伸
        self.tableView_result.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # 表格视图委托初始化
        self.tableViewDelegate = TableViewDelegate()
        self.tableView_result.setItemDelegate(self.tableViewDelegate)
        self.tableRow = 0 # 填入表格的行数
        
        # 第一次打开串口控自动检测制仪使能
        self.firstAutoDetetion = 1

        # 检测以及编码默认状态设置
        self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")
        self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")

        # 消息提示窗口初始化
        self.textBrowser.setFontFamily("微软雅黑")
        self.textBrowser.setFontPointSize(12)

        # UID输入验证器设置
        mixdedValidator = QRegExpValidator(self)
        reg = QRegExp("[a-fA-F0-9]+$")
        mixdedValidator.setRegExp(reg)
        self.lineEdit_uidInput.setMaxLength(5)
        self.lineEdit_uidInput.setValidator(mixdedValidator)
        self.lineEdit_uidInput.setToolTip("字母范围a~f, A~F, 数字0~9")

        # 串口变量初始化
        self.txCheck = 0
        self.txHighCheck = b'0'
        self.txLowCheck = b'0'
        self.rxCheck = 0
        self.rxHighCheck = b'0'
        self.rxLowCheck = b'0'
        self.serialNumber = 0

        # 串口初始化
        self.serialManager = PersonalSerial()  # 串口线程对象
        self.prvSerial = self.serialManager.userSerial  # 串口实例化全局对象
        self.detectPorts() # 检测端口并加入combobox
        self.serialManager.start()
        self.serialManager.recvSignal.connect(self.updateWorkMode)
        self.isSTM32Online = False

        # 绑定控件信号和槽函数
        self.bindSignalSlot()

    @QtCore.pyqtSlot()
    def on_lineEdit_uidInput_editingFinished(self):
        self.userTextBrowserAppend("编码输入完成")

    def userTextBrowserAppend(self, str):
        self.textBrowser.append(self.usualTools.getTimeStamp() + str)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
    
    def openMessageRecord(self):
        try:
            with open("message_save_record.txt", "rb") as msrf:
                omr = pk.load(msrf) # 将二进制文件对象转换成Python对象
                # print("openConfigRecord:" + str(ofr))
            self.isMessageSavedFirst = omr[0][0]
            self.isMessageSaved = omr[0][1]
            self.messagePath = omr[1]
        except:
            pass

    def saveMessageRecord(self):
        self.saved_info = ([self.isMessageSavedFirst, self.isMessageSaved],  self.messagePath)
        with open("message_save_record.txt", "wb") as fsmf:
            pk.dump(self.saved_info, fsmf) # 用dump函数将Python对象转成二进制对象文件
        # print("saveConfigRecord:" + str(self.saved_info))

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
            self.messagePath, isAccept =  QFileDialog.getSaveFileName(self, "保存文件", "./message", "logfiles (*.log)")
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
        self.label_localDateTime.setText(timeStr)
    
    def detectPorts(self):
        self.comboBox_selectComNum.clear()  # 清空端口选择按钮
        self.comPortList = serial.tools.list_ports.comports()
        self.comPortList.sort()
        self.comDescriptionList = list()
        if len(self.comPortList) >= 1:
            for p in self.comPortList:
                self.comDescription = p.description
                self.comDescriptionList.append(self.comDescription)
                self.comboBox_selectComNum.addItem(self.comDescription)
            print(self.comDescriptionList)
            self.userTextBrowserAppend("已检测到串口，请选择并打开串口")
            self.userTextBrowserAppend("请先接入被测模块！")
        else:
            print("No port detected!")
            # self.statusbar.showMessage("未检测到串口")
            self.userTextBrowserAppend("未检测到串口，请连接备")
            QMessageBox.information(self, "串口信息", "未检测到串口!", QMessageBox.Yes)
    
    @QtCore.pyqtSlot()
    def on_pushBtn_serialSwitch_clicked(self):
        staText = self.pushBtn_serialSwitch.text()
        self.idlePorts = QSerialPortInfo.availablePorts()
        if staText == "打开串口":
            if len(self.idlePorts) >= 1:  # 打开时检测到有串口
                self.comDescription = self.comboBox_selectComNum.currentText()  # 获取comboBox当前串口描述
                self.comIndex = self.comDescriptionList.index(self.comDescription)
                self.portInfo = QSerialPortInfo(self.comPortList[self.comIndex].device)  # 该串口信息
                self.portStatus = self.portInfo.isBusy()  # 该串口状态
                if self.portStatus == False:  # 该串口空闲
                    self.serialManager.initPort(self.comPortList[self.comIndex].device)
                    try:
                        self.prvSerial.open()
                        if self.prvSerial.isOpen():
                            self.userTextBrowserAppend("[" + self.comPortList[self.comIndex].device + "]已打开")
                            self.pushBtn_serialSwitch.setText("关闭串口")
                            self.comboBox_selectComNum.setEnabled(False)
                    except:
                        QMessageBox.warning(self, "打开串口", "打开串口失败")
                        self.userTextBrowserAppend("[" + self.comPortList[self.comIndex].device + "]打开失败")
                    if self.prvSerial.isOpen(): 
                        self.prvSerial.flush()
                        self.prvSerial.write(bytes("Terminal\r\n", encoding="utf-8"))
                        startTiming = dt.datetime.now()
                        while True:
                            QApplication.processEvents()
                            num = self.prvSerial.inWaiting()
                            # print("openClosePort num:" + str(num)) # 输出收到的字节数
                            endTiming = dt.datetime.now()
                            if num == 0:
                                if (endTiming - startTiming).seconds >= 5:
                                    self.userTextBrowserAppend("控制仪无响应，请执行操作")
                                    self.isSTM32Online = False
                                    break
                            elif (num > 0 and num <= 4):
                                self.prvSerial.flushInput()
                            elif num >= 5:
                                time.sleep(0.1)
                                data = self.prvSerial.read(num)
                                if data.decode("utf-8") == "STM32":
                                    self.isSTM32Online = True
                                    break
                        if self.isSTM32Online == True:
                            if self.firstAutoDetetion == 1: # 第一次打开软件会执行控制仪自检
                                self.firstAutoDetetion = 0
                                self.userTextBrowserAppend("控制仪在线!")
                                self.on_pushBtn_deviceSelfCheck_clicked() # 每次运行程序执行一次自检即可
                            else:
                                self.userTextBrowserAppend("控制仪在线，请执行操作")
                else:
                    QMessageBox.warning(self, "串口状态", "串口使用中")
            else:  # 打开时检测到无串口
                QMessageBox.information(self, "串口信息", "请连接好模块!", QMessageBox.Yes)
                self.userTextBrowserAppend("未检测到串口，请连接备")
        elif staText == "关闭串口":
            self.prvSerial.close()
            self.userTextBrowserAppend("[" + self.comPortList[self.comIndex].device + "]已关闭")
            self.pushBtn_serialSwitch.setText("打开串口")
            self.comboBox_selectComNum.setEnabled(True)

    def rxFrameCheck(self):
        self.rxCheck = int(0)  # 校验和清零
        self.rxHighCheck = "F",
        self.rxLowCheck = "F"
        dataLength = len(self.data)
        data = self.data[0:(dataLength - 4)]
        for ch in data:  # 计算校验和
            self.rxCheck += ch
        self.rxHighCheck, self.rxLowCheck = self.usualTools.convertCheck(
            self.rxCheck & 0xFF)
        if (self.data[0] == 85) and (self.data[dataLength - 4] == self.rxHighCheck) and (self.data[dataLength - 3] == self.rxLowCheck) and \
           (self.data[dataLength - 2] == 13) and (self.data[dataLength - 1] == 10):
            print("RxFrame is right!")
            return State.s_RxFrameCheckOK
        else:
            print("RxFrame is wrong!")
            return State.s_RxFrameCheckErr

    def sendData2Bytes(self, func):
        uid = self.lineEdit_uidInput.text()
        if func == Func.f_DevGetSelfPara:
            tmp = str("D" + str(self.serialNumber) + func)
        elif func == Func.f_DevEncoding:
            tmp = str("D" + str(self.serialNumber) + func + uid)
        elif func == Func.f_DevDetection:
            tmp = str("D" + str(self.serialNumber) + func + uid)
        elif func == Func.f_DevSettingThreshold:
            with open(self.configPath, 'r') as rf:
                s = rf.read()
            tmp = str("D" + str(self.serialNumber) + func + s)
        tmp = tmp.encode("utf-8")
        if self.serialNumber == 9:  # 流水号
            self.serialNumber = 0
        else:
            self.serialNumber += 1

        return tmp

    def txFrameFormat(self, func):
        self.txCheck = int(0)  # 校验和清零
        self.txHighCheck = "0",
        self.txLowCheck = "0"
        try:
            txData = self.sendData2Bytes(func)
        except:
            print("Transfrom txData to bytes type failed!")
            return
        for ch in txData:  # 计算校验和
            self.txCheck += ch
        self.txHighCheck, self.txLowCheck = self.usualTools.convertCheck(self.txCheck & 0xFF)
        byteTmp = bytearray(txData)
        byteTmp.append(self.txHighCheck)
        byteTmp.append(self.txLowCheck)
        byteTmp.append(0x0D)
        byteTmp.append(0x0A)

        return byteTmp

    def sendByFunc(self, func):
        self.writeData = b""
        self.writeData = self.txFrameFormat(func)
        self.prvSerial.write(self.writeData)
        print("[self.writeData]>" + str(self.writeData))

    def serialSendData(self, func):
        if self.prvSerial.isOpen():
            self.comDescription = self.comboBox_selectComNum.currentText()  # 获取comboBox当前串口描述
            self.comIndex = self.comDescriptionList.index(self.comDescription) # 索引
            self.portInfo = QSerialPortInfo(self.comPortList[self.comIndex].device)  # 该串口信息
            self.uid = self.lineEdit_uidInput.text()  # 获取编号
            if self.portInfo.isBusy():# 该串口状态
                self.prvSerial.flush()
                self.data = b""
                try:
                    if func == Func.f_DevEncoding:
                        if self.uid != "":
                            self.sendByFunc(func)
                            print("InputSN:" + self.uid)
                        else:
                            QMessageBox.information(self, "输入编号", "编号输入为空!\n请输入编号", QMessageBox.Yes)
                    elif func == Func.f_DevDetection:
                        if self.uid != "":
                            self.sendByFunc(func)
                            print("InputSN:" + self.uid)
                        else:
                            QMessageBox.information(self, "输入编号", "编号输入为空!\n请输入编号", QMessageBox.Yes)
                    else:
                        self.sendByFunc(func)
                except:
                    QMessageBox.critical(self, "串口信息", "发送数据失败")
                finally:
                    self.prvSerial.flushOutput()
            else:
                QMessageBox.warning(self, "串口信息", "串口使用中")
        else:
            QMessageBox.information(self, "串口信息", "串口未打开\n请打开串口", QMessageBox.Yes)
            self.userTextBrowserAppend("串口未打开")
    
    def getUserPara(self):
        paraDict["th_DrainCurrent_Up"] = self.lineEdit_setDrainCurrentTop.text()
        paraDict["th_DrainCurrent_Down"] = self.lineEdit_setDrainCurrentBottom.text()
        paraDict["th_WorkCurrent_Up"] = self.lineEdit_setWorkCurrentTop.text()
        paraDict["th_WorkCurrent_Down"] = self.lineEdit_setWorkCurrentBottom.text()
        paraDict["th_FireVoltage_Up"] = self.lineEdit_setFireVoltageTop.text()
        paraDict["th_FireVoltage_Down"] = self.lineEdit_setFireVoltageBottom.text()
        paraDict["th_FireCurrent_Up"] = self.lineEdit_setFireCurrentTop.text()
        paraDict["th_FireCurrent_Down"] = self.lineEdit_setFireCurrentBottom.text()
        paraDict["th_LineVoltage_Up"] = self.lineEdit_setLineVoltageTop.text()
        paraDict["th_LineVoltage_Down"] = self.lineEdit_setLineVoltageBottom.text()
        paraDict["th_LineCurrent_Up"] = self.lineEdit_setLineCurrentTop.text()
        paraDict["th_LineCurrent_Down"] = self.lineEdit_setLineCurrentBottom.text()
        paraDict["th_ComVoltage_Up"] = self.lineEdit_setComVoltageTop.text()
        paraDict["th_ComVoltage_Down"] = self.lineEdit_setComVoltageBottom.text()
        paraDict["th_ComCurrent_Up"] = self.lineEdit_setComCurrentTop.text()
        paraDict["th_ComCurrent_Down"] = self.lineEdit_setComCurrentBottom.text()
    
    def openConfigRecord(self):
        try:
            with open("config_save_record.txt", "rb") as fsrf:
                ofr = pk.load(fsrf) # 将二进制文件对象转换成Python对象
                # print("openConfigRecord:" + str(ofr))
            self.isConfigSavedFirst = ofr[0][0]
            self.isConfigSaved = ofr[0][1]
            self.configPath = ofr[1]
        except:
            pass

    def saveConfigRecord(self):
        self.saved_info = ([self.isConfigSavedFirst, self.isConfigSaved],  self.configPath)
        with open("config_save_record.txt", "wb") as fsrf:
            pk.dump(self.saved_info, fsrf) # 用dump函数将Python对象转成二进制对象文件
        # print("saveConfigRecord:" + str(self.saved_info))

    @QtCore.pyqtSlot()
    def on_lineEdit_setDrainCurrentTop_textChanged(self):
        if self.lineEdit_setDrainCurrentTop.text() != paraDict["th_DrainCurrent_Up"]:
            self.isConfigSaved = False
        else:
            self.isConfigSaved = True
        self.saveConfigRecord()
 
    def parseSettingThreshold(self):
        tmp = self.data.decode("utf-8")
        res = tmp[3:(len(tmp)-4)]
        if res == "PARAOK":
            self.userTextBrowserAppend("控制仪接收参数成功")
        elif res == "PARAERR":
            self.userTextBrowserAppend("控制仪接收参数失败")
        elif res == "PARALESS":
            self.userTextBrowserAppend("控制仪接收参数缺失")
        QApplication.processEvents()
    
    def settingThreshold(self):
        if self.prvSerial.isOpen():
            self.data = b''
            self.rxCheck = 0
            self.prvSerial.flush()
            self.serialSendData(Func.f_DevSettingThreshold)
            startTiming = dt.datetime.now()
            while True:
                QApplication.processEvents()
                try:
                    self.num = self.prvSerial.inWaiting()
                    # print("settingThreshold num:" + str(self.num)) # 输出收到的字节数
                    if self.num == 0:
                        endTiming = dt.datetime.now()
                        if (endTiming - startTiming).seconds >= 180:
                            self.userTextBrowserAppend("设定阈值@接收数据超时")
                            return
                        else:
                            continue
                    elif self.num > 0 and self.num <= 4:
                        self.prvSerial.flushInput()
                    else:
                        time.sleep(0.1)
                        self.num = self.prvSerial.inWaiting()
                        if self.num >= 13:
                            break
                except:
                    self.userTextBrowserAppend("设定阈值@接收数据失败")
                    return
            QApplication.processEvents()
            self.data = self.prvSerial.read(self.num)
            print("settingThreshold:" + str(self.data, encoding="utf-8") + "self.num:{}".format(self.num))
            if self.rxFrameCheck() == State.s_RxFrameCheckOK:
                self.parseSettingThreshold()   
            else:
                self.userTextBrowserAppend("设定阈值@接收帧错误")     
            self.prvSerial.flushInput()
        else:
            self.userTextBrowserAppend("下发阈值@串口未打开")
    
    def firstSaveThreshold(self, text):
        if self.configPath == "":
            self.configPath, isAccept =  QFileDialog.getSaveFileName(self, "保存文件", "./config", "settingfiles (*.txt)")
            if isAccept:
                if self.configPath:
                    with open(self.configPath, "w") as fsf:
                        fsf.write(text)
                    self.isConfigSavedFirst = False
                    self.isConfigSaved = True
                self.userTextBrowserAppend("参数保存成功")
                self.textBrowser.append("@保存至\"" + str(self.configPath) + "\"")
                self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
                self.saveConfigRecord()
                print(self.usualTools.getTimeStamp() + "下发参数\n")
                self.settingThreshold()
        else:
            pass

    def saveThreshold(self, text):
        with open(self.configPath, encoding="utf-8", mode="w") as sf:
            sf.write(text)
        self.isConfigSaved = True
        self.userTextBrowserAppend("保存配置参数成功")
        print(self.usualTools.getTimeStamp() + "下发参数\n")
        self.settingThreshold()
        self.saveConfigRecord()

    @QtCore.pyqtSlot()
    def on_pushBtn_saveSettingsRecord_clicked(self):
        print("/*>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>*/")
        print("Setting parameters's threshold ......")
        print(self.usualTools.getTimeStamp() + "获取界面参数\n")
        self.getUserPara()
        print(self.usualTools.getTimeStamp() + "保存参数\n")
        cnt = 0
        self.para = ""
        for k, v in paraDict.items():
            if cnt < 10:
                self.para = self.para + ("P" + str(cnt) + v)
            elif cnt == 10:
                self.para = self.para + ("PA" + v)
            elif cnt == 11:
                self.para = self.para + ("PB" + v)
            elif cnt == 12:
                self.para = self.para + ("PC" + v)
            elif cnt == 13:
                self.para = self.para + ("PD" + v)
            elif cnt == 14:
                self.para = self.para + ("PE" + v)
            elif cnt == 15:
                self.para = self.para + ("PF" + v)
            cnt += 1
        self.openConfigRecord()
        if self.isConfigSavedFirst:
            self.firstSaveThreshold(self.para)
        elif self.isConfigSaved:
            self.saveThreshold(self.para)
        
    @QtCore.pyqtSlot()
    def on_pushBtn_readSettingsRecord_clicked(self):        
        settingfile, _ = QFileDialog.getOpenFileName(self, "打开配置文件", './', 'settingfile (*.txt)')
        if settingfile:
            os.startfile(settingfile)
            self.isConfigSaved = True
            self.saveConfigRecord()

    def updateWorkMode(self, str):
        print("In updateWorkMode...............")
        QApplication.processEvents()
        endc = str[1]
        dete = str[2]
        if endc == "0":
            self.workMode["encoding"] = "0"
        else:
            self.workMode["encoding"] = "1"
        if dete == "0":
            self.workMode["detection"] = "0"
        else:
            self.workMode["detection"] = "1"
        if str[0] == "X":
            if endc == "0":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
                self.userTextBrowserAppend("编码发生改变，编码【关闭】")
            elif endc == "1":
                self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
                self.userTextBrowserAppend("编码发生改变，编码【开启】")
        elif str[0] == "Y":
            if dete == "0":
                self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/OFF)}")
                self.userTextBrowserAppend("检测发生改变，检测【关闭】")
            elif dete == "1":
                self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/ON)}")
                self.userTextBrowserAppend("检测发生改变，检测【开启】")
        elif str[0] == "Z":
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
        self.setWorkMode(self.data)
        tmp = self.data.decode("utf-8")
        PwrVol  = tmp[3:6]
        PwrCur  = tmp[6:10]
        ComVol  = tmp[10:13]
        ComCur  = tmp[13:17]
        FireVol = tmp[17:20]
        FireCur = tmp[20:24]
        self.label_selfLineVoltage.setText(PwrVol[0:2] + "." + PwrVol[2:3])
        self.label_selfLineCurrent.setText(PwrCur[0:1] + "." + PwrCur[1:4])
        self.label_selfComVoltage.setText(ComVol[0:2] + "." + ComVol[2:3])
        self.label_selfComCurrent.setText(ComCur[0:1] + "." + ComCur[1:4])
        self.label_selfFireVoltage.setText(FireVol[0:2] + "." + FireVol[2:3])
        self.label_selfFireCurrent.setText(FireCur[0:1] + "." + FireCur[1:4])
        self.userTextBrowserAppend("已获取控制仪参数")

    def getDevicePara(self):
        print("/*+++++++++++++++++++++++++++++++++++++++++++++*/")
        print("Checking device parameters ......")
        self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")
        self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")
        self.workMode = {"encoding": "X",  "detection": "X"} # 未知状态
        if self.prvSerial.isOpen:
            self.data = b''
            self.rxCheck = 0
            self.prvSerial.flush()
            self.serialSendData(Func.f_DevGetSelfPara)
            startTiming = dt.datetime.now()
            while True:
                QApplication.processEvents()
                try:
                    self.num = self.prvSerial.inWaiting()
                    # print(self.num) # 输出收到的字节数
                    if self.num == 0:
                        endTiming = dt.datetime.now()
                        if (endTiming - startTiming).seconds >= 6:
                            self.userTextBrowserAppend("控制仪自检@接收数据超时，工作模式未知")
                            return
                        else:
                            continue
                    elif self.num > 0 and self.num <= 4:
                        self.prvSerial.flushInput()
                    else:
                        time.sleep(0.01)
                        self.num = self.prvSerial.inWaiting()
                        if self.num >= 30:
                            break
                        elif self.num == 14:
                            break
                except:
                    self.userTextBrowserAppend("控制仪自检@接收数据失败")
                    return
            self.data = self.prvSerial.read(self.num)
            print("getDevicePara:" + str(self.data, encoding="utf-8") + "self.num:{}".format(self.num))
            if self.data.decode("utf-8")[2] != "N":
                if self.rxFrameCheck() == State.s_RxFrameCheckOK:  # 接收帧检查
                    self.parseDevicPara()
                    self.parseWorkMode()
                else:
                    self.userTextBrowserAppend("控制仪自检@接收帧错误")
            else:
                self.userTextBrowserAppend("请接通控制仪电源")
            self.prvSerial.flushInput()

        else:
            self.userTextBrowserAppend("串口未打开")

    @QtCore.pyqtSlot()
    def on_pushBtn_deviceSelfCheck_clicked(self):
        if self.prvSerial.isOpen() == True:
            self.userTextBrowserAppend("控制仪自检")
            self.getDevicePara()
        else:
            QMessageBox.information(self, "串口信息", "串口未打开\n请打开串口", QMessageBox.Yes)

    def parseEncodingResults(self):
        res = ""
        tmp = self.data.decode("utf-8")
        # print("tmp:" + tmp)
        res = tmp[3:(len(tmp) - 4)]
        if tmp.find("UID"):
            if res == "UIDOK":
                self.userTextBrowserAppend("写入UID成功")
            elif res == "UIDERR":
                self.userTextBrowserAppend("写入UID失败")
        elif res == "FACULTY":
            self.userTextBrowserAppend("模块已出故障，请更换模块！")
        elif res == "NCODE":
            self.workMode["encoding"] = "0"
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/close)}")
            self.userTextBrowserAppend("无法进行编码，请检查编码按键")
    
    @QtCore.pyqtSlot()
    def on_pushBtn_deviceEncoding_clicked(self):
        if self.workMode["encoding"] == "1":
            print("/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/")
            print("Encoding......")
            self.userTextBrowserAppend("模块编码")
            if self.prvSerial.isOpen():
                if self.lineEdit_uidInput.text() != "":
                    self.userTextBrowserAppend("输入UID：" + self.lineEdit_uidInput.text())
                    self.data = b''
                    self.rxCheck = 0
                    self.prvSerial.flushOutput()
                    self.serialSendData(Func.f_DevEncoding)
                    startTiming = dt.datetime.now()
                    while True:
                        QApplication.processEvents()
                        try:
                            self.num = self.prvSerial.inWaiting()
                            if self.num == 0:
                                endTiming = dt.datetime.now()
                                if (endTiming - startTiming).seconds >= 10:
                                    self.userTextBrowserAppend("模块编码@接收数据超时")
                                    return
                                else:
                                    continue
                            elif self.num > 0 and self.num <= 4:
                                self.prvSerial.flushInput()
                            else:
                                time.sleep(0.01)
                                self.num = self.prvSerial.inWaiting()
                                if self.num >= 12:
                                    break
                        except:
                            self.userTextBrowserAppend("模块编码@接收数据失败")
                            return
                    self.data = self.prvSerial.read(self.num)
                    print("encoding:" + str(self.data, encoding="utf-8") + "self.num:{}".format(self.num))
                    if self.rxFrameCheck() == State.s_RxFrameCheckOK:  # 接收帧检查
                        self.parseEncodingResults()
                    else:
                        self.userTextBrowserAppend("模块编码@接收帧错误")
                    self.prvSerial.flushInput()
                else:
                    self.userTextBrowserAppend("输入编号为空！")
            else:
                self.userTextBrowserAppend("串口未打开")
        else:
            self.userTextBrowserAppend("编码【未开启】")

    def parseDetectionResults(self):
        res = ""
        tmp = self.data.decode("utf-8")
        res = tmp[3:11]
        if res == "LVERLCER":
            self.userTextBrowserAppend("线路电流超限，线路电压超限")
        elif res == "LVOKLCER":
            self.userTextBrowserAppend("线路电压正常，线路电流超限")
        elif res == "LVERLCOK":
            self.userTextBrowserAppend("线路电压超限，线路电流正常")
        elif res == "LVOKLCOK":
            self.userTextBrowserAppend("线路电压正常，线路电流正常")
            self.label_resDrainCurrent.setText(tmp[13:15] + "." + tmp[15:16])
            self.label_resWorkCurrent.setText(tmp[18:21] + "." + tmp[21:22])
            self.resultCurrentList[0] = self.name
            self.resultCurrentList[1] = self.detectionTime
            self.resultCurrentList[2] = tmp[13:15] + "." + tmp[15:16]
            self.resultCurrentList[3] = tmp[18:21] + "." + tmp[21:22]
            # 被测模块
            self.label_resIdCheck.setText("完成")
            self.label_resOnlineCheck.setText("在线")
            self.label_resExDetID.setText(tmp[24:29])
            self.label_resExDetVoltage.setText(tmp[83:85] + "." + tmp[85:86])
            self.label_resExDetCurrent.setText(tmp[89:len(tmp)-4])
            self.resultCurrentList[4] = "成功"
            self.resultCurrentList[5] = "在线"
            self.resultCurrentList[6] = tmp[24:29]
            self.resultCurrentList[7] = tmp[89:len(tmp)-4]
            self.resultCurrentList[8] = tmp[83:85] + "." + tmp[85:86]
            self.resultCurrentList[9] = "正常"
            self.label_resExDetCurrentJudge.setText(self.resultCurrentList[9])
            # 内置模块
            self.label_resInDetID.setText(tmp[47:52])
            self.label_resInDetVoltage.setText(tmp[63:65] + "." + tmp[65:66])
            self.label_resInDetCurrent.setText(tmp[69:72])
            self.resultCurrentList[10] = tmp[47:52]
            self.resultCurrentList[11] = tmp[69:72]
            self.resultCurrentList[12] = tmp[63:65] + "." + tmp[65:66]
            self.resultCurrentList[13] = "正常"
            self.resultCurrentList[14] = "通过"
            # 更新model
            for col in range(15):
                item = QStandardItem(self.resultCurrentList[col])
                self.tableViewModel.setItem(self.tableRow, col, item)
            self.label_resInDetCurrentJudge.setText(self.resultCurrentList[13])
            self.label_finalResult.setText("PASSED")
        elif tmp[3:8] == "NDETE":
            self.workMode["detection"] = "0"
            self.userTextBrowserAppend("无法进行检测，请检查检测按键")

    @QtCore.pyqtSlot()
    def on_pushBtn_deviceDetection_clicked(self):
        if self.workMode["detection"] == "1":
            print("/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/")
            print("Detecting......")
            self.detectionTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.userTextBrowserAppend("模块检测")
            if self.prvSerial.isOpen():
                if self.lineEdit_uidInput.text() != "":
                    self.userTextBrowserAppend("输入UID：" + self.lineEdit_uidInput.text())
                    self.data = b""
                    self.rxCheck = 0
                    self.prvSerial.flushOutput()
                    self.serialSendData(Func.f_DevDetection)
                    startTiming = dt.datetime.now()
                    while True:
                        QApplication.processEvents()
                        try:
                            self.num = self.prvSerial.inWaiting()
                            if self.num == 0:
                                endTiming = dt.datetime.now()
                                QApplication.processEvents() 
                                if (endTiming - startTiming).seconds >= 30:
                                    self.userTextBrowserAppend("模块检测@接收数据超时")
                                    return
                                else:
                                    continue
                            elif self.num > 0 and self.num <= 4:
                                self.prvSerial.flushInput()
                            else:
                                time.sleep(0.01)
                                self.num = self.prvSerial.inWaiting()
                                if self.num >= 70:
                                    break
                        except:
                            QApplication.processEvents() 
                            self.userTextBrowserAppend("模块检测@接收数据失败")
                            return
                    self.data = self.prvSerial.read(self.num)
                    print("detection:" + str(self.data, encoding="utf-8") + "self.num:{}".format(self.num))
                    if self.rxFrameCheck() == State.s_RxFrameCheckOK:  # 接收帧检查
                        self.parseDetectionResults()
                    else:
                        self.userTextBrowserAppend("模块检测@接收帧错误")
                    self.prvSerial.flushInput()
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
        diffDef = set(self.resultCurrentList).difference(set(self.resultDefaultList))
        diffDet = set(self.resultCurrentList).difference(set(self.resultLastList))
        if diffDef == set() and diffDet == set():
            return -1
        elif diffDef != set() and diffDet == set():
            return 0
        elif diffDef != set() and diffDet != set():
            return 1    
            
    def firstSaveResults(self):
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
                        self.excel.wrtieRow(self.excelFile, self.resultCurrentList)
                        # for col in range(15):
                        #     item = QStandardItem(self.resultCurrentList[col])
                        #     self.tableViewModel.setItem(0, col, item)
                        self.tableRow = self.tableRow + 1
                        self.isExcelSaved = True
                        self.currentResultSaved = True
                        self.saveExcelRecord()
                    elif res == 0:
                        self.userTextBrowserAppend("当前检测结果已记录，请重新进行编码和检测")  
                    elif res == -1:
                        self.userTextBrowserAppend("未有检测结果，请进行编码和检测")
                    self.resultLastList = self.resultCurrentList.copy()
                    QApplication.processEvents() 
                else:
                    pass
        else:
            pass

    def SaveResults(self):
        self.openExcelRecord()
        res = self.compareResult()
        if res == 1:
            self.excel.wrtieRow(self.excelFile, self.resultCurrentList)
            self.userTextBrowserAppend("保存数据记录表成功")
            # for col in range(15):
            #     item = QStandardItem(self.resultCurrentList[col])
            #     self.tableViewModel.setItem(0, col, item)
            self.tableRow = self.tableRow + 1
            self.isExcelSaved = True
            self.currentResultSaved = True
            self.saveExcelRecord()
        elif res == 0:
            self.userTextBrowserAppend("当前检测结果已记录，请重新进行编码和检测")  
        elif res == -1:
            self.userTextBrowserAppend("未有检测结果，请进行编码和检测")
        self.resultLastList = self.resultCurrentList.copy()
        QApplication.processEvents()

    @QtCore.pyqtSlot()
    def on_pushBtn_clearResults_clicked(self):
        self.tableRow = 0
        self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())

    @QtCore.pyqtSlot()
    def on_pushBtn_saveResults_clicked(self):
        self.openExcelRecord()
        if self.isExcelSavedFirst:
            self.firstSaveResults()
        elif self.isExcelSaved:
            self.SaveResults()

    @QtCore.pyqtSlot()
    def on_pushBtn_showResults_clicked(self):
        self.openExcelRecord()
        recordsfile, _ = QFileDialog.getOpenFileName(self, "打开记录文件", './', 'records (*.xlsx)')
        if recordsfile:
                os.startfile(recordsfile)
                self.isConfigSaved = True
        self.saveExcelRecord()     

    @QtCore.pyqtSlot()
    def on_pushBtn_deviceEncodingDetection_clicked(self):
        self.userTextBrowserAppend("执行编码和检测")
        if self.prvSerial.isOpen():
            self.on_pushBtn_deviceEncoding_clicked()
            time.sleep(0.2)
            self.on_pushBtn_deviceDetection_clicked()
        else:
            self.userTextBrowserAppend("串口未打开")

    @QtCore.pyqtSlot()
    def on_pushBtn_clearUidInput_clicked(self):
        self.lineEdit_uidInput.clear()
        
    def closeEvent(self, QCloseEvent):
        if not self.isConfigSaved:
            choice = QMessageBox.question(self, "保存文件", "是否保存配置文件", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:               # 6
                QCloseEvent.accept()
                self.firstSaveThreshold()
                app = QApplication.instance()
                app.quit()
            elif choice == QMessageBox.No:
                QCloseEvent.accept()
            else:
                QCloseEvent.ignore()

if __name__ == "__main__":
    mainApp = QApplication(sys.argv)
    root = QFileInfo(__file__).absolutePath()
    mainApp.setWindowIcon(QIcon(root + "/resources/icons/robot.ico"))
    Terminal = MainWin()
    Terminal.show()
    sys.exit(mainApp.exec_())