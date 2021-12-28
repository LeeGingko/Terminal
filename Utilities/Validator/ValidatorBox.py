# -*- coding: utf-8 -*-
from PyQt5.QtGui import QValidator

class VLDR_INTFOLAT(QValidator):
    def __init__(self, up, down):
        super(VLDR_INTFOLAT, self).__init__()
        self.up = up
        self.down = down

    def validate(self, input_str, pos_type):
        try:
            if float(input_str) <= self.up and float(input_str)  >= self.down:      
                return(QValidator.Acceptable,input_str,pos_type)
            elif float(input_str) > self.up or float(input_str)  < self.down:
                return(QValidator.Intermediate,input_str,pos_type)
            else:
                return(QValidator.Invalid,input_str,pos_type)
        except:
            if len(input_str) == 0:
                return(QValidator.Intermediate,input_str,pos_type)
            return(QValidator.Invalid,input_str,pos_type)

    def fixup(self, p_str):
        try:
            if float(p_str)  < self.down:
                return str(self.down)
            elif float(p_str) > self.up:
                return str(self.up)
        except:
            return str(self.down)