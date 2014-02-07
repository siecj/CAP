import logging
import unittest
import pythoncom
import win32com.client
from win32com.client import Dispatch

class ExcelChartReader():
    """docstring for ExcelChartReader"""
    def __init__(self, arg):
        self.filename = arg

    def setup(self):
        self.xlapp = Dispatch("Excel.Application")
        try:
            self.workbook = self.xlapp.Workbooks.Open(self.filename)
        except Exception as e:
            logging.warning(e)

    def teardown(self):
        if self.workbook != None:
            self.workbook.Close(SaveChanges=False)

    def fill_data(self, sheetname, col, row, datalist):
        try:
            sheet = self.workbook.Worksheets(sheetname)
            for x in xrange(len(datalist)):
                sheet.Cells(row+x, col).Value = datalist[x]

        except Exception as e:
            logging.warning(e)

    def read_chart(self, sheetname, chartname):
        try:
            sheet = self.workbook.Worksheets(sheetname)
            chartobjs = sheet.ChartObjects()
            for x in xrange(chartobjs.Count):
                chtobj = chartobjs.Item(x+1)
                if chtobj.Chart.ChartTitle.Text == chartname:
                    chtobj.Chart.Export('D:\\Temp\\' + chartname + '.png')
        except Exception as e:
            logging.warning(e)


class _UT(unittest.TestCase):
    """docstring for _UT"""
    def test1(self):
        filename = 'D:\\Temp\\all_hist_graph_template.xls'
        reader = ExcelChartReader(filename)
        reader.setup()
        logging.debug('insert data')
        reader.fill_data('data_month', 16, 3, range(1, 13))
        logging.debug('save chart to file')
        reader.read_chart('graph', 'Tickets Per Region')
        logging.debug('teardown')
        reader.teardown()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    unittest.main()
        
        