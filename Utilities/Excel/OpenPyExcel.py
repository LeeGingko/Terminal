# -*- coding: utf-8 -*-
from openpyxl import *

class PersonalExcel():
    def __init__(self, filename="", sheetname="Sheet"):
        # super(PersonalExcel, self).__init__()
        self.filename = filename
        self.sheetname = sheetname

    def initWorkBook(self, filename):
        self.filename = filename
        self.workbook = Workbook(self.filename)
        # if self.sheetname == "":
        #     self.sheetname = "Sheet No1"
        # else:
        #     self.sheetname = "RecordedDataSheet1"
        self.workbook.save(self.filename)
        self.workbook.close()

    def setFileName(self, filename):
        self.filename = filename

    def getFileName(self):
        return self.filename

    def openFile(self):
        self.workbook = load_workbook(self.filename)

    def closeFile(self):
        self.workbook.close()

    def writeData(self, row, col, val):
        self.workbook["Sheet"].cell(row, col, val)

    def readData(self):
        self.openFile()
        print(self.workbook["Sheet"])
        print(self.sheetname)
        print(self.workbook["Sheet"].cell(1, 1).value)
        self.closeFile()



    def saveFile(self):
        self.workbook.save(self.filename)