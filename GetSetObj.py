# -*- coding: utf-8 -*-
from GlobalVariable import GlobalVar

gObjInstance = GlobalVar()

def get(index):
   return gObjInstance.getgObj(index)

def set(index, val):
   gObjInstance.setgObj(index, val)