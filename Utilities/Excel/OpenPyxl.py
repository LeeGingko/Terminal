# -*- coding: utf-8 -*-
from openpyxl import *
from openpyxl.styles import Alignment

class PrivateOpenPyxl():
    def __init__(self, filename = "", sheetname = ""):
        super(PrivateOpenPyxl, self).__init__()
        # 添加属性
        self.filename  = filename
        self.sheetname = sheetname
        self.workbook  = None
        self.worksheet = None
        self.alignment = Alignment(horizontal='fill', vertical='center', textRotation=0, wrapText=False, shrinkToFit=True)
        self.colindex = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

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

    def updateCodeRowData(self, code, dataList): # 根据编码去替换其对应所在行的数据
        maxrows = self.worksheet.max_row
        maxcols = self.worksheet.max_column
        gen = self.worksheet.iter_rows(2, maxrows, 1, maxcols) # 返回值为生成器
        for r in gen: # 迭代访问
            uid = r[6].value # 编号
            if code == uid:
                for i in range(15):
                    self.worksheet.cell(r[6].row, i+1, dataList[i])
                return True
        return False

    def setCellsStyle(self):
        maxrows = self.worksheet.max_row
        maxcols = self.worksheet.max_column
        for r in range(maxrows):
            for c in range(maxcols):
                col = self.colindex[c]
                pos = '{0}{1}'.format(col, r + 1)
                self.worksheet[pos].alignment = self.alignment
