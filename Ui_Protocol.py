# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\Learing\2021\719\Python\Terminal\Protocol.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_protocolDialog(object):
    def setupUi(self, protocolDialog):
        protocolDialog.setObjectName("protocolDialog")
        protocolDialog.resize(304, 163)
        self.groupBox = QtWidgets.QGroupBox(protocolDialog)
        self.groupBox.setGeometry(QtCore.QRect(8, 14, 281, 125))
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.groupBox.setFont(font)
        self.groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.setObjectName("groupBox")
        self.comboBox_selectComNum = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_selectComNum.setGeometry(QtCore.QRect(8, 30, 269, 40))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_selectComNum.sizePolicy().hasHeightForWidth())
        self.comboBox_selectComNum.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.comboBox_selectComNum.setFont(font)
        self.comboBox_selectComNum.setCurrentText("")
        self.comboBox_selectComNum.setObjectName("comboBox_selectComNum")
        self.pushBtn_serialSwitch = QtWidgets.QPushButton(self.groupBox)
        self.pushBtn_serialSwitch.setGeometry(QtCore.QRect(8, 78, 271, 40))
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.pushBtn_serialSwitch.setFont(font)
        self.pushBtn_serialSwitch.setAutoFillBackground(True)
        self.pushBtn_serialSwitch.setStyleSheet("QPushButton{\n"
"    \n"
"}")
        self.pushBtn_serialSwitch.setObjectName("pushBtn_serialSwitch")

        self.retranslateUi(protocolDialog)
        QtCore.QMetaObject.connectSlotsByName(protocolDialog)

    def retranslateUi(self, protocolDialog):
        _translate = QtCore.QCoreApplication.translate
        protocolDialog.setWindowTitle(_translate("protocolDialog", "Dialog"))
        self.groupBox.setTitle(_translate("protocolDialog", "端口设置"))
        self.pushBtn_serialSwitch.setText(_translate("protocolDialog", "打开串口"))
        self.pushBtn_serialSwitch.setShortcut(_translate("protocolDialog", "Ctrl+1"))
