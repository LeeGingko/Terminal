# 导入系统模块
import sys

# 默认导入
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *


class PrivateEvent(QEvent):
    def __init__(self):
        super(PrivateEvent, self).__init__()
    
        self.singnal = QEvent().getName() 