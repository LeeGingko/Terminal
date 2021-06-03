# -*- coding: utf-8 -*-
from openpyxl import *

class PrivateOpenPyxl():
    def __init__(self, filename = "", sheetname = ""):
        super(PrivateOpenPyxl, self).__init__()
        # 添加属性
        self.filename  = filename
        self.sheetname = sheetname
        self.workbook  = None
        self.worksheet = None

    def initWorkBook(self, filename, sheetname):
        self.filename = filename
        self.sheetname = sheetname
        self.workbook = Workbook(filename) # 创建工作簿
        self.worksheet = self.workbook.create_sheet(self.sheetname, 0)
        self.worksheet.title = self.sheetname
        self.worksheet.sheet_properties.tabColor = "1072BA"
        self.workbook.save(self.filename)

    def closeSheet(self):
        self.workbook.close()

    def loadSheet(self, filename):
        self.filename = filename
        self.workbook = load_workbook(filename)
        self.worksheet = self.workbook.active # 默认工作表

    def writeData(self, filename, row, col, val):
        self.workbook = load_workbook(filename)
        self.worksheet = self.workbook.active # 默认工作表
        self.worksheet.cell(row, col, val)
        self.workbook.save(filename)
        self.workbook.close()

    def wrtieRow(self, rowList):
        self.worksheet.append(rowList)
        
    def saveSheet(self):
        self.workbook.save(self.filename)

    def updateCodeRowData(self, code, dataList): # 根据编码去找出其对应的位置，同时替换编码所在行的数据
        maxrows = self.worksheet.max_row
        maxcols = self.worksheet.max_column
        gen = self.worksheet.iter_rows(2, maxrows, 1, maxcols)
        for r in gen:
            uid = r[6].value
            if code == uid:
                for i in range(15):
                    self.worksheet.cell(r[6].row, i+1, dataList[i])
                return True
        return False
