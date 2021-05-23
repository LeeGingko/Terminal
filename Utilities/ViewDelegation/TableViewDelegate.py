# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QStyle, QStyledItemDelegate, QStyleOptionButton)

class PrivateTableViewDelegate(QStyledItemDelegate):
    def __init__(self):
        super(PrivateTableViewDelegate, self).__init__()
    
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        # if index.row() == 0 and index.column() == 0:
        #     check_style = QStyleOptionButton()
        #     check_style.rect = option.rect
        #     check_style.state = QStyle.State_Enabled | QStyle.State_Off
        #     QApplication.style().drawControl(QStyle.CE_CheckBox, check_style, painter)
        
        return super(PrivateTableViewDelegate, self).paint(painter, option, index)
 
    # def editorEvent(self, event, model, option, index):
    #     # if index.row() == 0 and index.column() == 0:
    #     #     if event.type() == event.MouseButtonPress:
    #     #         print("if event.type() == event.MouseButtonPress")
    #     pass
 
    # def createEditor(self, parent, option, index):
    #     pass
    
    def updateEditorGeometry(self, editor, option, index):
        pass
 
    def setEditorData(self, editor, index):
        pass
 
    def setModelData(self, editor, model, index):
        pass
