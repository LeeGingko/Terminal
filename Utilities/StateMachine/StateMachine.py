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
        # s3状态
        # self.s3 = QState()
        # self.s2.addTransition(self.btn3.clicked, self.s3)
        # self.s3.assignProperty(self.label, "text", "S3")
        # self.s3.entered.connect(self.enterState3)
        # self.s3.addTransition(self.s1h)
        # self.stateMachine.addState(self.s3)
        # 状态机初始状态
        # self.stateMachine.setInitialState(self.s1)
        # self.stateMachine.start()

    # Using Parallel States to Avoid a Combinatorial Explosion of States
        # self.s1 = QState(QState.ParallelStates)
        # # s11和s12是并行状态
        # self.s11 = QState(self.s1)
        # self.s12 = QState(self.s1)
        # self.stateMachine.addState(self.s1) ## 直接添加s1
        # # s11子状态
        # self.s11_move = QState(self.s11)
        # self.s11_notMove = QState(self.s11)
        # self.s11_move.assignProperty(self.label_carMove, 'text', 'Moving')
        # self.s11_notMove.assignProperty(self.label_carMove, 'text', 'Not Moving')
        # self.s11_notMove.addTransition(self.btn_started.clicked, self.s11_move)
        # self.s11_move.addTransition(self.btn_stopped.clicked, self.s11_notMove)
        # self.s11.setInitialState(self.s11_move)
        # # s12子状态
        # self.s12_dirty = QState(self.s12)
        # self.s12_clean = QState(self.s12)
        # self.s12_dirty.assignProperty(self.label_carAir, 'text', 'Dirty')
        # self.s12_clean.assignProperty(self.label_carAir, 'text', 'Cleaned')
        # self.s12_clean.addTransition(self.btn_soiled.clicked, self.s12_dirty)
        # self.s12_dirty.addTransition(self.btn_cleaned.clicked, self.s12_clean)
        # self.s12.setInitialState(self.s12_dirty)
        # # 状态机初始状态
        # self.stateMachine.setInitialState(self.s1) 
        # self.stateMachine.start()

    # Detecting that a Composite State has Finished
        # self.s4 = QState()
        # self.s4.entered.connect(self.s4Entered)
        
        # self.s5 = QFinalState(self.s4)
        # self.s4.setInitialState(self.s5)
        # self.s5.entered.connect(self.s4Finished)
        # self.stateMachine.addState(self.s4)

        # self.s6 = QState()
        # self.s6.entered.connect(self.s6Entered)
        # self.s6.finished.connect(self.s6Entered)
        # self.s4.addTransition(self.s4.finished, self.s6)
        # self.stateMachine.addState(self.s6)

        # self.stateMachine.setInitialState(self.s4)
        # self.stateMachine.start()

    # Targetless Transitions
        self.s6 = QState(self.stateMachine)
        self.s6.entered.connect(self.targetlessS6Entered)
        self.s6.entered.connect(self.targetlessS6Exited)
        self.signalTransition = QSignalTransition(self.btn3.clicked)
        self.signalTransition.triggered.connect(self.signalTransitionTriggered)
        self.s6.addTransition(self.signalTransition)
        # the target state were explicitly set to s6, s6 will be exited and re-entered each time
        # self.signalTransition.setTargetState(self.s6) 
        self.stateMachine.setInitialState(self.s6)
        self.stateMachine.start()

    def targetlessS6Entered(self):
        print('targetlessS6Entered')

    def targetlessS6Exited(self):
        print('targetlessS6Exited')

    def signalTransitionTriggered(self):
        QMessageBox.information(self, "State", "signalTransitionTriggered!", QMessageBox.Yes)

    def s4Entered(self):
        QMessageBox.information(self, "State", "s4 Entered!", QMessageBox.Yes)

    def s4Finished(self):
        QMessageBox.information(self, "State", "s4 Finished!", QMessageBox.Yes)

    def s6Entered(self):
        QMessageBox.information(self, "State", "s6 Entered!", QMessageBox.Yes)

    def s6Finished(self):
        QMessageBox.information(self, "State", "s6 Finished!", QMessageBox.Yes)

    def enterState3(self):
        self.label.setText("St")
        QMessageBox.information(self, "State", "s3 Entered!!", QMessageBox.Yes)

    def enterState1(self):
        self.label.setText("St")
        QMessageBox.information(self, "State", "s1 Entered!!", QMessageBox.Yes)

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
