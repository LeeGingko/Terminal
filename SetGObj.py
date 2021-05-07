# -*- coding: utf-8 -*-

from GlobalVariable import GlobalVar

def set(val):
    print("set obj:" + str(val))
    GlobalVar.setgObj(val) 