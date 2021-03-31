# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QStyledItemDelegate

class TableViewDelegate(QStyledItemDelegate):
    def __init__(self):
        super(TableViewDelegate, self).__init__()
    
    def paint(self, painter, option, index):
        font = QFont("Monospaced", 16, 10, False)
        option.displayAlignment = Qt.AlignCenter
        painter.setFont(font)
        return super(TableViewDelegate, self).paint(painter, option, index)
 
    # def editorEvent(self, event, model, option, index):
    #     pass
 
    def createEditor(self, parent, option, index):
        pass
    
    def updateEditorGeometry(self, editor, option, index):
        pass
 
    # def setEditorData(self, editor, index):
    #     pass
 
    def setModelData(self, editor, model, index):
        pass