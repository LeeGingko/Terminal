# -*- coding: utf-8 -*-
# getset全局变量
import GetSetObj
# openpyxl相关模块
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Color, Font, NamedStyle
from openpyxl.styles.fills import PatternFill # 填充

class PrivateOpenPyxl():
    #*------------------------------------------------命名样式------------------------------------------------*#
    #*---------------------------------------------Named Styles----------------------------------------------*#
    # 检测结果通过
    resultPassStyle = NamedStyle('resultPassStyle')
    resultPassStyle.font = Font(name='Times New Roman', size=16, bold=False, color=Color(indexed=0))# 黑色字体
    resultPassStyle.alignment = Alignment(horizontal='center', vertical='center')
    resultPassStyle.fill = PatternFill('solid', '0000CCFF') # 蓝色填充背景
    # 检测结果失败
    resultFailStyle = NamedStyle('resultFailStyle')
    resultFailStyle.font = Font(name='Times New Roman', size=16, bold=False, color=Color(indexed=0))# 黑色字体
    resultFailStyle.alignment = Alignment(horizontal='center', vertical='center')
    resultFailStyle.fill = PatternFill('solid', '00FF0000') # 红色填充背景
    # 默认字体
    defaultContentStyle = NamedStyle('defaultContentStyle')
    defaultContentStyle.font = Font(name='Times New Roman', size=16, bold=False, color=Color(indexed=0))# 黑色字体
    defaultContentStyle.alignment = Alignment(horizontal='center', vertical='center')
    # 正常数值或结果
    normalContentStyle = NamedStyle('normalContentStyle')
    normalContentStyle.font = Font(name='Times New Roman', size=16, bold=False, color=Color(indexed=4))# 蓝色字体
    normalContentStyle.alignment = Alignment(horizontal='center', vertical='center')
    # 异常数值或结果
    abnormalContentStyle = NamedStyle('abnormalContentStyle')
    abnormalContentStyle.font = Font(name='Times New Roman', size=16, bold=False, color=Color(indexed=2)) # 红色字体
    abnormalContentStyle.alignment = Alignment(horizontal='center', vertical='center')
    
    def __init__(self, wbname = "", wsname = ""):
        super(PrivateOpenPyxl, self).__init__()
        # 添加属性
        self.wbname  = wbname   # 工作簿名
        self.wsname = wsname    # 工作表名
        self.wb  = None         # 工作簿对象
        self.ws = None          # 工作簿对象
        #*------------------------------------------------一般样式------------------------------------------------*#
        #*----------------------------------------------Cell Styles----------------------------------------------*#
        # 表头单元格格式
        self.hfont = Font(name='Times New Roman', size=16, bold=False, color=Color(indexed=17))
        self.halignment = Alignment(horizontal='center', vertical='center', textRotation=0, wrapText=False)
        # 默认列宽 对应字体如上
        self.columnWidth = [12, 30, 14.38, 17.25, 9, 11.88, 11.88, 12.13, 10, 11.88, 11.88, 12.13, 10, 11.88, 6.38]
        # 26列列索引
        self.colindex = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        

    def initWorkBook(self, wbname, wsname):
        # 创建工作簿工作表
        self.wbname = wbname
        self.wsname = wsname
        self.wb = Workbook(wbname) # 创建工作簿
        self.ws = self.wb.create_sheet(self.wsname, 0)
        self.ws.title = self.wsname
        self.ws.sheet_properties.tabColor = "1072BA"
        # 添加命名样式
        self.wb.add_named_style(self.resultPassStyle)
        self.wb.add_named_style(self.resultFailStyle)
        self.wb.add_named_style(self.defaultContentStyle)
        self.wb.add_named_style(self.normalContentStyle)
        self.wb.add_named_style(self.abnormalContentStyle)
        self.wb.save(self.wbname)

    def closeSheet(self):
        self.wb.close()

    def loadSheet(self, wbname):
        self.wbname = wbname
        self.wb = load_workbook(wbname)
        self.ws = self.wb.active # 默认工作表

    # def writeData(self, wbname, row, col, val):
    #     self.wb = load_workbook(wbname)
    #     self.ws = self.wb.active # 默认工作表
    #     self.ws.cell(row, col, val)
    #     self.wb.save(wbname)

    # def wrtieRow(self, rowList):
    #     self.ws.append(rowList)
        
    def saveSheet(self):
        self.wb.save(self.wbname)

    def setHeaderStyle(self, tableHeadline):
        self.loadSheet(self.wbname)
        for c in range(15):
            column = self.colindex[c]
            pos = '{0}{1}'.format(column, 1)
            self.ws[pos] = tableHeadline[c]
            self.ws[pos].alignment = self.halignment
            self.ws[pos].font = self.hfont
            self.ws.column_dimensions[column].width = self.columnWidth[c]
        self.saveSheet()
        self.closeSheet()
    
    def cellResultFillingStyleSetting(self, row, dataList):
        thresholdInstance = GetSetObj.get(2) # 获取阈值界面对象实例
        for col in range(15):
            pos = '{0}{1}'.format(self.colindex[col], row) # 表格索引 
            self.ws[pos] = dataList[col]
            if col == 2: # 漏电流
                if dataList[col] != '-' and float(dataList[col]) > float(thresholdInstance.paraDict['th_DrainCurrent_Up']):
                    self.ws[pos].style = 'abnormalContentStyle'
                elif dataList[col] != '-' and float(dataList[col]) <= float(thresholdInstance.paraDict['th_DrainCurrent_Up']):
                    self.ws[pos].style = 'normalContentStyle'
                elif dataList[col] == '-':
                    self.ws[pos].style = 'defaultContentStyle'
            elif col == 3: # 工作电流
                if dataList[col] != '-' and float(dataList[col]) > float(thresholdInstance.paraDict['th_WorkCurrent_Up']):
                    self.ws[pos].style = 'abnormalContentStyle'
                elif dataList[col] != '-' and float(dataList[col]) <= float(thresholdInstance.paraDict['th_WorkCurrent_Up']):
                    self.ws[pos].style = 'normalContentStyle'
                elif dataList[col] == '-':
                    self.ws[pos].style = 'defaultContentStyle'
            elif col == 4: # ID核对
                if dataList[col] != '-' and dataList[col] == '失败':
                    self.ws[pos].style = 'abnormalContentStyle'
                elif dataList[col] != '-' and dataList[col] == '成功':
                    self.ws[pos].style = 'normalContentStyle'
                elif dataList[col] == '-':
                    self.ws[pos].style = 'defaultContentStyle'
            elif col == 5: # 在线检测
                if dataList[col] != '-' and dataList[col] == '离线':
                    self.ws[pos].style = 'abnormalContentStyle'
                elif dataList[col] != '-' and dataList[col] == '在线':
                    self.ws[pos].style = 'normalContentStyle'
                elif dataList[col] == '-':
                    self.ws[pos].style = 'defaultContentStyle'
            elif col == 7: # 被测模块引爆电流
                if dataList[col] != '-' and float(dataList[col]) > float(thresholdInstance.paraDict['th_FireCurrent_Up']):
                    self.ws[pos].style = 'abnormalContentStyle'
                elif dataList[col] != '-' and float(dataList[col]) <= float(thresholdInstance.paraDict['th_FireCurrent_Up']):
                    self.ws[pos].style = 'normalContentStyle'
                elif dataList[col] == '-':
                    self.ws[pos].style = 'defaultContentStyle'
            elif col == 9: # 被测模块引爆电流判断
                if dataList[col] != '-' and dataList[col] == '超限':
                    self.ws[pos].style = 'abnormalContentStyle'
                elif dataList[col] != '-' and dataList[col] == '正常':
                    self.ws[pos].style = 'normalContentStyle'
                elif dataList[col] == '-':
                    self.ws[pos].style = 'defaultContentStyle'
            elif col == 11: # 内置模块引爆电流
                if dataList[col] != '-' and float(dataList[col]) > float(thresholdInstance.paraDict['th_FireCurrent_Up']):
                    self.ws[pos].style = 'abnormalContentStyle'
                elif dataList[col] != '-' and float(dataList[col]) <= float(thresholdInstance.paraDict['th_FireCurrent_Up']):
                    self.ws[pos].style = 'normalContentStyle'
                elif dataList[col] == '-':
                    self.ws[pos].style = 'defaultContentStyle'
            elif col == 13: # 内置模块引爆电流判断
                if dataList[col] != '-' and dataList[col] == '超限':
                    self.ws[pos].style = 'abnormalContentStyle'
                elif dataList[col] != '-' and dataList[col] == '正常':
                    self.ws[pos].style = 'normalContentStyle'
                elif dataList[col] == '-':
                    self.ws[pos].style = 'defaultContentStyle'
            elif col == 14: # 结论
                if dataList[col] != '-' and dataList[col] == '失败':
                    self.ws[pos].style = 'resultFailStyle'
                elif dataList[col] != '-' and dataList[col] == '通过':
                    self.ws[pos].style = 'resultPassStyle'
            else:
                self.ws[pos].style = 'defaultContentStyle'

    def updateCodeRowData(self, code, dataList): # 根据输入UID编码去替换其对应所在行的数据
        maxrows = self.ws.max_row # 每次执行行数据填入都获取最新的最大行（包括表头所在行）
        maxcols = self.ws.max_column
        nonDupCnt = 0;
        if maxrows >= 2: # 已填入了表头，且填入了数据
            gen = self.ws.iter_rows(2, maxrows, 1, maxcols) # 返回值生成器
            for rowdata in gen: # 迭代访问，判断并更新重复检测结果
                uid = rowdata[6].value # 第六列：UID编码
                if uid == code: # 重复检测结果
                    self.cellResultFillingStyleSetting(rowdata[6].row, dataList)
                    break
                else:
                    nonDupCnt = nonDupCnt + 1
                    continue
            if nonDupCnt == maxrows - 1: # 没有重复结果则新添加一行即可
                self.cellResultFillingStyleSetting(maxrows + 1, dataList)
        else: # 只填入了表头，还未填入有数据
            self.cellResultFillingStyleSetting(2, dataList)