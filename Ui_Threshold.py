# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\Learing\2021\719\Python\Terminal\Threshold.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_thresholdSettingDialog(object):
    def setupUi(self, thresholdSettingDialog):
        thresholdSettingDialog.setObjectName("thresholdSettingDialog")
        thresholdSettingDialog.resize(362, 426)
        self.groupBox = QtWidgets.QGroupBox(thresholdSettingDialog)
        self.groupBox.setGeometry(QtCore.QRect(6, 8, 347, 409))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.setObjectName("groupBox")
        self.pushBtn_saveSettingsRecord = QtWidgets.QPushButton(self.groupBox)
        self.pushBtn_saveSettingsRecord.setGeometry(QtCore.QRect(18, 354, 150, 40))
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(18)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.pushBtn_saveSettingsRecord.setFont(font)
        self.pushBtn_saveSettingsRecord.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushBtn_saveSettingsRecord.setObjectName("pushBtn_saveSettingsRecord")
        self.pushBtn_readSettingsRecord = QtWidgets.QPushButton(self.groupBox)
        self.pushBtn_readSettingsRecord.setGeometry(QtCore.QRect(172, 354, 150, 40))
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(18)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.pushBtn_readSettingsRecord.setFont(font)
        self.pushBtn_readSettingsRecord.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pushBtn_readSettingsRecord.setObjectName("pushBtn_readSettingsRecord")
        self.formLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.formLayoutWidget.setGeometry(QtCore.QRect(18, 84, 177, 265))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.lineEdit_setDrainCurrentTop = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setDrainCurrentTop.setFont(font)
        self.lineEdit_setDrainCurrentTop.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setDrainCurrentTop.setObjectName("lineEdit_setDrainCurrentTop")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setDrainCurrentTop)
        self.label_operator_29 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_29.setFont(font)
        self.label_operator_29.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_29.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_29.setObjectName("label_operator_29")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_operator_29)
        self.lineEdit_setWorkCurrentTop = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setWorkCurrentTop.setFont(font)
        self.lineEdit_setWorkCurrentTop.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setWorkCurrentTop.setObjectName("lineEdit_setWorkCurrentTop")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setWorkCurrentTop)
        self.label_operator_19 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_19.setFont(font)
        self.label_operator_19.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_19.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_19.setObjectName("label_operator_19")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_operator_19)
        self.lineEdit_setFireVoltageTop = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setFireVoltageTop.setFont(font)
        self.lineEdit_setFireVoltageTop.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setFireVoltageTop.setObjectName("lineEdit_setFireVoltageTop")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setFireVoltageTop)
        self.label_operator_45 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_45.setFont(font)
        self.label_operator_45.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_45.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_45.setObjectName("label_operator_45")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_operator_45)
        self.lineEdit_setFireCurrentTop = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setFireCurrentTop.setFont(font)
        self.lineEdit_setFireCurrentTop.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setFireCurrentTop.setObjectName("lineEdit_setFireCurrentTop")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setFireCurrentTop)
        self.label_operator_20 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_20.setFont(font)
        self.label_operator_20.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_20.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_20.setObjectName("label_operator_20")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_operator_20)
        self.lineEdit_setLineVoltageTop = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setLineVoltageTop.setFont(font)
        self.lineEdit_setLineVoltageTop.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setLineVoltageTop.setObjectName("lineEdit_setLineVoltageTop")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setLineVoltageTop)
        self.label_operator_55 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_55.setFont(font)
        self.label_operator_55.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_55.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_55.setObjectName("label_operator_55")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_operator_55)
        self.lineEdit_setLineCurrentTop = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setLineCurrentTop.setFont(font)
        self.lineEdit_setLineCurrentTop.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setLineCurrentTop.setObjectName("lineEdit_setLineCurrentTop")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setLineCurrentTop)
        self.label_operator_9 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_9.setFont(font)
        self.label_operator_9.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_9.setObjectName("label_operator_9")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_operator_9)
        self.lineEdit_setComVoltageTop = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setComVoltageTop.setFont(font)
        self.lineEdit_setComVoltageTop.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setComVoltageTop.setObjectName("lineEdit_setComVoltageTop")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setComVoltageTop)
        self.label_operator_49 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_49.setFont(font)
        self.label_operator_49.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_49.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_49.setObjectName("label_operator_49")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_operator_49)
        self.lineEdit_setComCurrentTop = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setComCurrentTop.setFont(font)
        self.lineEdit_setComCurrentTop.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setComCurrentTop.setObjectName("lineEdit_setComCurrentTop")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setComCurrentTop)
        self.label_operator_36 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_36.setFont(font)
        self.label_operator_36.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_36.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_36.setObjectName("label_operator_36")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_operator_36)
        self.label_operator_38 = QtWidgets.QLabel(self.groupBox)
        self.label_operator_38.setGeometry(QtCore.QRect(110, 50, 85, 27))
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_38.setFont(font)
        self.label_operator_38.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_38.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_38.setObjectName("label_operator_38")
        self.label_operator_39 = QtWidgets.QLabel(self.groupBox)
        self.label_operator_39.setGeometry(QtCore.QRect(198, 50, 81, 27))
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(20)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_39.setFont(font)
        self.label_operator_39.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_39.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_39.setObjectName("label_operator_39")
        self.formLayoutWidget_2 = QtWidgets.QWidget(self.groupBox)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(182, 84, 99, 265))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_operator_37 = QtWidgets.QLabel(self.formLayoutWidget_2)
        self.label_operator_37.setEnabled(False)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_37.setFont(font)
        self.label_operator_37.setText("")
        self.label_operator_37.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_37.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_37.setObjectName("label_operator_37")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_operator_37)
        self.lineEdit_setDrainCurrentBottom = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setDrainCurrentBottom.setFont(font)
        self.lineEdit_setDrainCurrentBottom.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setDrainCurrentBottom.setObjectName("lineEdit_setDrainCurrentBottom")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setDrainCurrentBottom)
        self.label_operator_30 = QtWidgets.QLabel(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_30.setFont(font)
        self.label_operator_30.setText("")
        self.label_operator_30.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_30.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_30.setObjectName("label_operator_30")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_operator_30)
        self.lineEdit_setWorkCurrentBottom = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setWorkCurrentBottom.setFont(font)
        self.lineEdit_setWorkCurrentBottom.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setWorkCurrentBottom.setObjectName("lineEdit_setWorkCurrentBottom")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setWorkCurrentBottom)
        self.label_operator_46 = QtWidgets.QLabel(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_46.setFont(font)
        self.label_operator_46.setText("")
        self.label_operator_46.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_46.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_46.setObjectName("label_operator_46")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_operator_46)
        self.lineEdit_setFireVoltageBottom = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setFireVoltageBottom.setFont(font)
        self.lineEdit_setFireVoltageBottom.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setFireVoltageBottom.setObjectName("lineEdit_setFireVoltageBottom")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setFireVoltageBottom)
        self.label_operator_21 = QtWidgets.QLabel(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_21.setFont(font)
        self.label_operator_21.setText("")
        self.label_operator_21.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_21.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_21.setObjectName("label_operator_21")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_operator_21)
        self.lineEdit_setFireCurrentBottom = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setFireCurrentBottom.setFont(font)
        self.lineEdit_setFireCurrentBottom.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setFireCurrentBottom.setObjectName("lineEdit_setFireCurrentBottom")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setFireCurrentBottom)
        self.label_operator_47 = QtWidgets.QLabel(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_47.setFont(font)
        self.label_operator_47.setText("")
        self.label_operator_47.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_47.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_47.setObjectName("label_operator_47")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_operator_47)
        self.lineEdit_setLineVoltageBottom = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setLineVoltageBottom.setFont(font)
        self.lineEdit_setLineVoltageBottom.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setLineVoltageBottom.setObjectName("lineEdit_setLineVoltageBottom")
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setLineVoltageBottom)
        self.label_operator_22 = QtWidgets.QLabel(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_22.setFont(font)
        self.label_operator_22.setText("")
        self.label_operator_22.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_22.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_22.setObjectName("label_operator_22")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_operator_22)
        self.lineEdit_setLineCurrentBottom = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setLineCurrentBottom.setFont(font)
        self.lineEdit_setLineCurrentBottom.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setLineCurrentBottom.setObjectName("lineEdit_setLineCurrentBottom")
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setLineCurrentBottom)
        self.label_operator_56 = QtWidgets.QLabel(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_56.setFont(font)
        self.label_operator_56.setText("")
        self.label_operator_56.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_56.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_56.setObjectName("label_operator_56")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_operator_56)
        self.lineEdit_setComVoltageBottom = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setComVoltageBottom.setFont(font)
        self.lineEdit_setComVoltageBottom.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setComVoltageBottom.setObjectName("lineEdit_setComVoltageBottom")
        self.formLayout_2.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setComVoltageBottom)
        self.label_operator_10 = QtWidgets.QLabel(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_10.setFont(font)
        self.label_operator_10.setText("")
        self.label_operator_10.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_10.setObjectName("label_operator_10")
        self.formLayout_2.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_operator_10)
        self.lineEdit_setComCurrentBottom = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.lineEdit_setComCurrentBottom.setFont(font)
        self.lineEdit_setComCurrentBottom.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_setComCurrentBottom.setObjectName("lineEdit_setComCurrentBottom")
        self.formLayout_2.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.lineEdit_setComCurrentBottom)
        self.formLayoutWidget_3 = QtWidgets.QWidget(self.groupBox)
        self.formLayoutWidget_3.setGeometry(QtCore.QRect(284, 84, 37, 265))
        self.formLayoutWidget_3.setObjectName("formLayoutWidget_3")
        self.formLayout_3 = QtWidgets.QFormLayout(self.formLayoutWidget_3)
        self.formLayout_3.setContentsMargins(0, 0, 0, 0)
        self.formLayout_3.setObjectName("formLayout_3")
        self.label_operator_41 = QtWidgets.QLabel(self.formLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_41.setFont(font)
        self.label_operator_41.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_41.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_41.setObjectName("label_operator_41")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.label_operator_41)
        self.label_operator_42 = QtWidgets.QLabel(self.formLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_42.setFont(font)
        self.label_operator_42.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_42.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_42.setObjectName("label_operator_42")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.label_operator_42)
        self.label_operator_51 = QtWidgets.QLabel(self.formLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_51.setFont(font)
        self.label_operator_51.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_51.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_51.setObjectName("label_operator_51")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.label_operator_51)
        self.label_operator_44 = QtWidgets.QLabel(self.formLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_44.setFont(font)
        self.label_operator_44.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_44.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_44.setObjectName("label_operator_44")
        self.formLayout_3.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.label_operator_44)
        self.label_operator_52 = QtWidgets.QLabel(self.formLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_52.setFont(font)
        self.label_operator_52.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_52.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_52.setObjectName("label_operator_52")
        self.formLayout_3.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.label_operator_52)
        self.label_operator_43 = QtWidgets.QLabel(self.formLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_43.setFont(font)
        self.label_operator_43.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_43.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_43.setObjectName("label_operator_43")
        self.formLayout_3.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.label_operator_43)
        self.label_operator_53 = QtWidgets.QLabel(self.formLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_53.setFont(font)
        self.label_operator_53.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_53.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_53.setObjectName("label_operator_53")
        self.formLayout_3.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.label_operator_53)
        self.label_operator_35 = QtWidgets.QLabel(self.formLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("幼圆")
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.label_operator_35.setFont(font)
        self.label_operator_35.setTextFormat(QtCore.Qt.AutoText)
        self.label_operator_35.setAlignment(QtCore.Qt.AlignCenter)
        self.label_operator_35.setObjectName("label_operator_35")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.label_operator_35)

        self.retranslateUi(thresholdSettingDialog)
        QtCore.QMetaObject.connectSlotsByName(thresholdSettingDialog)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setDrainCurrentTop, self.lineEdit_setDrainCurrentBottom)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setDrainCurrentBottom, self.lineEdit_setWorkCurrentTop)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setWorkCurrentTop, self.lineEdit_setWorkCurrentBottom)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setWorkCurrentBottom, self.lineEdit_setFireVoltageTop)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setFireVoltageTop, self.lineEdit_setFireVoltageBottom)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setFireVoltageBottom, self.lineEdit_setFireCurrentTop)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setFireCurrentTop, self.lineEdit_setFireCurrentBottom)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setFireCurrentBottom, self.lineEdit_setLineVoltageTop)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setLineVoltageTop, self.lineEdit_setLineVoltageBottom)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setLineVoltageBottom, self.lineEdit_setLineCurrentTop)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setLineCurrentTop, self.lineEdit_setLineCurrentBottom)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setLineCurrentBottom, self.lineEdit_setComVoltageTop)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setComVoltageTop, self.lineEdit_setComVoltageBottom)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setComVoltageBottom, self.lineEdit_setComCurrentTop)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setComCurrentTop, self.lineEdit_setComCurrentBottom)
        thresholdSettingDialog.setTabOrder(self.lineEdit_setComCurrentBottom, self.pushBtn_saveSettingsRecord)
        thresholdSettingDialog.setTabOrder(self.pushBtn_saveSettingsRecord, self.pushBtn_readSettingsRecord)

    def retranslateUi(self, thresholdSettingDialog):
        _translate = QtCore.QCoreApplication.translate
        thresholdSettingDialog.setWindowTitle(_translate("thresholdSettingDialog", "Dialog"))
        self.groupBox.setTitle(_translate("thresholdSettingDialog", "设备阈值设定"))
        self.pushBtn_saveSettingsRecord.setText(_translate("thresholdSettingDialog", "保存参数"))
        self.pushBtn_saveSettingsRecord.setShortcut(_translate("thresholdSettingDialog", "Ctrl+8"))
        self.pushBtn_readSettingsRecord.setText(_translate("thresholdSettingDialog", "读取参数"))
        self.pushBtn_readSettingsRecord.setShortcut(_translate("thresholdSettingDialog", "Ctrl+9"))
        self.lineEdit_setDrainCurrentTop.setText(_translate("thresholdSettingDialog", "100.0"))
        self.label_operator_29.setText(_translate("thresholdSettingDialog", "工作电流"))
        self.lineEdit_setWorkCurrentTop.setText(_translate("thresholdSettingDialog", "2000.0"))
        self.label_operator_19.setText(_translate("thresholdSettingDialog", "起爆电压"))
        self.lineEdit_setFireVoltageTop.setText(_translate("thresholdSettingDialog", "74.0"))
        self.label_operator_45.setText(_translate("thresholdSettingDialog", "起爆电流"))
        self.lineEdit_setFireCurrentTop.setText(_translate("thresholdSettingDialog", "10.0"))
        self.label_operator_20.setText(_translate("thresholdSettingDialog", "线路电压"))
        self.lineEdit_setLineVoltageTop.setText(_translate("thresholdSettingDialog", "26.0"))
        self.label_operator_55.setText(_translate("thresholdSettingDialog", "线路电流"))
        self.lineEdit_setLineCurrentTop.setText(_translate("thresholdSettingDialog", "10.0"))
        self.label_operator_9.setText(_translate("thresholdSettingDialog", "通信电压"))
        self.lineEdit_setComVoltageTop.setText(_translate("thresholdSettingDialog", "38.0"))
        self.label_operator_49.setText(_translate("thresholdSettingDialog", "通信电流"))
        self.lineEdit_setComCurrentTop.setText(_translate("thresholdSettingDialog", "10.0"))
        self.label_operator_36.setText(_translate("thresholdSettingDialog", "漏电流"))
        self.label_operator_38.setText(_translate("thresholdSettingDialog", "上限"))
        self.label_operator_39.setText(_translate("thresholdSettingDialog", "下限"))
        self.lineEdit_setDrainCurrentBottom.setText(_translate("thresholdSettingDialog", "50.0"))
        self.lineEdit_setWorkCurrentBottom.setText(_translate("thresholdSettingDialog", "500.0"))
        self.lineEdit_setFireVoltageBottom.setText(_translate("thresholdSettingDialog", "70.0"))
        self.lineEdit_setFireCurrentBottom.setText(_translate("thresholdSettingDialog", "0.0"))
        self.lineEdit_setLineVoltageBottom.setText(_translate("thresholdSettingDialog", "21.0"))
        self.lineEdit_setLineCurrentBottom.setText(_translate("thresholdSettingDialog", "8.0"))
        self.lineEdit_setComVoltageBottom.setText(_translate("thresholdSettingDialog", "32.0"))
        self.lineEdit_setComCurrentBottom.setText(_translate("thresholdSettingDialog", "8.0"))
        self.label_operator_41.setText(_translate("thresholdSettingDialog", "uA"))
        self.label_operator_42.setText(_translate("thresholdSettingDialog", "V"))
        self.label_operator_51.setText(_translate("thresholdSettingDialog", "mA"))
        self.label_operator_44.setText(_translate("thresholdSettingDialog", "V"))
        self.label_operator_52.setText(_translate("thresholdSettingDialog", "mA"))
        self.label_operator_43.setText(_translate("thresholdSettingDialog", "V"))
        self.label_operator_53.setText(_translate("thresholdSettingDialog", "mA"))
        self.label_operator_35.setText(_translate("thresholdSettingDialog", "uA"))
