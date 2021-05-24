# 导入系统模块
import sys

# 默认导入
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import *

class PrivateStateMachine(QStateMachine):
    def __init__(self):
        super(PrivateStateMachine, self).__init__()
        self.autoInitStateMachine = QStateMachine()
        self.autoInitState = QState()
        self.autoInitInitialState = QState(self.autoInitState)
        self.autoInitSendState = QState(self.autoInitState)
        self.autoInitResopnseState = QState(self.autoInitState)
        self.autoInitFinalState = QFinalState(self.autoInitState)        
        self.autoInitHistoryState = QHistoryState(self.autoInitState)