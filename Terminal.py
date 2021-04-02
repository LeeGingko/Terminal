# -*- coding: utf-8 -*-
from UserImport import *

class MainWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWin, self).__init__()  # 继承父类的所有属性

        # 自定义工具实例化
        self.usualTools = Tools()

        # self.btnQss = "QPushButton {color:blue; background-color:#FCFCFC}"

        # 初始化UI
        self.initUi()

        # 绑定控件信号和槽函数
        self.bindSignalSlot()
        
        # 消息保存
        self.is_message_saved_first = True
        self.is_message_saved = True
        self.messagePath = ""

        # 工作模式初始化
        self.workMode = {"encoding": "X",  "detection": "X"} # 未知状态
        self.data = b''

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
        self.portDetection() # 检测端口并加入combobox
        self.serialManager.start()
        self.serialManager.recvSignal.connect(self.updateWorkMode)

        # 操作人员姓名录入
        self.is_name_input = False
        self.name = "武则天" # 默认操作员姓名
        self.nameInputThread = GetNameThread()
        self.nameInputThread.inputNameSignal.connect(self.operatorNameCheck)
        self.nameInputThread.start()
        self.userTextBrowserAppend("请输入操作员姓名，20秒内未输入自动填入。")
        
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
        self.userTextBrowserAppend("读取默认配置")
        self.getUserPara()

        # 配置文件保存变量的初始化
        self.is_config_saved_first = True # 是否是第一次保存
        self.is_config_saved = True # 是否是已经保存 
        self.configPath = "" # 文件路径

        # 测试数据Excel文件保存变量的初始化
        self.excel = PersonalExcel() # Excel实例化全局对象
        self.is_excel_saved_first = True
        self.is_excel_saved = True
        self.excelFilePath = "" # 文件路径
        self.excel_file = ""
        self.table_headline = [
            "测试员", "时间",      "漏电流(uA)", "工作电流(uA)", "ID核对",
            "在线检测", "被测选发",   "电流(mA)",  "电压(V)",      "电流判断",
            "内置选发", "电流(mA)",  "电压(V)",   "电流判断",      "结论" ]
        initTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.resultListDefault = [
            self.name, initTime,   "0.0",  "0.0",  "成功",
              "在线",   "FFFFF",    "0",    "0",   "正常",
             "23456",    "0",      "0",    "正常", "通过" ]
        self.resultList = [
            self.name, initTime,   "0.0",  "0.0",  "成功",
              "在线",   "FFFFF",    "0",    "0",   "正常",
             "23456",    "0",      "0",    "正常", "通过" ]   
        # 检测数据显示表格模型初始化
        self.tableViewModel = QStandardItemModel(1, 15, self)
        self.tableViewModel.setHorizontalHeaderLabels(self.table_headline)
        self.tableView_result.setModel(self.tableViewModel)
        self.tableView_result.horizontalHeader().setStretchLastSection(True)
        # self.tableView_result.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView_result.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # 表格视图委托初始化
        self.tableViewDelegate = TableViewDelegate()
        self.tableView_result.setItemDelegate(self.tableViewDelegate)
        self.tableRow = 0
        # 
        self.first_auto_detetion = 1
    
    def __del__(self):
        if self.prvSerial.isOpen():
            self.prvSerial.close()
        self.excel.closeFile
        print("{} 程序结束，释放资源".format(__class__))

    def initUi(self):
        self.setupUi(self)

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
        self.setWindowIcon(QIcon("resources/icons/robot.ico"))
        # self.setStyleSheet("QMainWindow {background-color:#FCFCFC}")

        # 检测以及编码默认状态设置
        self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")
        self.label_encoding.setStyleSheet("QLabel{border-image: url(:/icons/NONE)}")

        # 消息提示窗口初始化
        self.textBrowser.setFontFamily("微软雅黑")
        self.textBrowser.setFontPointSize(12)
        # self.textBrowser.setStyleSheet("QTextBrowser {color:#0055FF; background-color:#FCFCFC}")
        self.userTextBrowserAppend("请先接入被测模块再进行操作")

    def bindSignalSlot(self):
        self.pushBtn_serialSwitch.clicked.connect(self.switchPort)
        self.pushBtn_clearUidInput.clicked.connect(self.clearUidInput)
        self.pushBtn_cleanMsgArea.clicked.connect(self.clearMessage)
        self.pushBtn_saveMsgArea.clicked.connect(self.userSaveMessage)
        self.pushBtn_deviceSelfCheck.clicked.connect(self.deviceSelfCheck)
        self.pushBtn_deviceEncoding.clicked.connect(self.encoding)
        self.pushBtn_deviceDetection.clicked.connect(self.detection)
        self.pushBtn_saveSettingsRecord.clicked.connect(self.userSaveThreshold)
        self.pushBtn_readSettingsRecord.clicked.connect(self.userOpenThreshold)
        self.pushBtn_saveResults.clicked.connect(self.userSaveResults)
        self.pushBtn_showResults.clicked.connect(self.userCheckResults)
        self.pushBtn_clearResults.clicked.connect(self.clearShowResult)
        self.pushBtn_deviceEncodingDetection.clicked.connect(self.encodingDetection)
        self.lineEdit_setDrainCurrentTop.textChanged.connect(self.paraChanged)
        self.lineEdit_uidInput.returnPressed.connect(self.encoding)

    def userTextBrowserAppend(self, str):
        self.textBrowser.append(self.usualTools.getTimeStamp() + str)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)

    def operatorNameCheck(self, str):
        if str == "sec":
            # if self.lineEdit_op_name.text() != "":
            #         self.name = self.lineEdit_op_name.text()
            #         if self.lineEdit_op_name.returnPressed:
            #             self.userTextBrowserAppend("当前操作员：" + self.name)
            #             self.lineEdit_op_name.setText(self.name)
            #             self.is_name_input = True
            pass
        else:
            self.userTextBrowserAppend("默认操作员：" + self.name)
            self.is_name_input = True
            self.lineEdit_op_name.setText(self.name)
            self.nameInputThread.quit()
    
    def openMessageRecord(self):
        try:
            with open("message_save_record.txt", "rb") as msrf:
                omr = pk.load(msrf) # 将二进制文件对象转换成Python对象
                # print("openConfigRecord:" + str(ofr))
            self.is_message_saved_first = omr[0][0]
            self.is_message_saved = omr[0][1]
            self.messagePath = omr[1]
        except:
            pass

    def saveMessageRecord(self):
        self.saved_info = ([self.is_message_saved_first, self.is_message_saved],  self.messagePath)
        with open("message_save_record.txt", "wb") as fsmf:
            pk.dump(self.saved_info, fsmf) # 用dump函数将Python对象转成二进制对象文件
        # print("saveConfigRecord:" + str(self.saved_info))

    def clearMessage(self):
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
                    self.is_message_saved_first = False
                    self.is_message_saved = True
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
    
    def userSaveMessage(self):
        self.openMessageRecord()
        if self.is_message_saved_first:
            self.firstSaveMessage()
        elif self.is_message_saved:
            self.saveMessage()

    def showDaetTime(self, timeStr):
        self.label_localDateTime.setText(timeStr)
    
    def portDetection(self):
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
        else:
            print("No port detected!")
            # self.statusbar.showMessage("未检测到串口")
            self.userTextBrowserAppend("未检测到串口，请连接备")
            QMessageBox.information(self, "串口信息", "未检测到串口!", QMessageBox.Yes)

    def switchPort(self):
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
                    time.sleep(1)
                    if self.prvSerial.isOpen(): 
                        startTiming = dt.datetime.now()
                        self.prvSerial.write(bytes("Terminal\r\n", encoding="utf-8"))
                        while True:
                                QApplication.processEvents()
                                num = self.prvSerial.inWaiting()
                                # print("switchPort num:" + str(num)) # 输出收到的字节数
                                endTiming = dt.datetime.now()
                                if num == 0:
                                    if (endTiming - startTiming).seconds >= 5:
                                        QApplication.processEvents()
                                        self.userTextBrowserAppend("控制仪无响应，请执行操作")
                                        break
                                elif (num > 0 and num <= 4):
                                    self.prvSerial.flushInput()
                                elif num >= 5:
                                    time.sleep(0.1)
                                    data = self.prvSerial.read(num)
                                    if data.decode("utf-8") == "STM32":
                                        QApplication.processEvents()
                                        self.userTextBrowserAppend("控制仪在线，请执行操作")
                                        if self.first_auto_detetion == 1:
                                            self.first_auto_detetion = 0
                                            self.deviceSelfCheck() # 每次运行程序执行一次自检即可
                                        break
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
            self.is_config_saved_first = ofr[0][0]
            self.is_config_saved = ofr[0][1]
            self.configPath = ofr[1]
        except:
            pass

    def saveConfigRecord(self):
        self.saved_info = ([self.is_config_saved_first, self.is_config_saved],  self.configPath)
        with open("config_save_record.txt", "wb") as fsrf:
            pk.dump(self.saved_info, fsrf) # 用dump函数将Python对象转成二进制对象文件
        # print("saveConfigRecord:" + str(self.saved_info))

    def paraChanged(self):
        if self.lineEdit_setDrainCurrentTop.text() != paraDict["th_DrainCurrent_Up"]:
            self.is_config_saved = False
        else:
            self.is_config_saved = True
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
            # self.prvSerial.flush()
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
                            QApplication.processEvents()
                            self.userTextBrowserAppend("设定阈值@接收数据超时")
                            break
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
                    QApplication.processEvents()
                    self.userTextBrowserAppend("设定阈值@接收数据失败")
                    break
            if self.num >= 13:
                QApplication.processEvents()
                self.data = self.prvSerial.read(self.num)
                print("settingThreshold:" + str(self.data, encoding="utf-8") + "self.num:{}".format(self.num))
                self.rxFrameCheck()
                self.parseSettingThreshold()
                self.prvSerial.flushInput()
            else:
                pass
        else:
            self.userTextBrowserAppend("下发阈值@串口未打开")
    
    def firstSaveThreshold(self, text):
        if self.configPath == "":
            self.configPath, isAccept =  QFileDialog.getSaveFileName(self, "保存文件", "./config", "settingfiles (*.txt)")
            if isAccept:
                if self.configPath:
                    with open(self.configPath, "w") as fsf:
                        fsf.write(text)
                    self.is_config_saved_first = False
                    self.is_config_saved = True
                self.userTextBrowserAppend("参数保存成功")
                self.textBrowser.append("@保存至\"" + str(self.configPath) + "\"")
                self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
                self.saveConfigRecord()
                print(self.usualTools.getTimeStamp() + "下发参数\n")
                self.settingThreshold()
        else:
            pass

    def saveThreshold(self, text):
        with open(self.configPath, 'w') as sf:
            sf.write(text)
        self.is_config_saved = True
        self.userTextBrowserAppend("保存配置参数成功")
        print(self.usualTools.getTimeStamp() + "下发参数\n")
        self.settingThreshold()
        self.saveConfigRecord()

    def userSaveThreshold(self):
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
        if self.is_config_saved_first:
            self.firstSaveThreshold(self.para)
        elif self.is_config_saved:
            self.saveThreshold(self.para)
        
    def userOpenThreshold(self):
        settingfile, _ = QFileDialog.getOpenFileName(self, "打开配置文件", './', 'settingfile (*.txt)')
        if settingfile:
            os.startfile(settingfile)
            self.is_config_saved = True
            self.saveConfigRecord()

    def updateWorkMode(self, str):
        # print("In updateWorkMode...............")
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
            self.prvSerial.flushOutput()
            self.serialSendData(Func.f_DevGetSelfPara)
            startTiming = dt.datetime.now()
            while True:
                QApplication.processEvents()
                try:
                    self.num = self.prvSerial.inWaiting()
                    # print(self.num) # 输出收到的字节数
                    if self.num == 0:
                        QApplication.processEvents()
                        endTiming = dt.datetime.now()
                        if (endTiming - startTiming).seconds >= 6:
                            QApplication.processEvents()
                            self.userTextBrowserAppend("控制仪自检@接收数据超时，工作模式未知")
                            break
                        else:
                            continue
                    elif self.num > 0 and self.num <= 4:
                        self.prvSerial.flushInput()
                    else:
                        time.sleep(0.01)
                        self.num = self.prvSerial.inWaiting()
                        if self.num >= 30:
                            break
                except:
                    QApplication.processEvents()
                    self.userTextBrowserAppend("控制仪自检@接收数据失败")
                    break
            if self.num >= 30:
                QApplication.processEvents()
                self.data = self.prvSerial.read(self.num)
                print("getDevicePara:" + str(self.data, encoding="utf-8") + "self.num:{}".format(self.num))
                if self.rxFrameCheck() == State.s_RxFrameCheckOK:  # 接收帧检查
                    self.parseDevicPara()
                    self.parseWorkMode()
                else:
                    QApplication.processEvents()
                    self.userTextBrowserAppend("接收帧错误")
                self.prvSerial.flushInput()
            else:
                pass
        else:
            self.userTextBrowserAppend("串口未打开")

    def deviceSelfCheck(self):
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

    def encoding(self):
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
                                    QApplication.processEvents()
                                    self.userTextBrowserAppend("模块编码@接收数据超时")
                                    break
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
                            QApplication.processEvents()
                            self.userTextBrowserAppend("模块编码@接收数据失败")
                            break
                    if self.num >= 12:
                        QApplication.processEvents()
                        self.data = self.prvSerial.read(self.num)
                        print("encoding:" + str(self.data, encoding="utf-8") + "self.num:{}".format(self.num))
                        self.rxFrameCheck()  # 接收帧检查
                        self.parseEncodingResults()
                        self.prvSerial.flushInput()
                    else:
                        pass
                else:
                    self.userTextBrowserAppend("输入编号为空！")
            else:
                self.userTextBrowserAppend("串口未打开")
        else:
            self.userTextBrowserAppend("编码【未开启】")

    def parseDetectionResults(self):
        QApplication.processEvents() 
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
            self.resultList[0] = self.name
            self.resultList[1] = self.detectionTime
            self.resultList[2] = tmp[13:15] + "." + tmp[15:16]
            self.resultList[3] = tmp[18:21] + "." + tmp[21:22]
            # 被测模块
            self.label_resIdCheck.setText("完成")
            self.label_resOnlineCheck.setText("在线")
            self.label_resExDetID.setText(tmp[24:29])
            self.label_resExDetVoltage.setText(tmp[83:85] + "." + tmp[85:86])
            self.label_resExDetCurrent.setText(tmp[89:len(tmp)-4])
            self.resultList[4] = "成功"
            self.resultList[5] = "在线"
            self.resultList[6] = tmp[24:29]
            self.resultList[7] = tmp[89:len(tmp)-4]
            self.resultList[8] = tmp[83:85] + "." + tmp[85:86]
            self.resultList[9] = "正常"
            self.label_resExDetCurrentJudge.setText(self.resultList[9])
            # 内置模块
            self.label_resInDetID.setText(tmp[47:52])
            self.label_resInDetVoltage.setText(tmp[63:65] + "." + tmp[65:66])
            self.label_resInDetCurrent.setText(tmp[69:72])
            self.resultList[10] = tmp[47:52]
            self.resultList[11] = tmp[69:72]
            self.resultList[12] = tmp[63:65] + "." + tmp[65:66]
            self.resultList[13] = "正常"
            self.resultList[14] = "通过"
            # 更新model
            for col in range(15):
                item = QStandardItem(self.resultList[col])
                self.tableViewModel.setItem(self.tableRow, col, item)
            self.label_resInDetCurrentJudge.setText(self.resultList[13])
            self.label_finalResult.setText("PASSED")
        elif tmp[3:8] == "NDETE":
            self.workMode["detection"] = "0"
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/icons/close)}")
            self.userTextBrowserAppend("无法进行检测，请检查检测按键")
        QApplication.processEvents() 

    def detection(self):
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
                                    QApplication.processEvents()
                                    self.userTextBrowserAppend("模块检测@接收数据超时")
                                    break
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
                            break
                    if self.num >= 70:
                        QApplication.processEvents()
                        self.data = self.prvSerial.read(self.num)
                        print("detection:" + str(self.data, encoding="utf-8") + "self.num:{}".format(self.num))
                        self.rxFrameCheck()  # 接收帧检查
                        self.parseDetectionResults()
                        self.prvSerial.flushInput()
                    else:
                        pass
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
            self.is_excel_saved_first = oer[0][0]
            self.is_excel_saved = oer[0][1]
            self.excelFilePath = oer[1]
            self.excel_file = os.path.split(self.excelFilePath)[1]
        except:
            pass
    
    def saveExcelRecord(self):
        self.saved_info = ([self.is_excel_saved_first, self.is_excel_saved],  self.excelFilePath)
        with open("excel_save_record.txt", "wb") as esrf:
            pk.dump( self.saved_info, esrf) # 用dump函数将Python对象转成二进制对象文件
        # print("saveExcelRecord:" + str(self.saved_info))

    def compareResult(self):
        a = self.resultListDefault
        b = self.resultList
        cnt = 0
        for i in range(15):
            if a[i] == b[i]:
                cnt += 1
            else:
                return -1
        return cnt
            
    def firstSaveResults(self):
        if self.excelFilePath == "":
            self.excelFilePath, isAccept =  QFileDialog.getSaveFileName(self, "保存文件", "./recording", "recorded data(*.xlsx)")
            if isAccept:
                if self.excelFilePath:
                    self.excel_file = os.path.split(self.excelFilePath)[1]
                    self.excel_sheet = "record sheet"
                    self.excel.initWorkBook(self.excel_file, self.excel_sheet)
                    self.is_excel_saved_first = False
                    self.is_excel_saved = True
                    self.excel.wrtieRow(self.excel_file, self.table_headline) # 添加表头
                    self.userTextBrowserAppend("创建数据记录表成功")
                    self.textBrowser.append("@保存至\"" + str(self.excelFilePath) + "\"")
                    self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
                    res = self.compareResult()
                    if res == -1:
                        self.excel.wrtieRow(self.excel_file, self.resultList)
                        for col in range(15):
                            item = QStandardItem(self.resultList[col])
                            self.tableViewModel.setItem(0, col, item)
                        self.tableRow = self.tableRow + 1
                        self.is_excel_saved = True
                    else:
                        self.userTextBrowserAppend("未有检测结果，请进行检测")
                    self.saveExcelRecord()
                    QApplication.processEvents() 
                else:
                    pass
        else:
            pass

    def SaveResults(self):
        self.openExcelRecord()
        res = self.compareResult()
        if res == -1:
            self.excel.wrtieRow(self.excel_file, self.resultList)
            self.userTextBrowserAppend("数据记录表保存成功")
            self.is_excel_saved = True
            self.saveExcelRecord()
            self.tableRow = self.tableRow + 1
        else:
            self.userTextBrowserAppend("未有检测结果，请进行检测")
        QApplication.processEvents()

    def clearShowResult(self):
        # print("clearShowResult")
        self.tableRow = 0
        self.tableViewModel.removeRows(0, self.tableViewModel.rowCount())

    def userSaveResults(self):
        self.openExcelRecord()
        if self.is_excel_saved_first:
            self.firstSaveResults()
        elif self.is_excel_saved:
            self.SaveResults()

    def userCheckResults(self):
        self.openExcelRecord()
        recordsfile, _ = QFileDialog.getOpenFileName(self, "打开记录文件", './', 'records (*.xlsx)')
        if recordsfile:
            # with open(recordsfile, 'r') as of:
                # print(of.read())
                os.startfile(recordsfile)
                self.is_config_saved = True
        self.saveExcelRecord()     

    def encodingDetection(self):
        self.userTextBrowserAppend("执行编码和检测")
        if self.prvSerial.isOpen():
            self.encoding()
            time.sleep(0.2)
            self.detection()
        else:
            self.userTextBrowserAppend("串口未打开")

    def clearUidInput(self):
        self.lineEdit_uidInput.clear()
        
    def closeEvent(self, QCloseEvent):
        if not self.is_config_saved:
            choice = QMessageBox.question(self, "保存文件", "是否保存配置文件", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:               # 6
                self.firstSaveThreshold()
                QCloseEvent.accept()
            elif choice == QMessageBox.No:
                QCloseEvent.accept()
            else:
                QCloseEvent.ignore()

if __name__ == "__main__":
    mainApp = QtWidgets.QApplication(sys.argv)
    Terminal = MainWin()
    Terminal.show()
    sys.exit(mainApp.exec_())