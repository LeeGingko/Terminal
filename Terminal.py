# -*- coding: utf-8 -*-
import sys

# 导入time相关模块
import time

# 导入serial相关模块
import serial
import serial.tools.list_ports
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import *

# 导入功能枚举
from FuncEnum import Func

# 导入主窗口类
from Ui_Detector import Ui_MainWindow

# 导入qrc资源
from resources import resources_rc

class MainWin(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__() # 继承父类的所有属性

        # initialization of UI
        self.initUi()

        # initialization of serial receive data timer
        self.timer_serial_recv = QTimer(self)
        self.timer_serial_recv.timeout.connect(self.serialRecvData)

        # system datetime timer
        self.timer_datetime = QTimer(self)
        self.timer_datetime.timeout.connect(self.showDaetTime)
        self.timer_datetime.start(1000)

        # signal<--bind-->slot
        self.connectSignalAndSlot()

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

    def connectSignalAndSlot(self):
        self.pushBtn_serialSwitch.clicked.connect(self.switchPort)
        self.pushBtn_confirmUidInput.clicked.connect(self.serialSendData)
        self.pushBtn_clearUidInput.clicked.connect(self.clearUidInput)
    
    def showDaetTime(self):
        dateTimeStr = time.strftime("%Y年%m月%d日\n%H:%M:%S ", time.localtime())
        dayOfWeek = time.localtime().tm_wday
        if dayOfWeek == 0:
            dateTimeStr = dateTimeStr + "星期一"
        elif dayOfWeek == 1:
            dateTimeStr = dateTimeStr + "星期二"
        elif dayOfWeek == 2:
            dateTimeStr = dateTimeStr + "星期三"
        elif dayOfWeek == 3:
            dateTimeStr = dateTimeStr + "星期四"
        elif dayOfWeek == 4:
            dateTimeStr = dateTimeStr + "星期五"
        elif dayOfWeek == 5:
            dateTimeStr = dateTimeStr + "星期六"
        elif dayOfWeek == 6:
            dateTimeStr = dateTimeStr + "星期天"
        self.label_localDateTime.setText(dateTimeStr)
    
    # 
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
        else:
            print("No port detected!")
            self.statusbar.showMessage("未检测到串口")
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
                            self.timer_serial_recv.start(10)
                            self.pushBtn_serialSwitch.setText("关闭串口")
                            self.comboBox_selectComNum.setEnabled(False)
                    except:
                        QMessageBox.warning(self, "打开串口", "打开串口失败")
                else:
                    QMessageBox.warning(self, "串口状态", "串口使用中或已拔出")
            else:  # 打开时检测到无串口
                QMessageBox.information(
                    self, "串口信息", "请连接好设备!", QMessageBox.Yes)
        elif staText == "关闭串口":
            self.timer_serial_recv.stop()
            self.serialInstance.close()
            self.pushBtn_serialSwitch.setText("打开串口")
            self.comboBox_selectComNum.setEnabled(True)
    
    def parseFunc(self):
        # self.tmp = bytearray(self.data)
        for b in self.tmp:
            print(b, end=" ")

    def rxFrameCheck(self):
        self.rxCheck = 0 # 校验和清零
        for ch in self.tmp: # 计算校验和
            self.rxCheck += ch
        dataLength = len(self.data)
        self.convertCheck(self.rxCheck) # 
        self.rxHighCheck = self.highCheck
        self.rxLowCheck = self.lowCheck
        if (self.data[0] == 68) and (self.data[dataLength-4] == self.rxHighCheck) and (self.data[dataLength-3] == self.rxLowCheck) and \
           (self.data[dataLength-2] == 13) and (self.data[dataLength-1] == 10):
            print("RxFrame is correct!!")
        else:
            print("RxFrame is mistake!!")

    def serialRecvData(self):
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

    def serialSendData(self):
        if self.serialInstance.isOpen():
            if self.lineEdit_uidInput.text() != "":
                self.comDescription = self.comboBox_selectComNum.currentText()  # 获取comboBox当前串口描述
                self.comIndex = self.comDescriptionList.index(self.comDescription)
                self.portInfo = QSerialPortInfo(self.comPortList[self.comIndex].device)  # 该串口信息
                self.portStatus = self.portInfo.isBusy()  # 该串口状态
                self.uid = self.lineEdit_uidInput.text()  # 获取编号
                if self.portStatus == True:
                    try:
                        self.sendByFunc(Func.f_CheckMode)
                        # self.serialInstance.write(bytes("D00FRANK16" + "\r\n", encoding="utf-8"))
                    except:
                        QMessageBox.warning(self, "串口信息", "发送数据失败")
                    finally:
                        self.serialInstance.flushOutput()
                else:
                    QMessageBox.warning(self, "串口信息", "串口使用中或已拔出")
            else:
                QMessageBox.information(self, "输入编号", "编号输入为空!\n请输入编号", QMessageBox.Yes)
        else:
            QMessageBox.information(self, "串口信息", "串口未打开\n请先打开串口", QMessageBox.Yes)
    
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

    def sendByFunc(self, func):
        self.writeData = ""
        self.txCheck = 0
        if func == "0":
            try:
                self.tmp = str("D" + self.serialNumber + func + self.uid)
                self.tmp = self.tmp.encode("utf-8")
            except:
                print("self.tmp to bytes failed!")
                return
            for ch in self.tmp: # 计算校验和
                self.txCheck += ch
            self.convertCheck(self.txCheck)
            self.txHighCheck = self.highCheck
            self.txLowCheck = self.lowCheck
            byteTmp = bytearray(self.tmp)
            byteTmp.append(self.txHighCheck)
            byteTmp.append(self.txLowCheck)
            byteTmp.append(0x0D)
            byteTmp.append(0x0A)
            self.writeData = byteTmp
            self.serialInstance.write(self.writeData)
        elif func == "1":
            self.serialInstance.write(self.writeData)
        elif func == "2":
            self.serialInstance.write(self.writeData)
        self.serialNumber = str(int(self.serialNumber) + 1) # 流水号
        if self.serialNumber == '10':
            self.serialNumber = "0"

    def clearUidInput(self):
        self.lineEdit_uidInput.clear()

    def closeEvent(self, QCloseEvent):
        choice = QMessageBox.question(self, "窗口消息", "是否要关闭窗口？",
                                      QMessageBox.Yes | QMessageBox.Cancel)
        if choice == QMessageBox.Yes:
            QCloseEvent.accept()
        elif choice == QMessageBox.Cancel:
            QCloseEvent.ignore() 

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    DetectorWin = MainWin()
    DetectorWin.show()
    sys.exit(app.exec_())
