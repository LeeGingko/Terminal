# -*- coding: utf-8 -*-

from GlobalVariable import GlobalVar

def get():
   # print("get obj:" + str(GlobalVar.getgObj()))
   return GlobalVar.getgObj()

def set(val):
   # print("set obj:" + str(val))
   GlobalVar.setgObj(val)  