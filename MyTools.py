# -*- coding: utf-8 -*-
import sys
# 导入time相关模块
import time

class Tools(object):
    def getTimeStamp():
        # time.sleep(0.2)
        s = time.strftime("[%H:%M:%S]>", time.localtime())
        # s = time.strftime("[%Y/%m/%d %H:%M:%S]>", time.localtime())
        return s