# -*- coding: utf-8 -*-
# 导入日期时间模块
import datetime as dt
# 导入struct模块
import struct
# 导入系统模块
import sys
# 导入线程模块
import threading
# 导入time相关模块
import time

# 导入serial相关模块
import serial
import serial.tools.list_ports
# 默认导入
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import *
from serial import tools

# 导入功能枚举
from FuncEnum import Func
# 导入qrc资源
from resources import resources_rc
# 导入状态枚举
from StateEnum import State
# 导入自定义线程类
from ThreadLee import TimeThread
# 导入主窗口类
from Ui_Detector import Ui_MainWindow
# 引入串口封装类
from Utilities.Serial.SerialThread import PersonalSerial
# 导入自定义工具
from Utilities.usual import Tools
# 工作模式更新类
from WMMonitor import WMThread


class MainWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWin, self).__init__() # 继承父类的所有属性
        # tools instance
        self.usualTools = Tools()

        # initialization of UI
        self.initUi()

        # initialization of serial receive data timer
        self.timer_serial_recv = QTimer(self)
        self.timer_serial_recv.timeout.connect(self.serialRecvData)

        # signal<--bind-->slot
        self.bindSignalSlot()

        # initialization of serial
        # self.serialInstance = serial.Serial()  # 实例化串口对象
        self.comPortList = []
        self.comIndex = 0
        # self.comDescriptionList = list()
        self.portManager = PersonalSerial()
        self.serialInstance = self.portManager.serial
        
        self.portDetection()
        # self.serialInstance = PersonalSerial(self.comPortList[self.comIndex].device)

        # initialization of variables
        self.txCheck = 0
        self.txHighCheck = b'0'
        self.txLowCheck = b'0'
        self.rxCheck = 0
        self.rxHighCheck = b'0'
        self.rxLowCheck = b'0'
        self.serialNumber = 0

        # work mode dectionary
        self.workMode = { "encoding":"X",  "detection":"X"}
        self.data = b''

        # 自定义日期更新线程
        self.thread01 = TimeThread()
        self.thread01.secondSignal.connect(self.showDaetTime)
        self.thread01.start()

        # 阈值初始化
        global paraDict 
        paraDict = {
        "th_DrainCurrent_Up": "0", "th_DrainCurrent_Down": "0",
        "th_WorkCurrent_Up":  "0", "th_WorkCurrent_Down":  "0",
        "th_FireVoltage_Up":  "0", "th_FireVoltage_Down":  "0",
        "th_FireCurrent_Up":  "0", "th_FireCurrent_Down":  "0",
        "th_LineVoltage_Up":  "0", "th_LineVoltage_Down":  "0",
        "th_LineCurrent_Up":  "0", "th_LineCurrent_Down":  "0",
        "th_ComVoltage_Up":   "0", "th_ComVoltage_Down":   "0",
        "th_ComCurrent_Up":   "0", "th_ComCurrent_Down":   "0" }
        self.textBrowser.append(self.usualTools.getTimeStamp()+ "读取默认配置")
        self.getUserPara()

        # 配置文件的初始化
        self.is_saved_first = False
        self.is_saved = False
        self.path = ""

        #
        # self.wmRefresh = WMThread(self.serialInstance.port)
        # self.wmRefresh.start()
        # self.wmRefresh.wmChangedSignal.connect(self.wmRefreshFunc)

    def __del__(self):
        print("{}程序结束，释放资源".format(__class__))
        if self.serialInstance.portIsOpen():
            self.serialInstance.closePort()
    
    def wmRefreshFunc(self, data):
        print(data)

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
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setWindowState(Qt.WindowMaximized)

        # 检测以及编码模式默认状态设置
        self.label_detection.setStyleSheet("QLabel{border-image: url(:/images/toggle_none)}")
        self.label_encoding.setStyleSheet("QLabel{border-image: url(:/images/toggle_none)}")

        # 消息提示窗口初始化
        # self.textBrowser.setFontFamily("Times New Roman")
        self.textBrowser.setFontFamily("微软雅黑")
        self.textBrowser.setFontPointSize(12)
        self.textBrowser.append(self.usualTools.getTimeStamp()+ "请先接入被测模块再进行操作")

    def bindSignalSlot(self):
        self.pushBtn_serialSwitch.clicked.connect(self.switchPort)
        self.pushBtn_clearUidInput.clicked.connect(self.clearUidInput)
        self.pushBtn_cleanMsgArea.clicked.connect(self.clearMessage)
        self.pushBtn_saveMsgArea.clicked.connect(self.saveMessage)
        self.pushBtn_deviceSelfCheck.clicked.connect(self.deviceSelfCheck)
        self.pushBtn_deviceEncoding.clicked.connect(self.encoding)
        self.pushBtn_deviceDetection.clicked.connect(self.detection)
        self.pushBtn_saveSettingsRecord.clicked.connect(self.saveParaThreshold)
        self.pushBtn_readSettingsRecord.clicked.connect(self.readParaThreshold)

    def clearMessage(self):
        if self.textBrowser.toPlainText() != "":
            choice = QMessageBox.question(self, "窗口消息", "确认清除消息？", QMessageBox.Yes | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                self.textBrowser.clear()
            elif choice == QMessageBox.Cancel:
                pass
        else:
            pass

    def saveMessage(self):
        if self.textBrowser.toPlainText() != "":
            choice = QMessageBox.question(self, "窗口消息", "保存消息？", QMessageBox.Yes | QMessageBox.Cancel)
            if choice == QMessageBox.Yes:
                pass
            elif choice == QMessageBox.Cancel:
                pass
        else:
            pass

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
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "已检测到串口，请选择并打开串口")
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "请进行模块自检")
        else:
            print("No port detected!")
            self.statusbar.showMessage("未检测到串口")
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "未检测到串口，请连接备")
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
                    
                    self.portManager.initPort(self.comPortList[self.comIndex].device)
                    # self.serialInstance.port = self.comPortList[self.comIndex].device
                    # self.serialInstance.baudrate = 115200
                    # self.serialInstance.bytesize = serial.EIGHTBITS
                    # self.serialInstance.stopbits = serial.STOPBITS_ONE
                    # self.serialInstance.parity = serial.PARITY_NONE
                    # self.serialInstance.timeout = None
                    # self.serialInstance.xonxoff = False
                    # self.serialInstance.rtscts = False
                    # self.serialInstance.dsrdtr = False
                    try:
                        self.serialInstance.open()
                        # self.portManager.openPort()
                        if self.serialInstance.isOpen():
                            # self.timer_serial_recv.start(10)
                            self.textBrowser.append(self.usualTools.getTimeStamp()+ "端口[" + self.comPortList[self.comIndex].device + "]已打开")
                            self.pushBtn_serialSwitch.setText("关闭串口")
                            self.comboBox_selectComNum.setEnabled(False)
                    except:
                        QMessageBox.warning(self, "打开串口", "打开串口失败")
                        self.textBrowser.append(self.usualTools.getTimeStamp()+ "端口[" + self.comPortList[self.comIndex].device + "]打开失败")
                else:
                    QMessageBox.warning(self, "串口状态", "串口使用中")
            else:  # 打开时检测到无串口
                QMessageBox.information(self, "串口信息", "请连接好模块!", QMessageBox.Yes)
                self.textBrowser.append(self.usualTools.getTimeStamp()+ "未检测到串口，请连接备")
        elif staText == "关闭串口":
            self.timer_serial_recv.stop()
            self.portManager.closePort()
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "端口[" + self.comPortList[self.comIndex].device + "]已关闭")
            self.pushBtn_serialSwitch.setText("打开串口")
            self.comboBox_selectComNum.setEnabled(True)   
    
    def rxFrameCheck(self):
        self.rxCheck = int(0) # 校验和清零
        self.rxHighCheck = "F",
        self.rxLowCheck  = "F"
        dataLength = len(self.data)
        data = self.data[0:(dataLength - 4)]
        for ch in data: # 计算校验和
            self.rxCheck += ch
        self.rxHighCheck, self.rxLowCheck = self.usualTools.convertCheck(self.rxCheck & 0xFF)
        if (self.data[0] == 85) and (self.data[dataLength - 4] == self.rxHighCheck) and (self.data[dataLength - 3] == self.rxLowCheck) and \
            (self.data[dataLength - 2] == 13) and (self.data[dataLength - 1] == 10):
            print("RxFrame is right!")
            return State.s_RxFrameCheckOK
        else:
            self.serialInstance.flush()
            print("RxFrame is wrong!")
            return State.s_RxFrameCheckErr

    def serialRecvData(self):
        self.data = b''
        try:
            self.num = self.serialInstance.inWaiting()
        except:
            pass
        if self.num > 0:
            self.data = self.serialInstance.read(self.num)
            if self.data == b"\r\n":
                pass
            else:
                s = self.data.decode("utf-8")
                print(s)
                self.rxFrameCheck() # 接收帧检查
        else:
            self.serialInstance.flushInput()
            pass
    
    def sendData2Bytes(self, func):
        uid = self.lineEdit_uidInput.text()
        if func == Func.f_CheckWorkMode:
            tmp = str("D" + str(self.serialNumber) + func)
        elif func == Func.f_DevGetSelfPara:
            tmp = str("D" + str(self.serialNumber) + func)
        elif func == Func.f_DevEncoding:
            tmp = str("D" + str(self.serialNumber) + func + uid)
        elif func == Func.f_DevDetection:
            tmp = str("D" + str(self.serialNumber) + func + uid)
        elif func == Func.f_DevSettingPara:
            configPath = r"E:\Learing\2021\719\Python\Terminal\config.txt"
            with open(configPath, 'r') as f:
                s = f.read()
            tmp = str("D" + str(self.serialNumber) + func + s)
        tmp = tmp.encode("utf-8")
        if self.serialNumber == 9:# 流水号
            self.serialNumber = 0
        else:
            self.serialNumber += 1 

        return tmp

    def txFrameFormat(self, func):
        self.txCheck = int(0) # 校验和清零
        self.txHighCheck = "F",
        self.txLowCheck  = "F"
        try:
            txData = self.sendData2Bytes(func)
        except:
            print("Transfrom txData to bytes type failed!")
            return
        for ch in txData: # 计算校验和
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
        self.serialInstance.write(self.writeData)
        print("[self.writeData]" + str(self.writeData))

    def serialSendData(self, func):
        self.portIsOpen = self.serialInstance.isOpen()
        if self.portIsOpen:
            self.comDescription = self.comboBox_selectComNum.currentText()  # 获取comboBox当前串口描述
            self.comIndex = self.comDescriptionList.index(self.comDescription)
            self.portInfo = QSerialPortInfo(self.comPortList[self.comIndex].device)  # 该串口信息
            self.portStatus = self.portInfo.isBusy()  # 该串口状态
            self.uid = self.lineEdit_uidInput.text()  # 获取编号
            if self.portStatus == True:
                self.serialInstance.flush()
                self.data = b""
                try:
                    if func == Func.f_DevEncoding: 
                        if self.uid != "":
                            self.sendByFunc(func)
                            print("InputSN:" + self.uid)
                        else:
                            QMessageBox.information(self, "输入编号", "编号输入为空!\n请再输入编号", QMessageBox.Yes)
                    elif func == Func.f_DevDetection:
                        if self.uid != "":
                            self.sendByFunc(func)
                            print("InputSN:" + self.uid)
                        else:
                            QMessageBox.information(self, "输入编号", "编号输入为空!\n请再输入编号", QMessageBox.Yes)
                    else:
                        self.sendByFunc(func)
                except:
                    QMessageBox.critical(self, "串口信息", "发送数据失败")
                finally:
                    self.serialInstance.flushOutput()
            else:
                QMessageBox.warning(self, "串口信息", "串口使用中")
        else:
            QMessageBox.information(self, "串口信息", "串口未打开\n请打开串口", QMessageBox.Yes)
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "串口未打开")

        return self.portIsOpen

    def parseSettingResult(self):
        tmp = self.data.decode("utf-8")
        res =  tmp[3:(len(tmp)-4)]
        if res == "PARAOK":
            print(self.usualTools.getTimeStamp()+ "控制仪接收参数成功\n")
        elif res == "PARAERR":
            print(self.usualTools.getTimeStamp()+ "控制仪接收参数失败\n")
        elif res == "PARALESS":
            print(self.usualTools.getTimeStamp()+ "控制仪接收参数缺失\n")

    def getUserPara(self):
        paraDict["th_DrainCurrent_Up"]   = self.lineEdit_setDrainCurrentTop.text()
        paraDict["th_DrainCurrent_Down"] = self.lineEdit_setDrainCurrentBottom.text()
        paraDict["th_WorkCurrent_Up"]    = self.lineEdit_setWorkCurrentTop.text()
        paraDict["th_WorkCurrent_Down"]  = self.lineEdit_setWorkCurrentBottom.text()
        paraDict["th_FireVoltage_Up"]    = self.lineEdit_setFireVoltageTop.text()
        paraDict["th_FireVoltage_Down"]  = self.lineEdit_setFireVoltageBottom.text()
        paraDict["th_FireCurrent_Up"]    = self.lineEdit_setFireCurrentTop.text()
        paraDict["th_FireCurrent_Down"]  = self.lineEdit_setFireCurrentBottom.text()
        paraDict["th_LineVoltage_Up"]    = self.lineEdit_setLineVoltageTop.text()
        paraDict["th_LineVoltage_Down"]  = self.lineEdit_setLineVoltageBottom.text()
        paraDict["th_LineCurrent_Up"]    = self.lineEdit_setLineCurrentTop.text()
        paraDict["th_LineCurrent_Down"]  = self.lineEdit_setLineCurrentBottom.text()
        paraDict["th_ComVoltage_Up"]     = self.lineEdit_setComVoltageTop.text()
        paraDict["th_ComVoltage_Down"]   = self.lineEdit_setComVoltageBottom.text()
        paraDict["th_ComCurrent_Up"]     = self.lineEdit_setComCurrentTop.text()
        paraDict["th_ComCurrent_Down"]   = self.lineEdit_setComCurrentBottom.text()

    def settingParaThreshold(self):
        print("/*>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>*/")
        # self.textBrowser.append(self.usualTools.getTimeStamp()+ "设置参数阈值")
        if self.serialSendData(Func.f_DevSettingPara) == True:
            if self.portStatus == True:
                print("Setting parameters's threshold ......")
                self.data = b''
                self.rxCheck = 0
                startTiming = dt.datetime.now()
                self.serialInstance.flushInput()
                while True:
                    QApplication.processEvents()
                    try:
                        self.num = self.serialInstance.inWaiting()
                        # print("workModeCheck num:" + str(self.num)) # 输出收到的字节数
                        if self.num > 0:
                            time.sleep(0.1)
                            self.num = self.serialInstance.inWaiting()
                        if self.num >= 9:
                            break
                        elif self.num == 0:
                            endTiming = dt.datetime.now()
                            if (endTiming - startTiming).seconds >= 5:
                                self.textBrowser.append(self.usualTools.getTimeStamp()+ "@接收数据超时")
                                break
                            else:
                                continue
                        else:
                            continue
                    except:
                        continue
                if self.num >= 9:
                    self.data = self.serialInstance.read(self.num)
                    print("settingParaThreshold:" + str(self.data, encoding="utf-8"))
                    if self.rxFrameCheck() == State.s_RxFrameCheckOK: # 接收帧检查
                        self.parseSettingResult()
                    else:
                        self.textBrowser.append(self.usualTools.getTimeStamp()+ "接收帧错误")
                    self.serialInstance.flush()
                else:
                    self.serialInstance.flush()
            else:
                self.textBrowser.append(self.usualTools.getTimeStamp()+ "串口使用中或已拔出")
        else:
            pass # 返回串口未打开，发送函数已做处理，这里直接pass即可        
    
    def saveParaThreshold(self):
        if self.serialInstance.isOpen():
            print(self.usualTools.getTimeStamp()+ "下发并保存指定参数\n")
            # self.textBrowser.append(self.usualTools.getTimeStamp()+ "下发并保存指定参数")
            self.getUserPara()
            print(self.usualTools.getTimeStamp()+ "下发指定参数\n")
            # self.textBrowser.append(self.usualTools.getTimeStamp()+ "下发指定参数")
            self.settingParaThreshold()
            print(self.usualTools.getTimeStamp()+ "保存指定参数\n")
            # self.textBrowser.append(self.usualTools.getTimeStamp()+ "保存指定参数")
            configPath = r"E:\Learing\2021\719\Python\Terminal\config.txt"
            with open(configPath, 'w') as f:
                cnt = 0
                for k,v in paraDict.items():
                    if cnt == 10:
                        para = "PA" + v
                    elif cnt == 11:
                        para = "PB" + v
                    elif cnt == 12:
                        para = "PC" + v
                    elif cnt == 13:
                        para = "PD" + v
                    elif cnt == 14:
                        para = "PE" + v
                    elif cnt == 15:
                        para = "PF" + v
                    else:
                        para = "P" + str(cnt) + v
                    cnt += 1
                    f.write(para)
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "保存配置参数成功")
        else:
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "未打开串口，无法下发参数")

    def readParaThreshold(self):
        configPath = r"E:\Learing\2021\719\Python\Terminal\config.txt"
        with open(configPath, 'r') as f:
            s = f.read()
            # print(s)
        self.textBrowser.append(self.usualTools.getTimeStamp()+ "读取配置参数成功")
        
    def setWorkMode(self):
        if self.data[len(self.data) - 6] == 48:
            self.workMode["encoding"] = "0"
        else:
            self.workMode["encoding"] = "1"
        if self.data[len(self.data) - 5] == 48:
            self.workMode["detection"] = "0"
        else:
            self.workMode["detection"] = "1" 

    def getWorkMode(self):
        return self.workMode

    def showWorkMode(self):
        wm = self.getWorkMode()
        endc = wm["encoding"]
        dete = wm["detection"]
        if endc == "1" and dete == "1":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/images/toggle_on)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/images/toggle_on)}")
            self.textBrowser.append(self.usualTools.getTimeStamp() + "编码模式【开启】 检测模式【开启】")
        elif endc == "1" and dete == "0":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/images/toggle_on)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")
            self.textBrowser.append(self.usualTools.getTimeStamp() + "编码模式【开启】 检测模式【关闭】")
        elif endc == "0" and dete == "1":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/images/toggle_on)}")
            self.textBrowser.append(self.usualTools.getTimeStamp() + "编码模式【关闭】 检测模式【开启】")
        elif endc == "0" and dete == "0":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")
            self.textBrowser.append(self.usualTools.getTimeStamp() + "编码模式【关闭】 检测模式【关闭】")
            
        if dete == "1" and endc == "1":
            print(self.usualTools.getTimeStamp() + "允许进行【编码】和【检测】")
            # self.textBrowser.append(self.usualTools.getTimeStamp() + "允许进行【编码】和【检测】")
        elif dete == "1" and endc == "0":
            print(self.usualTools.getTimeStamp() + "只能进行【检测】")
            # self.textBrowser.append(self.usualTools.getTimeStamp() + "只能进行【检测】")
        elif dete == "0" and endc == "1":
            print(self.usualTools.getTimeStamp() + "只能进行【编码】")
            # self.textBrowser.append(self.usualTools.getTimeStamp() + "只能进行【编码】")
        elif dete == "0" and endc == "0":
            print(self.usualTools.getTimeStamp() + "无法进行【编码】和【检测】，请按下功能按键！")
            self.textBrowser.append(self.usualTools.getTimeStamp() + "无法进行【编码】和【检测】，请按下功能按键！")

    def workModeCheck(self):
        print("/*---------------------------------------------*/")
        # self.textBrowser.append(self.usualTools.getTimeStamp()+ "检查工作模式")
        if self.serialSendData(Func.f_CheckWorkMode) == True:
            if self.portStatus == True:
                print("Checking work mode ......")
                self.data = b''
                self.rxCheck = 0
                startTiming = dt.datetime.now()
                self.serialInstance.flushInput()
                while True:
                    QApplication.processEvents()
                    try:
                        self.num = self.serialInstance.inWaiting()
                        # print("workModeCheck num:" + str(self.num)) # 输出收到的字节数
                        if self.num > 0:
                            time.sleep(0.01)
                            self.num = self.serialInstance.inWaiting()
                        if self.num >= 9:
                            break
                        elif self.num == 0:
                            endTiming = dt.datetime.now()
                            if (endTiming - startTiming).seconds >= 2:
                                QApplication.processEvents()
                                self.textBrowser.append(self.usualTools.getTimeStamp()+ "@接收数据超时")
                                break
                            else:
                                continue
                        else:
                            continue
                    except:
                        continue
                if self.num >= 9:
                    self.data = self.serialInstance.read(self.num)
                    print("workModeCheck:" + str(self.data, encoding="utf-8"))
                    if self.rxFrameCheck() == State.s_RxFrameCheckOK: # 接收帧检查
                        self.setWorkMode()
                        self.showWorkMode()
                    else:
                        self.textBrowser.append(self.usualTools.getTimeStamp()+ "接收帧错误")
                    self.serialInstance.flush()
                else:
                    self.serialInstance.flush()
            else:
                self.textBrowser.append(self.usualTools.getTimeStamp()+ "串口使用中或已拔出")
        else:
            pass # 返回串口未打开，发送函数已做处理，这里直接pass即可
    
    def parseSelfPara(self):
        tmp = self.data.decode("utf-8")
        PwrVol  = tmp[3:6];   PwrCur  = tmp[6:10]
        ComVol  = tmp[10:13]; ComCur  = tmp[13:17]
        FireVol = tmp[17:20]; FireCur = tmp[20:24]
        self.label_selfLineVoltage.setText(PwrVol[0:2] + "." + PwrVol[2:3])
        self.label_selfLineCurrent.setText(PwrCur[0:1] + "." + PwrCur[1:4])
        self.label_selfComVoltage.setText(ComVol[0:2] + "." + ComVol[2:3])
        self.label_selfComCurrent.setText(ComCur[0:1] + "." + ComCur[1:4])
        self.label_selfFireVoltage.setText(FireVol[0:2] + "." + FireVol[2:3])
        self.label_selfFireCurrent.setText(FireCur[0:1] + "." + FireCur[1:4])
        self.textBrowser.append(self.usualTools.getTimeStamp()+ "已获取控制仪参数")

    def getDevicePara(self):
        print("/*+++++++++++++++++++++++++++++++++++++++++++++*/")
        # self.textBrowser.append(self.usualTools.getTimeStamp()+ "检查模块参数")
        if self.serialSendData(Func.f_DevGetSelfPara) == True:
            if self.portStatus == True:
                print("Checking device parameters ......")
                self.data = b''
                self.rxCheck = 0
                self.serialInstance.flushInput()
                startTiming = dt.datetime.now()
                while True:
                    QApplication.processEvents()
                    try:
                        self.num = self.serialInstance.inWaiting()
                        # print(self.num) # 输出收到的字节数
                        if self.num > 0:
                            time.sleep(0.2)
                            self.num = self.serialInstance.inWaiting()
                        if self.num >= 28:
                            break
                        elif self.num == 0:
                            endTiming = dt.datetime.now()
                            if (endTiming - startTiming).seconds >= 6:
                                self.textBrowser.append(self.usualTools.getTimeStamp()+ "@接收数据超时")
                                break
                            else:
                                continue
                    except:
                        continue
                if self.num >= 28:
                    self.data = self.serialInstance.read(self.num)
                    print("getDevicePara:" + str(self.data, encoding="utf-8"))
                    if self.rxFrameCheck() == State.s_RxFrameCheckOK: # 接收帧检查
                        self.parseSelfPara()
                    else:
                        self.textBrowser.append(self.usualTools.getTimeStamp()+ "接收帧错误")
                    self.serialInstance.flush()
                else:
                    self.serialInstance.flush()
            else:
                self.textBrowser.append(self.usualTools.getTimeStamp()+ "串口使用中或已拔出")
        else:
            pass # 返回串口未打开，发送函数已做处理，这里直接pass即可

    def deviceSelfCheck(self):
        # if self.serialInstance.isOpen() == True:
        if self.serialInstance.isOpen() == True:
            self.workModeCheck()
            time.sleep(0.5)
            self.getDevicePara()
        else:
            QMessageBox.information(self, "串口信息", "串口未打开\n请打开串口", QMessageBox.Yes)

    def parseEncodeResult(self):
        res = ""
        tmp = self.data.decode("utf-8")
        res =  tmp[3:(len(tmp) - 4)]
        if res == "UIDOK":
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "对比UID成功")
        elif res == "UIDERR":
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "对比UID失败")
        elif res == "FACULTY":
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "模块已出故障，请更换模块！")
        elif res == "NCODE":
            self.workMode["encoding"] = "0"
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "无法进行编码，请检查编码按键")

    def encoding(self):
        if self.workMode["encoding"] == "1":
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "模块编码")
            print("/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/")
            if self.serialSendData(Func.f_DevEncoding) == True:
                if self.portStatus == True:
                    print("Encoding......")
                    if self.lineEdit_uidInput.text() != "":
                        self.textBrowser.append(self.usualTools.getTimeStamp()+ "输入UID为：" + self.lineEdit_uidInput.text())
                        self.data = b''
                        self.rxCheck = 0
                        self.serialInstance.flushInput()
                        startTiming = dt.datetime.now()
                        while True:
                            QApplication.processEvents()
                            try:
                                self.num = self.serialInstance.inWaiting()
                                # print(self.num) # 输出收到的字节数
                                if self.num > 0:
                                    time.sleep(0.01)
                                    self.num = self.serialInstance.inWaiting()
                                if self.num >= 12:
                                    break
                                elif self.num == 0:
                                    endTiming = dt.datetime.now()
                                    if (endTiming - startTiming).seconds >= 10:
                                        QApplication.processEvents()
                                        self.textBrowser.append(self.usualTools.getTimeStamp()+ "@接收数据超时")
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            except:
                                self.textBrowser.append(self.usualTools.getTimeStamp()+ "@接收数据失败")
                                # return
                        if self.num >= 12:
                            self.data = self.serialInstance.read(self.num)
                            print("encoding:" + str(self.data, encoding="utf-8"))
                            self.rxFrameCheck() # 接收帧检查
                            self.parseEncodeResult()
                            self.serialInstance.flush()
                        else:
                            self.serialInstance.flush()
                    else:
                        self.textBrowser.append(self.usualTools.getTimeStamp()+ "输入编号为空！")
                else:
                    self.textBrowser.append(self.usualTools.getTimeStamp()+ "串口使用中或已拔出")
            else:
                pass
        else:
            self.textBrowser.append(self.usualTools.getTimeStamp() + "编码模式【未开启】")

    def parseDetectResult(self):
        global PwrVolSta, PwrCurSta
        PwrVolSta = 9
        PwrCurSta = 9
        res = ""
        tmp = self.data.decode("utf-8")
        res =  tmp[3:(len(tmp) - 4)]
        if res == "LVERRLCERR":
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "电流超限，电压超限")
            PwrVolSta = 1; PwrCurSta = 1
        elif res == "LVOKLCERR":
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "电压正常，电流超限")
            PwrVolSta = 0; PwrCurSta = 1
        elif res == "LVERRLCOK":
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "电压超限，电流正常")
            PwrVolSta = 1; PwrCurSta = 0
        elif res == "LVOKLCOK":
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "电压正常，电流正常")
            PwrVolSta = 0; PwrCurSta = 0
        elif res == "NDETE":
            self.workMode["detection"] = "0"
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "无法进行检测，请检查检测按键")

        return PwrVolSta, PwrCurSta

    def detRepLineAV(self):
        pass

    def detection(self):
        if self.workMode["detection"] == "1":
            print("/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/")
            self.textBrowser.append(self.usualTools.getTimeStamp()+ "模块检测")
            if self.serialSendData(Func.f_DevDetection) == True:
                if self.portStatus == True:
                    print("Detecting......")
                    if self.lineEdit_uidInput.text() != "":
                        self.textBrowser.append(self.usualTools.getTimeStamp()+ "输入UID为：" + self.lineEdit_uidInput.text())
                        self.data = b''
                        self.rxCheck = 0
                        startTiming = dt.datetime.now()
                        self.serialInstance.flushInput()
                        while True:
                            try:
                                QApplication.processEvents()
                                self.num = self.serialInstance.inWaiting()
                                # print(self.num) # 输出收到的字节数
                                if self.num > 0:
                                    time.sleep(0.01)
                                    self.num = self.serialInstance.inWaiting()
                                if self.num >= 9:
                                    break
                                elif self.num == 0:
                                    endTiming = dt.datetime.now()
                                    if (endTiming - startTiming).seconds >= 2:
                                        QApplication.processEvents()
                                        self.textBrowser.append(self.usualTools.getTimeStamp()+ "@接收数据超时")
                                        break
                                    else:
                                        continue
                                else:
                                    continue
                            except:
                                continue
                        if self.num >= 9:
                            self.data = self.serialInstance.read(self.num)
                            print("detection:" + str(self.data, encoding="utf-8"))
                            self.rxFrameCheck() # 接收帧检查
                            self.parseDetectResult()
                            self.serialInstance.flush()
                        else:
                            self.serialInstance.flush()
                    else:
                        self.textBrowser.append(self.usualTools.getTimeStamp()+ "输入编号为空！")  
                else:
                    self.textBrowser.append(self.usualTools.getTimeStamp()+ "串口使用中或已拔出")
            else:
                pass
        else:
            self.textBrowser.append(self.usualTools.getTimeStamp() + "检测模式【未开启】")

    def clearUidInput(self):
        self.lineEdit_uidInput.clear()

    def closeEvent(self, QCloseEvent):
        choice = QMessageBox.question(self, "窗口消息", "是否要关闭窗口？", QMessageBox.Yes | QMessageBox.Cancel)
        if choice == QMessageBox.Yes:
            QCloseEvent.accept()
        elif choice == QMessageBox.Cancel:
            QCloseEvent.ignore()

if __name__ == "__main__":
    mainApp = QtWidgets.QApplication(sys.argv)
    Terminal = MainWin()
    Terminal.show()
    sys.exit(mainApp.exec_())
