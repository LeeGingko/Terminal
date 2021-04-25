# -*- coding: utf-8 -*-
# 导入time相关模块
import time

class Tools:
    def getTimeStamp(self):
        return time.strftime("[At %H:%M:%S]>", time.localtime())

    def convertCheck(self, check):
        ch = bytearray([0,0,0,0])
        ch[0] = ((check & 0xF0) >> 4) - 10 + 65
        ch[1] = (check & 0x0F) - 10 + 65
        ch[2] = ((check & 0xF0) >> 4) + 48
        ch[3] = (check & 0x0F) + 48
        # 校验和高四位
        if(((check & 0xF0) >> 4) >= 10):
            highCheck = ch[0]
        else:
            highCheck = ch[2]
        # 校验和低四位
        if((check & 0x0F) >= 10):
            lowCheck = ch[1]
        else:
            lowCheck = ch[3]

        return highCheck, lowCheck
