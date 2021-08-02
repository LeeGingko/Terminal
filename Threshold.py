# -*- coding: utf-8 -*-
import os
# 导入pickle模块
import pickle as pk

# 默认导入
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox

# getset全局变量
import GetSetObj
# 导入参数设置界面
from Ui_Threshold import Ui_ThresholdDialog
# 导入功能枚举
from Utilities.Enum.FuncEnum import Func
# 导入验证器
from Utilities.Validator.ValidatorBox import VLDR_INTFOLAT


class ThresholdWin(QDialog, Ui_ThresholdDialog):
    thresholdAppendSignal = pyqtSignal(str)
    openFileSignal = pyqtSignal(str)

    def __init__(self):
        super(ThresholdWin, self).__init__()  # 继承父类的所有属性
        self.initUi()
        # 配置文件保存变量的初始化
        # self.isConfigSavedFirst = True # 是否是第一次保存
        # self.isConfigSaved = True # 是否是已经保存 
        self.configPath = "" # 文件路径
        # 阈值初始化
        self.paraDict = { # 参数字典
            "th_DrainCurrent_Up": "0", "th_DrainCurrent_Down": "0",
            "th_WorkCurrent_Up":  "0", "th_WorkCurrent_Down":  "0",
            "th_FireVoltage_Up":  "0", "th_FireVoltage_Down":  "0",
            "th_FireCurrent_Up":  "0", "th_FireCurrent_Down":  "0",
            "th_LineVoltage_Up":  "0", "th_LineVoltage_Down":  "0",
            "th_LineCurrent_Up":  "0", "th_LineCurrent_Down":  "0",
            "th_ComVoltage_Up":   "0", "th_ComVoltage_Down":   "0",
            "th_ComCurrent_Up":   "0", "th_ComCurrent_Down":   "0" }
        self.getUserPara()
        # 漏电流
        self.dcUpVdt = VLDR_INTFOLAT(150, 110)
        self.lineEdit_setDrainCurrentTop.setValidator(self.dcUpVdt)
        self.lineEdit_setDrainCurrentTop.setToolTip('[150, 110]')
        self.dcDnVdt = VLDR_INTFOLAT(50, 0)
        self.lineEdit_setDrainCurrentBottom.setValidator(self.dcDnVdt)
        self.lineEdit_setDrainCurrentBottom.setToolTip('[50, 0]')
        # 工作电流
        self.wcUpVdt = VLDR_INTFOLAT(2500, 1500)
        self.lineEdit_setWorkCurrentTop.setValidator(self.wcUpVdt)
        self.lineEdit_setWorkCurrentTop.setToolTip('[2500, 1500]')
        self.wcDnVdt = VLDR_INTFOLAT(500, 0)
        self.lineEdit_setWorkCurrentBottom.setValidator(self.wcDnVdt)
        self.lineEdit_setWorkCurrentBottom.setToolTip('[500, 0]')
        # 起爆电压
        self.fvUpVdt = VLDR_INTFOLAT(76, 74)
        self.lineEdit_setFireVoltageTop.setValidator(self.fvUpVdt)
        self.lineEdit_setFireVoltageTop.setToolTip('[76, 74]')
        self.fvDnVdt = VLDR_INTFOLAT(70, 68)
        self.lineEdit_setFireVoltageBottom.setValidator(self.fvDnVdt)
        self.lineEdit_setFireVoltageBottom.setToolTip('[70, 68]')
        # 起爆电流
        self.fcUpVdt = VLDR_INTFOLAT(550, 500)
        self.lineEdit_setFireCurrentTop.setValidator(self.fcUpVdt)
        self.lineEdit_setFireCurrentTop.setToolTip('[550, 500]')
        self.fcDnVdt = VLDR_INTFOLAT(350, 0)
        self.lineEdit_setFireCurrentBottom.setValidator(self.fcDnVdt)
        self.lineEdit_setFireCurrentBottom.setToolTip('[350, 0]')
        # 线路电压
        self.lvUpVdt = VLDR_INTFOLAT(26, 24)
        self.lineEdit_setLineVoltageTop.setValidator(self.lvUpVdt)
        self.lineEdit_setLineVoltageTop.setToolTip('[26, 24]')
        self.lvDnVdt = VLDR_INTFOLAT(22, 20)
        self.lineEdit_setLineVoltageBottom.setValidator(self.lvDnVdt)
        self.lineEdit_setLineVoltageBottom.setToolTip('[22, 20]')
        # 线路电流
        self.lcUpVdt = VLDR_INTFOLAT(14, 12)
        self.lineEdit_setLineCurrentTop.setValidator(self.lcUpVdt)
        self.lineEdit_setLineCurrentTop.setToolTip('[14, 12]')
        self.lcDnVdt = VLDR_INTFOLAT(6, 0)
        self.lineEdit_setLineCurrentBottom.setValidator(self.lcDnVdt)
        self.lineEdit_setLineCurrentBottom.setToolTip('[6, 0]')
        # 通信电压
        self.cvUpVdt = VLDR_INTFOLAT(38, 34)
        self.lineEdit_setComVoltageTop.setValidator(self.cvUpVdt)
        self.lineEdit_setComVoltageTop.setToolTip('[38, 34]')
        self.cvDnVdt = VLDR_INTFOLAT(32, 30)
        self.lineEdit_setComVoltageBottom.setValidator(self.cvDnVdt)
        self.lineEdit_setComVoltageBottom.setToolTip('[32, 30]')
        # 通信电流
        self.ccUpVdt = VLDR_INTFOLAT(36, 32)
        self.lineEdit_setComCurrentTop.setValidator(self.ccUpVdt)
        self.lineEdit_setComCurrentTop.setToolTip('[36, 32]')
        self.ccDnVdt = VLDR_INTFOLAT(20, 8)
        self.lineEdit_setComCurrentBottom.setValidator(self.ccDnVdt)
        self.lineEdit_setComCurrentBottom.setToolTip('[20, 8]')

    def initUi(self):
        self.setupUi(self)
        # 设置窗口居中显示
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.width = self.screenRect.width()
        self.height = self.screenRect.height()
        self.Wsize = self.geometry()
        centerX = int((self.width - self.Wsize.width()) / 2)
        centerY = int((self.height - self.Wsize.height()) / 2)
        self.move(centerX, centerY)
        self.setWindowTitle("Threshold")
        iconPath = os.path.join(os.getcwd(),'./resources/icons/IDDD.ico')
        self.setWindowIcon(QIcon(iconPath))
        self.configFolder = os.path.join(os.getcwd(), 'configurations')
        self.setWindowFlags(Qt.WindowCloseButtonHint|Qt.WindowMinimizeButtonHint|Qt.WindowStaysOnTopHint)
        # 阻塞父类窗口不能点击
        self.setWindowModality(Qt.ApplicationModal)
        
    def getUserPara(self):
        self.paraDict["th_DrainCurrent_Up"  ] = self.lineEdit_setDrainCurrentTop.text()
        self.paraDict["th_DrainCurrent_Down"] = self.lineEdit_setDrainCurrentBottom.text()
        self.paraDict["th_WorkCurrent_Up"   ] = self.lineEdit_setWorkCurrentTop.text()
        self.paraDict["th_WorkCurrent_Down" ] = self.lineEdit_setWorkCurrentBottom.text()
        self.paraDict["th_FireVoltage_Up"   ] = self.lineEdit_setFireVoltageTop.text()
        self.paraDict["th_FireVoltage_Down" ] = self.lineEdit_setFireVoltageBottom.text()
        self.paraDict["th_FireCurrent_Up"   ] = self.lineEdit_setFireCurrentTop.text()
        self.paraDict["th_FireCurrent_Down" ] = self.lineEdit_setFireCurrentBottom.text()
        self.paraDict["th_LineVoltage_Up"   ] = self.lineEdit_setLineVoltageTop.text()
        self.paraDict["th_LineVoltage_Down" ] = self.lineEdit_setLineVoltageBottom.text()
        self.paraDict["th_LineCurrent_Up"   ] = self.lineEdit_setLineCurrentTop.text()
        self.paraDict["th_LineCurrent_Down" ] = self.lineEdit_setLineCurrentBottom.text()
        self.paraDict["th_ComVoltage_Up"    ] = self.lineEdit_setComVoltageTop.text()
        self.paraDict["th_ComVoltage_Down"  ] = self.lineEdit_setComVoltageBottom.text()
        self.paraDict["th_ComCurrent_Up"    ] = self.lineEdit_setComCurrentTop.text()
        self.paraDict["th_ComCurrent_Down"  ] = self.lineEdit_setComCurrentBottom.text()
    
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

    def settingThreshold(self):
        print("Setting threshold.................: ")
        self.thresholdAppendSignal.emit("下发参数到测试仪")
        self.pSerial = GetSetObj.get(1)
        if self.pSerial.prvSerial.isOpen():
            self.pSerial.data = b''
            self.pSerial.rxCheck = 0
            self.pSerial.prvSerial.flush()
            self.pSerial.serialSendData(Func.f_DevSettingThreshold, '', self.configPath)
        else:
            self.thresholdAppendSignal.emit("下发阈值@串口未打开")
    
    def firstSaveThreshold(self, text):
        if self.configPath == "":
            self.configPath, isAccept =  QFileDialog.getSaveFileName(self, "保存文件", "./config", "settingfiles (*.txt)")
            if isAccept:
                if self.configPath:
                    with open(self.configPath, encoding="utf-8", mode="w") as fsf:
                        fsf.write(text)
                    self.isConfigSavedFirst = False
                    self.isConfigSaved = True
                self.thresholdAppendSignal.emit("参数保存成功")
                self.thresholdAppendSignal.emit("@保存至\"" + str(self.configPath) + "\"")
                # self.saveConfigRecord()
                self.settingThreshold()
        else:
            pass

    def saveThreshold(self, text):
        with open(self.configPath, encoding="utf-8", mode="w") as sf:
            sf.write(text)
        self.settingThreshold()

    def getThreshold(self):
        self.getUserPara()
        cnt = 0
        self.para = ""
        for k, v in self.paraDict.items():
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

    def aloneSaveSettingsRecord(self):
        print("/*>>>>>>>>>>>>>>>>>>>>>aloneSaveSettingsRecord>>>>>>>>>>>>>>>>>>>>>>>>*/")
        self.getThreshold()
        self.saveThreshold(self.para)

    @QtCore.pyqtSlot()
    def on_pushBtn_saveSettingsRecord_clicked(self):
        print("/*>>>>>>>>>>>>>>>>>>>>on_pushBtn_saveSettingsRecord_clicked>>>>>>>>>>>>>>>>>>>>>>>>>*/")
        self.getThreshold()
        self.saveThreshold(self.para)
        
    @QtCore.pyqtSlot()
    def on_pushBtn_readSettingsRecord_clicked(self):
        file = os.path.join(self.configFolder, 'config.txt')
        settingfile, _ = QFileDialog.getOpenFileName(self, "打开配置文件", file, 'settingfile (config.txt)')
        if settingfile:
            os.startfile(settingfile)
            self.openFileSignal.emit(settingfile)
            self.close()
