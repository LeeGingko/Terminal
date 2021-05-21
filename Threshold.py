# -*- coding: utf-8 -*-
import os
# 导入pickle模块
import pickle as pk

# 默认导入
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog

# getset全局变量
import GetSetObj
# 导入参数设置界面
from Ui_Threshold import Ui_ThresholdDialog
# 导入功能枚举
from Utilities.Enum.FuncEnum import Func


class ThresholdWin(QDialog, Ui_ThresholdDialog):
    thresholdAppendSignal = pyqtSignal(str)

    def __init__(self):
        super(ThresholdWin, self).__init__()  # 继承父类的所有属性
        self.initUi()
        # 配置文件保存变量的初始化
        self.isConfigSavedFirst = True # 是否是第一次保存
        self.isConfigSaved = True # 是否是已经保存 
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
        # self.settingThreshold()

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
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

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
        print("settingThreshold: ")
        self.thresholdAppendSignal.emit("下发参数到测试仪")
        self.pSerial = GetSetObj.get()
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
                    with open(self.configPath, "w") as fsf:
                        fsf.write(text)
                    self.isConfigSavedFirst = False
                    self.isConfigSaved = True
                self.thresholdAppendSignal.emit("参数保存成功")
                self.thresholdAppendSignal.emit("@保存至\"" + str(self.configPath) + "\"")
                self.saveConfigRecord()
                self.settingThreshold()
        else:
            pass

    def saveThreshold(self, text):
        with open(self.configPath, encoding="utf-8", mode="w") as sf:
            sf.write(text)
        self.isConfigSaved = True
        self.thresholdAppendSignal.emit("保存配置参数成功")
        # print(self.usualTools.getTimeStamp() + "下发参数")
        self.settingThreshold()
        self.saveConfigRecord()

    @QtCore.pyqtSlot()
    def on_pushBtn_saveSettingsRecord_clicked(self):
        print("/*>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>*/")
        print("Setting parameters's threshold ......")
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
