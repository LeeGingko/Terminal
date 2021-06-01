# -*- coding: utf-8 -*-
# 导入日期时间模块
import datetime as dt
# 导入time相关模块
import time
# 默认导入
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox

# 导入协议通信界面
from Ui_Protocol import Ui_ProtocolDialog
# 导入功能枚举
from Utilities.Enum.FuncEnum import Func
# 导入状态枚举
from Utilities.Enum.StateEnum import State
# 引入串口封装类
from Utilities.Serial.SerialMonitor import PrivateSerialMonitor
from Utilities.Serial.SerialThread import PrivateSerialThread
# 导入自定义工具
from Utilities.Tool.usual import Tools

class ProtocolWin(QtWidgets.QDialog, Ui_ProtocolDialog):
    protocolAppendSignal = pyqtSignal(str)

    def __init__(self):
        super(ProtocolWin, self).__init__()  # 继承父类的所有属性
        self.initUi()
        self.convert = Tools()
        # 串口变量初始化
        self.txCheck = 0
        self.txHighCheck = b'0'
        self.txLowCheck = b'0'
        self.rxCheck = 0
        self.rxHighCheck = b'0'
        self.rxLowCheck = b'0'
        self.serialNumber = 0
        self.data = b''
        self.firstAutoDetetion = 1 # 第一次打开串口测试仪自动检测使能
        # 串口检测
        self.serialMonitor = PrivateSerialMonitor()  # 串口检测线程对象
        # self.comPortList = list()
        # self.comDescriptionList = list()
        self.serialMonitor.portChangeSignal.connect(self.portsMonitoring)
        self.serialMonitor.start()
        # 串口初始化
        self.serialManager = PrivateSerialThread()  # 串口接收线程对象
        self.prvSerial = self.serialManager.inUseSerial  # 获取全局实例化串口对象
        self.isSTM32Online = False # 测试仪是否在线
        self.serialManager.start()
        self.comDescription = ''
        self.comController = ''

    def initUi(self):
        self.setupUi(self)
        # 设置窗口居中显示
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()
        self.Wsize = self.geometry()
        centerX = int((self.width - self.Wsize.width()) / 2)
        centerY = int((self.height - self.Wsize.height()) / 2 - 20)
        self.move(centerX, centerY)
        self.setWindowTitle("Protocol")
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

    def autoConnectDetector(self):
        self.comboBox_selectComNum.setEnabled(True)
        self.comboBox_selectComNum.clear()  # 清空端口选择按钮
        self.serialMonitor.portList.clear()
        self.serialMonitor.descriptionList.clear()
        self.serialMonitor.searchPorts()
        self.comPortList = self.serialMonitor.portList.copy()
        self.comDescriptionList = self.serialMonitor.descriptionList.copy()
        if len(self.comPortList) == 0:
            self.protocolAppendSignal.emit("未检测到串口，请连接设备！")
        else:
            self.comboBox_selectComNum.addItems(self.comDescriptionList) # 
            self.comboBox_selectComNum.setEnabled(False)
            for i in self.comPortList:
                QApplication.processEvents()
                self.comDescription = i.description
                pInfo = QSerialPortInfo(i.device)
                pSta = pInfo.isBusy()  # 该串口状态
                if pSta == False:  # 该串口空闲
                    self.serialManager.initPort(i.device)
                    try:
                        self.prvSerial.open()
                        # if self.prvSerial.isOpen(): # 多余判断
                        self.protocolAppendSignal.emit("[" + i.device + "]已打开")
                        self.prvSerial.write(bytes("Terminal\r\n", encoding="utf-8"))
                        startTiming = dt.datetime.now()
                        endTiming = startTiming
                        # self.protocolAppendSignal.emit("等待测试仪回应")
                        while True: # 等待测试仪回应
                            QApplication.processEvents()
                            num = self.prvSerial.inWaiting()
                            # print("openClosePort num:" + str(num)) # 输出收到的字节数
                            if num == 0:
                                if (endTiming - startTiming).seconds >= 2:
                                    self.isSTM32Online = False
                                    self.prvSerial.close()
                                    self.protocolAppendSignal.emit("测试仪无响应，已关闭[" + i.device + "]")
                                    self.pushBtn_serialSwitch.setText("打开串口")
                                    self.comboBox_selectComNum.setEnabled(True)
                                    break
                            elif (num > 0 and num <= 4):
                                self.prvSerial.flushInput()
                            elif num >= 5:
                                QApplication.processEvents()
                                time.sleep(0.1)
                                data = self.prvSerial.read(num)
                                if data.decode("utf-8") == "STM32":
                                    self.isSTM32Online = True
                                    self.comController = self.comDescription
                                    self.protocolAppendSignal.emit("测试仪在线!")
                                    self.comboBox_selectComNum.setCurrentText(self.comController)
                                    self.comboBox_selectComNum.setEnabled(False)
                                    self.pushBtn_serialSwitch.setText("关闭串口")
                                    print('/*+++++++++++++++++++++++++++++++++++++++++++++*/\nChecking device parameters ......:')
                                    self.deviceSelfCheck() # 每次运行程序执行一次自检即可
                                    break
                            endTiming = dt.datetime.now()
                    except:
                        QMessageBox.warning(self, "打开串口", "打开串口失败")
                        self.protocolAppendSignal.emit("[" + self.comPortList[self.comIndex].device + "] 打开失败")
                if self.isSTM32Online == True:
                    break

    def portsMonitoring(self, list):
        if list[0] == 'NOCOM':
            self.comController = ''
            self.comPortList.clear()
            self.comDescriptionList.clear()
            self.protocolAppendSignal.emit("当前已无串口")
            print(str(list[0]))
            self.comboBox_selectComNum.setEnabled(True)
            self.comboBox_selectComNum.clear() # 清空端口选择按钮 
            if self.prvSerial.isOpen():
                self.prvSerial.close()
            self.pushBtn_serialSwitch.setText('打开串口')
        else:
            print(str(list))
            self.protocolAppendSignal.emit("串口发生改变")
            self.comboBox_selectComNum.setEnabled(True)
            self.comboBox_selectComNum.clear() # 清空端口选择按钮
            self.comPortList = self.serialMonitor.portList.copy()
            self.comDescriptionList = self.serialMonitor.descriptionList.copy()
            if len(self.comDescriptionList) != 0:
                for p in self.comDescriptionList:
                    self.comboBox_selectComNum.addItem(p)
            self.pushBtn_serialSwitch.setText('打开串口')
            if (self.comController != '') and (not self.comController in self.comDescriptionList):
                self.prvSerial.close()
                # self.protocolAppendSignal.emit('控制仪串口已拔出')
                self.comboBox_selectComNum.setCurrentText(self.comDescription)
                self.comboBox_selectComNum.setEnabled(True)
            elif (self.comController != '') and (self.comController in self.comDescriptionList):
                # self.protocolAppendSignal.emit('控制仪串口已接入')
                self.comIndex = self.comDescriptionList.index(self.comController)
                self.portInfo = QSerialPortInfo(self.comPortList[self.comIndex].device)  # 该串口信息
                self.portStatus = self.portInfo.isBusy()  # 该串口状态
                if self.portStatus == False:  # 该串口空闲
                    self.serialManager.initPort(self.comPortList[self.comIndex].device)
                    if not self.prvSerial.isOpen():
                        self.prvSerial.open()
                self.pushBtn_serialSwitch.setText('关闭串口')
                self.comboBox_selectComNum.setCurrentText(self.comController)
                self.comboBox_selectComNum.setEnabled(False)

    @QtCore.pyqtSlot()
    def on_pushBtn_serialSwitch_clicked(self):
        staText = self.pushBtn_serialSwitch.text()
        self.idlePorts = QSerialPortInfo.availablePorts()
        if staText == "打开串口":
            if len(self.idlePorts) >= 1:  # 检测到有串口
                self.comDescription = self.comboBox_selectComNum.currentText()  # 获取comboBox当前串口描述
                self.comIndex = self.comDescriptionList.index(self.comDescription)
                self.portInfo = QSerialPortInfo(self.comPortList[self.comIndex].device)  # 该串口信息
                self.portStatus = self.portInfo.isBusy()  # 该串口状态
                if self.portStatus == False:  # 该串口空闲
                    self.serialManager.initPort(self.comPortList[self.comIndex].device)
                    try:
                        self.prvSerial.open()
                        # if self.prvSerial.isOpen():
                        self.protocolAppendSignal.emit("[" + self.comPortList[self.comIndex].device + "]已打开")
                        self.pushBtn_serialSwitch.setText("关闭串口")
                        self.comboBox_selectComNum.setEnabled(False)
                        self.pushBtn_serialSwitch.setEnabled(False)
                    except:
                        QMessageBox.warning(self, "打开串口", "打开串口失败")
                        self.protocolAppendSignal.emit("[" + self.comPortList[self.comIndex].device + "]打开失败")
                    if self.prvSerial.isOpen(): 
                        self.prvSerial.flush()
                        self.prvSerial.write(bytes("Terminal\r\n", encoding="utf-8"))
                        startTiming = dt.datetime.now()
                        endTiming = startTiming
                        # self.protocolAppendSignal.emit("等待测试仪回应")
                        while True: # 等待测试仪回应
                            QApplication.processEvents()
                            num = self.prvSerial.inWaiting()
                            # print("openClosePort num:" + str(num)) # 输出收到的字节数
                            if num == 0:
                                if (endTiming - startTiming).seconds >= 2:
                                    self.prvSerial.close()
                                    self.protocolAppendSignal.emit("测试仪无响应，请执行操作")
                                    self.comboBox_selectComNum.setEnabled(True)
                                    self.pushBtn_serialSwitch.setEnabled(True)
                                    self.pushBtn_serialSwitch.setText("打开串口")
                                    self.isSTM32Online = False
                                    break
                            elif (num > 0 and num <= 4):
                                self.prvSerial.flushInput()
                            elif num >= 5:
                                time.sleep(0.01)
                                data = self.prvSerial.read(num)
                                if data.decode("utf-8") == "STM32":
                                    self.isSTM32Online = True
                                    self.comController = self.comDescription
                                    break
                            endTiming = dt.datetime.now()        
                        if self.isSTM32Online == True:
                            if self.firstAutoDetetion == 1: # 第一次打开软件会执行测试仪自检
                                self.firstAutoDetetion = 0
                                self.protocolAppendSignal.emit("测试仪在线!")
                                self.close()
                                self.deviceSelfCheck() # 每次重新运行程序执行一次自检
                            else:
                                self.protocolAppendSignal.emit("测试仪在线，请执行操作")
                                self.close()
                        self.pushBtn_serialSwitch.setEnabled(True)
                        
                else:
                    QMessageBox.warning(self, "串口状态", "串口使用中")
            else:  # 打开时检测到无串口
                self.protocolAppendSignal.emit("未检测到串口，请连接设备")
                QMessageBox.information(self, "串口信息", "未检测到串口!", QMessageBox.Yes)
        elif staText == "关闭串口":
            self.prvSerial.close()
            self.protocolAppendSignal.emit("[" + self.comPortList[self.comIndex].device + "]已关闭")
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
        self.rxHighCheck, self.rxLowCheck = self.convert.convertCheck(self.rxCheck & 0xFF)
        if (self.data[0] == 85) and (self.data[dataLength - 4] == self.rxHighCheck) and (self.data[dataLength - 3] == self.rxLowCheck) and \
           (self.data[dataLength - 2] == 13) and (self.data[dataLength - 1] == 10):
            print("RxFrame is right!")
            return State.s_RxFrameCheckOK
        else:
            print("RxFrame is wrong!")
            return State.s_RxFrameCheckErr

    def txFrameFormatting(self, func, uid, configPath):
        self.txCheck = 0 # 校验和清零
        self.txHighCheck = "0",
        self.txLowCheck = "0"
        try:
            if func == Func.f_DevGetSelfPara or func == Func.f_DevQueryCurrentCode:
                tmp = str("D" + str(self.serialNumber) + func)
            elif func == Func.f_DevEncoding or func == Func.f_DevDetection or func == Func.f_DevEncodingDetection:
                tmp = str("D" + str(self.serialNumber) + func + uid)
            elif func == Func.f_DevSettingThreshold:
                with open(configPath, 'r') as rf:
                    configContents = rf.read()
                tmp = str("D" + str(self.serialNumber) + func + configContents)
            tmp = tmp.encode("utf-8")
            if self.serialNumber == 9:  # 流水号
                self.serialNumber = 0
            else:
                self.serialNumber += 1
            txData = tmp
        except:
            print("Transfromed txData to bytes type failed!")
            return
        for ch in txData:  # 计算校验和
            self.txCheck += ch
        self.txHighCheck, self.txLowCheck = self.convert.convertCheck(self.txCheck & 0xFF)
        byteTmp = bytearray(txData)
        byteTmp.append(self.txHighCheck)
        byteTmp.append(self.txLowCheck)
        byteTmp.append(0x0D)
        byteTmp.append(0x0A)

        return byteTmp
    
    def serialSendData(self, func, uid, configPath):
        if self.prvSerial.isOpen():
            self.comIndex = self.comDescriptionList.index(self.comDescription) # 索引
            self.portInfo = QSerialPortInfo(self.comPortList[self.comIndex].device)  # 该串口信息
            if self.portInfo.isBusy():# 该串口状态
                self.prvSerial.flush()
                self.data = b""
                self.writeData = b""
                try:
                    self.writeData = self.txFrameFormatting(func, uid, configPath)
                    self.prvSerial.write(self.writeData)
                except:
                    QMessageBox.critical(self, "串口信息", "发送数据失败")
                finally:
                    self.prvSerial.flushOutput()
            else:
                QMessageBox.warning(self, "串口信息", "串口使用中")
        else:
            QMessageBox.information(self, "串口信息", "串口未打开\n请打开串口", QMessageBox.Yes)
            self.protocolAppendSignal.emit("串口未打开")

    def deviceSelfCheck(self):
        self.prvSerial.flush()
        self.data = b''
        self.rxCheck = 0
        self.prvSerial.flush()
        time.sleep(1)
        self.protocolAppendSignal.emit("测试仪自检")
        self.serialSendData(Func.f_DevGetSelfPara, '', '')