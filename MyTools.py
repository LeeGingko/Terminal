# -*- coding: utf-8 -*-
import sys
# 导入time相关模块
import time

class Tools:
    def getTimeStamp(self):
        s = time.strftime("[%Y/%m/%d %H:%M:%S]>", time.localtime())
        return s