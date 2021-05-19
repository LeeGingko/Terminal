# 导入系统模块
import sys

# 默认导入
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import *

from Ui_Win import Ui_StateMachineWin


class PrivateStateMachine(QtWidgets.QWidget, Ui_StateMachineWin):
    def __init__(self):
        super(PrivateStateMachine, self).__init__()
        self.initUi()
        self.processing()

    def initUi(self):
        self.setupUi(self)

    def processing(self):
        self.stateMachine = QStateMachine()
    # 1 A Simple State Machine
        # self.s1 = QState()
        # self.s2 = QState()
        # self.s3 = QState()
        
        # self.s1.addTransition(self.btn1.clicked, self.s2)
        # self.s2.addTransition(self.btn1.clicked, self.s3)
        # self.s3.addTransition(self.btn1.clicked, self.s1)

        # self.s1.assignProperty(self.label, "text", "S1")
        # self.s2.assignProperty(self.label, "text", "S2")
        # self.s3.assignProperty(self.label, "text", "S3")

        # self.stateMachine.addState(self.s1)
        # self.stateMachine.addState(self.s2)
        # self.stateMachine.addState(self.s3)

        # self.stateMachine.setInitialState(self.s2)
        # self.stateMachine.start()
    # 2 Sharing Transitions By Grouping States
        # self.s1 = QState()

        # self.s11 = QState(self.s1)
        # self.s12 = QState(self.s1)
        # self.s13 = QState(self.s1)

        # self.s11.addTransition(self.btn1.clicked, self.s12)
        # self.s12.addTransition(self.btn1.clicked, self.s13)
        # self.s13.addTransition(self.btn1.clicked, self.s11)
        # self.s11.assignProperty(self.label, "text", "S11")
        # self.s12.assignProperty(self.label, "text", "S12")
        # self.s13.assignProperty(self.label, "text", "S13")

        # self.s1.setInitialState(self.s11)
        # self.stateMachine.addState(self.s1) 

        # self.s2 = QFinalState()
        # self.s1.addTransition(self.btn2.clicked, self.s2)
        
        # self.stateMachine.addState(self.s2)
        # self.stateMachine.en
        # self.stateMachine.finished.connect(self.close)

        # self.stateMachine.setInitialState(self.s1)
        # self.stateMachine.start()

    # 3 Using History States to Save and Restore the Current State
        # self.s1 = QState()
        # self.s1.entered.connect(self.enterState1)

        # self.s11 = QState(self.s1)
        # self.s12 = QState(self.s1)
        # self.s13 = QState(self.s1)

        # self.s11.addTransition(self.btn1.clicked, self.s12)
        # self.s12.addTransition(self.btn1.clicked, self.s13)
        # self.s13.addTransition(self.btn1.clicked, self.s11)
        # self.s11.assignProperty(self.label, "text", "S11")
        # self.s12.assignProperty(self.label, "text", "S12")
        # self.s13.assignProperty(self.label, "text", "S13")

        # self.s1.setInitialState(self.s11)
        # self.stateMachine.addState(self.s1) 

        # self.s2 = QState()
        # self.s1.addTransition(self.btn2.clicked, self.s2)
        # self.s2.assignProperty(self.label, "text", "S2")
        # self.stateMachine.addState(self.s2)

        # self.s1h = QHistoryState(self.s1)

        # self.s3 = QState()
        # self.s2.addTransition(self.btn3.clicked, self.s3)
        # self.s3.assignProperty(self.label, "text", "S3")
        # self.s3.entered.connect(self.enterState3)
        # self.s3.addTransition(self.s1h)
        # self.stateMachine.addState(self.s3)

        # self.stateMachine.setInitialState(self.s1)
        # self.stateMachine.start()

    # Using Parallel States to Avoid a Combinatorial Explosion of States
        self.s1 = QState(QState.ParallelStates)
        self.s11 = QState(self.s1)
        self.s12 = QState(self.s1)
        self.stateMachine.addState(self.s1) ## 直接添加s1

        self.s11_move = QState(self.s11)
        self.s11_notMove = QState(self.s11)
        self.s11_move.assignProperty(self.label_carMove, 'text', 'Moving')
        self.s11_notMove.assignProperty(self.label_carMove, 'text', 'Not Moving')
        self.s11_notMove.addTransition(self.btn_started.clicked, self.s11_move)
        self.s11_move.addTransition(self.btn_stopped.clicked, self.s11_notMove)
        self.s11.setInitialState(self.s11_notMove)

        self.s12_dirty = QState(self.s12)
        self.s12_clean = QState(self.s12)
        self.s12_dirty.assignProperty(self.label_carAir, 'text', 'Dirty')
        self.s12_clean.assignProperty(self.label_carAir, 'text', 'Cleaned')
        self.s12_clean.addTransition(self.btn_soiled.clicked, self.s12_dirty)
        self.s12_dirty.addTransition(self.btn_cleaned.clicked, self.s12_clean)
        self.s12.setInitialState(self.s12_clean)

        self.stateMachine.setInitialState(self.s1) 
        self.stateMachine.start()

    def enterState1(self):
        self.label.setText("St")
        QMessageBox.information(self, "enterStatet", "enterState1!", QMessageBox.Yes)

    def enterState3(self):
        QMessageBox.information(self, "Interrupted", "State3 entered!", QMessageBox.Yes)

    @pyqtSlot()
    def on_btn1_clicked(self):
        print('on_btn1_clicked')

    @pyqtSlot()
    def on_btn2_clicked(self):
        print('on_btn2_clicked')

    @pyqtSlot()
    def on_btn3_clicked(self):
        print('on_btn3_clicked')

    def closeEvent(self, QCloseEvent):
        print("退出主窗口")
        app = QApplication.instance()
        app.quit()

if __name__ == "__main__":
    App = QApplication(sys.argv)
    Terminal = PrivateStateMachine()
    Terminal.show()
    sys.exit(App.exec_()) 
