# -*- coding: utf-8 -*-
import sys
# 导入time相关模块
import time

class Tools(object):
    def getTimeStamp():
        return time.strftime("[%Y/%m/%d %H:%M:%S]>", time.localtime())