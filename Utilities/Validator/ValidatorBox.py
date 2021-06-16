# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIntValidator

class VLDR_DCT(QIntValidator):
    dctsig = pyqtSignal(str)

    def fixup(self, p_str):
        try:
            if float(p_str)  < 100:
                return '100'
            elif float(p_str) > 120:
                return '100'
        except:
            return '100'