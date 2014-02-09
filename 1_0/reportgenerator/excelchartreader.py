import logging
import unittest
import pythoncom
import win32com.client
from win32com.client import Dispatch

class ExcelChartReader():
    """docstring for ExcelChartReader"""
    def __init__(self, arg):
        self.filename = arg
        self.xlapp = Dispatch("Excel.Application")
        self.workbook = None
        try:
            self.workbook = self.xlapp.Workbooks.Open(self.filename)
            logging.debug('init Excel COM')
        except Exception as e:
            logging.warning(e)

    def __del__(self):
        if self.workbook != None:
            self.workbook.Close(SaveChanges=False)
            logging.info('Relase COM')

    def fill_data(self, sheetname, col, row, datalist):
        try:
            sheet = self.workbook.Worksheets(sheetname)
            for x in xrange(len(datalist)):
                sheet.Cells(row+x, col).Value = datalist[x]

        except Exception as e:
            logging.warning(e)

    def save_chart_to_file(self, sheetname, chartname, outputfile):
        try:
            sheet = self.workbook.Worksheets(sheetname)
            chartobjs = sheet.ChartObjects()
            for x in xrange(chartobjs.Count):
                chtobj = chartobjs.Item(x+1)
                if chtobj.Chart.ChartTitle.Text == chartname:
                    chtobj.Chart.Export(outputfile)
        except Exception as e:
            logging.warning(e)


class _UT(unittest.TestCase):
    """docstring for _UT"""
    def test1(self):
        filename = 'D:\\Temp\\all_hist_graph_template.xls'
        reader = ExcelChartReader(filename)
        logging.debug('insert data')
        reader.fill_data('data_month', 16, 3, range(1, 13))
        logging.debug('save chart to file')
        reader.save_chart_to_file('graph', 'Tickets Per Region', """D:\Temp\TicketsPerRegion.png""")

    def test2(self):
        filename = 'D:\\Temp\\demo.xlsx'
        reader = ExcelChartReader(filename)
        logging.debug('insert data')
        reader.fill_data('Sheet2', 2, 2, range(12, 0, -1))
        logging.debug('save chart to file')
        reader.save_chart_to_file('Sheet1', 'Demo', """D:\Temp\Demo.png""")


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    unittest.main()
        
        