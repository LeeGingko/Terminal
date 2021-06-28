# -*- coding: utf-8 -*-

class GlobalVar():
    gObjSerial = None
    gObjThreshold = None
    
    def setgObj(self, index, val):
        if index == 1:
            GlobalVar.gObjSerial = val
        elif index == 2:
            GlobalVar.gObjThreshold = val     
 
    def getgObj(self, index):
        if index == 1:
            return GlobalVar.gObjSerial
        elif index == 2:
            return GlobalVar.gObjThreshold