# -*- coding: utf-8 -*-

class GlobalVar():
    gObjSerial = None # 串口实例全局对象
    gObjThreshold = None # 阈值界面全局对象
    
    def setgObj(self, index, val): # 设置全局对象
        if index == 1:
            GlobalVar.gObjSerial = val
        elif index == 2:
            GlobalVar.gObjThreshold = val     
 
    def getgObj(self, index): # 获取全局对象
        if index == 1:
            return GlobalVar.gObjSerial
        elif index == 2:
            return GlobalVar.gObjThreshold