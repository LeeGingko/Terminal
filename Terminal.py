# -*- coding: utf-8 -*-
# 导入日期时间模块
import datetime as dt
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
# 导入自定义工具
from MyTools import Tools
# 导入qrc资源
from resources import resources_rc
# 导入状态枚举
from StateEnum import State
# 导入自定义线程类
from ThreadLee import MyThread
# 导入主窗口类
from Ui_Detector import Ui_MainWindow

class MainWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWin, self).__init__() # 继承父类的所有属性
        # time stamp getter instance
        self.timeTool = Tools()

        # initialization of UI
        self.initUi()

        # initialization of serial receive data timer
        self.timer_serial_recv = QTimer(self)
        self.timer_serial_recv.timeout.connect(self.serialRecvData)

        # system datetime timer
        # self.timer_datetime = QTimer(self)
        # self.timer_datetime.timeout.connect(self.showDaetTime)
        # self.timer_datetime.start(1000)

        # signal<--bind-->slot
        self.bindSignalSlot()

        # initialization of serial
        self.serialInstance = serial.Serial()  # 实例化串口对象
        self.portDetection()

        # initialization of variables
        self.txCheck = 0
        self.txHighCheck = b'0'
        self.txLowCheck = b'0'
        self.rxCheck = 0
        self.rxHighCheck = b'0'
        self.rxLowCheck = b'0'
        self.serialNumber = '0'

        # work mode dectionary
        self.workMode = { "encoding":"X",  "detection":"X"}
        self.data = b''

        # 启动日期更新线程 2021年3月19日 20:53:07--暂时不用此方法
        # self.thDateTimeFefresh = threading.Thread(target=self.dateTimeFefresh, name="dateTimeFefresh")
        # self.thDateTimeFefresh.setDaemon(True)
        # self.thDateTimeFefresh.start()

        self.thread01 = MyThread()
        self.thread01.secondSignal.connect(self.showDaetTime)
        self.thread01.start()

    def __del__(self):
        print("{}程序结束，释放资源".format(__class__))
        if self.serialInstance.isOpen():
            self.serialInstance.close()
        
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
        self.label_detection.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")
        self.label_encoding.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")

        # 消息提示窗口初始化
        # self.textBrowser.setFontFamily("Times New Roman")
        self.textBrowser.setFontFamily("微软雅黑")
        self.textBrowser.setFontPointSize(12)
        self.textBrowser.append(self.timeTool.getTimeStamp()+ "请先接入被测模块")

    def bindSignalSlot(self):
        self.pushBtn_serialSwitch.clicked.connect(self.switchPort)
        self.pushBtn_clearUidInput.clicked.connect(self.clearUidInput)
        self.pushBtn_cleanMsgArea.clicked.connect(self.clearMessage)
        self.pushBtn_saveMsgArea.clicked.connect(self.saveMessage)
        self.pushBtn_deviceSelfCheck.clicked.connect(self.deviceSelfCheck)
        self.pushBtn_deviceEncoding.clicked.connect(self.encoding)
        self.pushBtn_deviceDetection.clicked.connect(self.detection)

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
        # if str((time.strftime("%p"),time.localtime()[0])).strip("AM"):
        #     dateTimeStr = time.strftime("%Y年%m月%d日\n上午 %H:%M:%S ", time.localtime())
        # else:
        #     dateTimeStr = time.strftime("%Y年%m月%d日\n下午 %H:%M:%S ", time.localtime())
        # dayOfWeek = time.localtime().tm_wday
        # if dayOfWeek == 0:
        #     dateTimeStr = dateTimeStr + "星期一"
        # elif dayOfWeek == 1:
        #     dateTimeStr = dateTimeStr + "星期二"
        # elif dayOfWeek == 2:
        #     dateTimeStr = dateTimeStr + "星期三"
        # elif dayOfWeek == 3:
        #     dateTimeStr = dateTimeStr + "星期四"
        # elif dayOfWeek == 4:
        #     dateTimeStr = dateTimeStr + "星期五"
        # elif dayOfWeek == 5:
        #     dateTimeStr = dateTimeStr + "星期六"
        # elif dayOfWeek == 6:
        #     dateTimeStr = dateTimeStr + "星期天"
        self.label_localDateTime.setText(timeStr)

    def dateTimeFefresh(self):
        print('thread %s is running...' % threading.current_thread().name)
        while True:
            time.sleep(1)
            self.showDaetTime()
        print('thread %s ended.' % threading.current_thread().name)

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
            self.textBrowser.append(self.timeTool.getTimeStamp()+ "已检测到串口，请选择并打开串口")
            self.textBrowser.append(self.timeTool.getTimeStamp()+ "请进行设备自检")
        else:
            print("No port detected!")
            self.statusbar.showMessage("未检测到串口")
            self.textBrowser.append(self.timeTool.getTimeStamp()+ "未检测到串口，请连接备")
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
                    self.serialInstance.port = self.comPortList[self.comIndex].device
                    self.serialInstance.baudrate = 115200
                    self.serialInstance.bytesize = serial.EIGHTBITS
                    self.serialInstance.stopbits = serial.STOPBITS_ONE
                    self.serialInstance.parity = serial.PARITY_NONE
                    self.serialInstance.timeout = None
                    self.serialInstance.xonxoff = False
                    self.serialInstance.rtscts = False
                    self.serialInstance.dsrdtr = False
                    try:
                        self.serialInstance.open()
                        if self.serialInstance.isOpen():
                            # self.timer_serial_recv.start(10)
                            self.textBrowser.append(self.timeTool.getTimeStamp()+ "端口[" + self.comPortList[self.comIndex].device + "]已打开")
                            self.pushBtn_serialSwitch.setText("关闭串口")
                            self.comboBox_selectComNum.setEnabled(False)
                    except:
                        QMessageBox.warning(self, "打开串口", "打开串口失败")
                        self.textBrowser.append(self.timeTool.getTimeStamp()+ "端口[" + self.comPortList[self.comIndex].device + "]打开失败")
                else:
                    QMessageBox.warning(self, "串口状态", "串口使用中或已拔出")
            else:  # 打开时检测到无串口
                QMessageBox.information(self, "串口信息", "请连接好设备!", QMessageBox.Yes)
                self.textBrowser.append(self.timeTool.getTimeStamp()+ "未检测到串口，请连接备")
        elif staText == "关闭串口":
            self.timer_serial_recv.stop()
            self.serialInstance.close()
            self.textBrowser.append(self.timeTool.getTimeStamp()+ "端口[" + self.comPortList[self.comIndex].device + "]已关闭")
            self.pushBtn_serialSwitch.setText("打开串口")
            self.comboBox_selectComNum.setEnabled(True)   
    
    def convertCheck(self, check):
        ch = bytearray([0,0,0,0])
        ch[0] = ((check & 0xF0) >> 4) - 10 + 65
        ch[1] = (check & 0x0F) - 10 + 65
        ch[2] = ((check & 0xF0) >> 4) + 48
        ch[3] = (check & 0x0F) + 48
        # 校验和高四位
        if(((check & 0xF0) >> 4) >= 10):
            self.highCheck = ch[0]
        else:
            self.highCheck = ch[2]
        # 校验和低四位
        if((check & 0x0F) >= 10):
            self.lowCheck = ch[1]
        else:
            self.lowCheck = ch[3]

    def rxFrameCheck(self):
        self.rxCheck = int(0) # 校验和清零
        dataLength = len(self.data)
        data = self.data[0:(dataLength - 4)]
        # print(data)
        for ch in data: # 计算校验和
            self.rxCheck += ch
        self.convertCheck(self.rxCheck & 0xFF) # 
        self.rxHighCheck = self.highCheck
        self.rxLowCheck = self.lowCheck
        if (self.data[0] == 85) and (self.data[dataLength - 4] == self.rxHighCheck) and (self.data[dataLength - 3] == self.rxLowCheck) and \
            (self.data[dataLength - 2] == 13) and (self.data[dataLength - 1] == 10):
            print("RxFrame is correct!!")
            return State.s_RxFrameCheckOK
        else:
            self.serialInstance.flush()
            print("RxFrame is mistake!!")
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
            tmp = str("D" + self.serialNumber + func)
        elif func == Func.f_DevGetSelfPara:
            tmp = str("D" + self.serialNumber + func)
        elif func == Func.f_DevEncoding:
            tmp = str("D" + self.serialNumber + func + uid)
        elif func == Func.f_DevDetection:
            tmp = str("D" + self.serialNumber + func + uid)
        tmp = tmp.encode("utf-8")

        return tmp

    def txFrameFormat(self, func):
        self.txCheck = 0
        try:
            txData = self.sendData2Bytes(func)
        except:
            print("Transfrom txData to bytes failed!")
            return
        for ch in txData: # 计算校验和
            self.txCheck += ch
        self.convertCheck(self.txCheck)
        self.txHighCheck = self.highCheck
        self.txLowCheck = self.lowCheck
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
        if self.serialNumber == '10':
            self.serialNumber = "0"
        else:
            self.serialNumber = str(int(self.serialNumber) + 1) # 流水号

    def serialSendData(self, func):
        self.portIsOpen = self.serialInstance.isOpen()
        if self.portIsOpen:
            self.comDescription = self.comboBox_selectComNum.currentText()  # 获取comboBox当前串口描述
            self.comIndex = self.comDescriptionList.index(self.comDescription)
            self.portInfo = QSerialPortInfo(self.comPortList[self.comIndex].device)  # 该串口信息
            self.portStatus = self.portInfo.isBusy()  # 该串口状态
            self.uid = self.lineEdit_uidInput.text()  # 获取编号
            if self.portStatus == True:
                try:
                    # print("func:" + func)
                    if func == Func.f_CheckWorkMode:
                        self.sendByFunc(func)
                    elif func == Func.f_DevGetSelfPara:
                        self.sendByFunc(func)
                    elif func == Func.f_DevEncoding: 
                        if self.lineEdit_uidInput.text() != "":
                            self.sendByFunc(func)
                            print("InputSN:" + self.lineEdit_uidInput.text())
                        else:
                            QMessageBox.information(self, "输入编号", "编号输入为空!\n请输入编号", QMessageBox.Yes)
                    elif func == Func.f_DevDetection:
                        if self.lineEdit_uidInput.text() != "":
                            self.sendByFunc(func)
                            print("InputSN:" + self.lineEdit_uidInput.text())
                        else:
                            QMessageBox.information(self, "输入编号", "编号输入为空!\n请输入编号", QMessageBox.Yes)
                except:
                    QMessageBox.warning(self, "串口信息", "发送数据失败")
                finally:
                    self.serialInstance.flushOutput()
            else:
                QMessageBox.warning(self, "串口信息", "串口使用中或已拔出")
        else:
            QMessageBox.information(self, "串口信息", "串口未打开\n请先打开串口", QMessageBox.Yes)
            self.textBrowser.append(self.timeTool.getTimeStamp()+ "串口未打开")

        return self.portIsOpen

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
            self.textBrowser.append(self.timeTool.getTimeStamp() + "&编码模式【开启】 #检测模式【开启】")
        elif endc == "1" and dete == "0":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/images/toggle_on)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")
            self.textBrowser.append(self.timeTool.getTimeStamp() + "&编码模式【开启】 #检测模式【关闭】")
        elif endc == "0" and dete == "1":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/images/toggle_on)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")
            self.textBrowser.append(self.timeTool.getTimeStamp() + "&编码模式【关闭】 #检测模式【开启】")
        elif endc == "0" and dete == "0":
            self.label_encoding.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")
            self.label_detection.setStyleSheet("QLabel{border-image: url(:/images/toggle_off)}")
            self.textBrowser.append(self.timeTool.getTimeStamp() + "&编码模式【关闭】 #检测模式【关闭】")
        if dete == "1" and endc == "1":
            self.textBrowser.append(self.timeTool.getTimeStamp() + "允许进行【编码】和【检测】")
        elif dete == "1" and endc == "0":
            self.textBrowser.append(self.timeTool.getTimeStamp() + "只能进行【检测】")
        elif dete == "0" and endc == "1":
            self.textBrowser.append(self.timeTool.getTimeStamp() + "只能进行【编码】")
        elif dete == "0" and endc == "0":
            self.textBrowser.append(self.timeTool.getTimeStamp() + "无法进行【编码】和【检测】，请按下功能按键！")

    def workModeCheck(self):
        print("/*-----------------------------------------------------------*/")
        self.textBrowser.append(self.timeTool.getTimeStamp()+ "检查工作模式")
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
                        if self.num >= 9:
                            break
                        elif self.num == 0:
                            endTiming = dt.datetime.now()
                            if (endTiming - startTiming).seconds >= 2:
                                self.textBrowser.append(self.timeTool.getTimeStamp()+ "@接收数据超时")
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
                        self.textBrowser.append(self.timeTool.getTimeStamp()+ "接收帧错误")
                    self.serialInstance.flush()
                else:
                    self.serialInstance.flush()
            else:
                self.textBrowser.append(self.timeTool.getTimeStamp()+ "串口使用中或已拔出")
        else:
            pass # 返回串口未打开，发送函数已做处理，这里直接pass即可
    
    def parseSelfPara(self):
        tmp = self.data.decode("utf-8")
        PwrVol  = tmp[3:6];   PwrCur  = tmp[6:10]
        ComVol  = tmp[10:13]; ComCur  = tmp[13:17]
        FireVol = tmp[17:20]; FireCur = tmp[20:24]
        self.label_selfSupVoltage.setText(PwrVol[0:2] + "." + PwrVol[2:3])
        self.label_selfSupCurrent.setText(PwrCur[0:1] + "." + PwrCur[1:4])
        self.label_selfComVoltage.setText(ComVol[0:2] + "." + ComVol[2:3])
        self.label_selfComCurrent.setText(ComCur[0:1] + "." + ComCur[1:4])
        self.label_selfFireVoltage.setText(FireVol[0:2] + "." + FireVol[2:3])
        self.label_selfFireCurrent.setText(FireCur[0:1] + "." + FireCur[1:4])
        self.textBrowser.append(self.timeTool.getTimeStamp()+ "已获取设备参数")

    def getDevicePara(self):
        print("/*+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*/")
        self.textBrowser.append(self.timeTool.getTimeStamp()+ "检查设备参数")
        if self.serialSendData(Func.f_DevGetSelfPara) == True:
            if self.portStatus == True:
                print("Checking device parameters ......")
                self.data = b''
                self.rxCheck = 0
                startTiming = dt.datetime.now()
                self.serialInstance.flushInput()
                while True:
                    QApplication.processEvents()
                    try:
                        self.num = self.serialInstance.inWaiting()
                        # print(self.num) # 输出收到的字节数
                        if self.num >= 28:
                            break
                        elif self.num == 0:
                            endTiming = dt.datetime.now()
                            if (endTiming - startTiming).seconds >= 5:
                                self.textBrowser.append(self.timeTool.getTimeStamp()+ "@接收数据超时")
                                break
                            else:
                                continue
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
                        self.textBrowser.append(self.timeTool.getTimeStamp()+ "接收帧错误")
                    self.serialInstance.flush()
                else:
                    self.serialInstance.flush()
            else:
                self.textBrowser.append(self.timeTool.getTimeStamp()+ "串口使用中或已拔出")
        else:
            pass # 返回串口未打开，发送函数已做处理，这里直接pass即可

    def deviceSelfCheck(self):
        if self.serialInstance.isOpen() == True:
            self.workModeCheck()
            time.sleep(0.5)
            self.getDevicePara()
        else:
            QMessageBox.information(self, "串口信息", "串口未打开\n请先打开串口", QMessageBox.Yes)

    def parseEncodeResult(self):
        tmp = self.data.decode("utf-8")
        res =  tmp[3:(len(tmp)-4)]
        if res == "FACULTY":
            self.textBrowser.append(self.timeTool.getTimeStamp()+ "设备已出故障，请更换设备！")
        elif res == "UIDOK":
            self.textBrowser.append(self.timeTool.getTimeStamp()+ "对比UID成功")
        elif res == "UIDERR":
            self.textBrowser.append(self.timeTool.getTimeStamp()+ "对比UID失败")
        elif res == "NCODE":
            self.textBrowser.append(self.timeTool.getTimeStamp()+ "无法进行编码，请检查编码按键")

    def encoding(self):
        self.textBrowser.append(self.timeTool.getTimeStamp()+ "设备编码")
        print("/*^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^*/")
        if self.serialSendData(Func.f_DevEncoding) == True:
            if self.portStatus == True:
                print("Encoding......")
                if self.lineEdit_uidInput.text() != "":
                    self.textBrowser.append(self.timeTool.getTimeStamp()+ "输入UID为：" + self.lineEdit_uidInput.text())
                    self.data = b''
                    self.rxCheck = 0
                    self.serialInstance.flushInput()
                    startTiming = dt.datetime.now()
                    while True:
                        QApplication.processEvents()
                        try:
                            self.num = self.serialInstance.inWaiting()
                            # print(self.num) # 输出收到的字节数
                            if self.num >= 12:
                                break
                            elif self.num == 0:
                                endTiming = dt.datetime.now()
                                if (endTiming - startTiming).seconds >= 10:
                                    self.textBrowser.append(self.timeTool.getTimeStamp()+ "@接收数据超时")
                                    break
                                else:
                                    continue
                            else:
                                endTiming = dt.datetime.now()
                                if (endTiming - startTiming).seconds >= 10:
                                    self.textBrowser.append(self.timeTool.getTimeStamp()+ "@接收数据超时")
                                    break
                                else:
                                    continue
                        except:
                            continue
                    if self.num >= 12:
                        self.data = self.serialInstance.read(self.num)
                        print("encoding:" + str(self.data, encoding="utf-8"))
                        self.rxFrameCheck() # 接收帧检查
                        self.parseEncodeResult()
                        self.serialInstance.flush()
                    else:
                        self.serialInstance.flush()
                else:
                    self.textBrowser.append(self.timeTool.getTimeStamp()+ "编号输入为空！")
            else:
                self.textBrowser.append(self.timeTool.getTimeStamp()+ "串口使用中或已拔出")
        else:
            pass
        
    def detection(self):
        print("/*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/")
        self.textBrowser.append(self.timeTool.getTimeStamp()+ "设备检测")
        if self.serialSendData(Func.f_DevDetection) == True:
            if self.portStatus == True:
                print("Detecting......")
                if self.lineEdit_uidInput.text() != "":
                    self.data = b''
                    self.rxCheck = 0
                    startTiming = dt.datetime.now()
                    self.serialInstance.flushInput()
                    while True:
                        QApplication.processEvents()
                        try:
                            self.num = self.serialInstance.inWaiting()
                            # print(self.num) # 输出收到的字节数
                            if self.num >= 9:
                                break
                            elif self.num == 0:
                                endTiming = dt.datetime.now()
                                if (endTiming - startTiming).seconds >= 2:
                                    self.textBrowser.append(self.timeTool.getTimeStamp()+ "@接收数据超时")
                                    break
                                else:
                                    continue
                            else:
                                endTiming = dt.datetime.now()
                                if (endTiming - startTiming).seconds >= 2:
                                    self.textBrowser.append(self.timeTool.getTimeStamp()+ "@接收数据超时")
                                    break
                                else:
                                    continue
                        except:
                            continue
                    if self.num >= 9:
                        self.data = self.serialInstance.read(self.num)
                        print("detection:" + str(self.data, encoding="utf-8"))
                        self.rxFrameCheck() # 接收帧检查
                        self.serialInstance.flush()
                    else:
                        self.serialInstance.flush()
                else:
                    self.textBrowser.append(self.timeTool.getTimeStamp()+ "编号输入为空！")  
            else:
                self.textBrowser.append(self.timeTool.getTimeStamp()+ "串口使用中或已拔出")
        else:
            pass

    def clearUidInput(self):
        self.lineEdit_uidInput.clear()

    def closeEvent(self, QCloseEvent):
        choice = QMessageBox.question(self, "窗口消息", "是否要关闭窗口？", QMessageBox.Yes | QMessageBox.Cancel)
        if choice == QMessageBox.Yes:
            QCloseEvent.accept()
        elif choice == QMessageBox.Cancel:
            QCloseEvent.ignore()

if __name__ == "__main__":
    mainThread = QtWidgets.QApplication(sys.argv)
    Terminal = MainWin()
    Terminal.show()
    sys.exit(mainThread.exec_())