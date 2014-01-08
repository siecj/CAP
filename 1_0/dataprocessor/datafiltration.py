import csv
import logging
import unittest
import re
from datetime import datetime

class DataFiltration():
    """docstring for DataFiltration"""

    def filter(self, diclist, fidname, fidvalue, comparison, outputfidlist=[]):
        result = self.filter_by_fid(diclist, fidname, fidvalue, comparison)
        result = self.filter_output(result, outputfidlist)

        return result

    def filter_by_fid(self, diclist, name, value, comparison):
        """"docstring for filter_by_fid

        return: list of dictionary
        comparison symbol define: GT, LT, EQ
        """
        if comparison == 'GT':
            result = [item for item in diclist if item[name] > value]
        elif comparison == 'LT':
            result = [item for item in diclist if item[name] < value]
        elif comparison == 'EQ':
            result = [item for item in diclist if item[name] == value]
        else:
            result = []
        return result

    def filter_output(self, diclist, outputfidlist=[]):
        if len(outputfidlist) == 0:
            return diclist

        result = []
        for item in diclist:
            dic = {}
            for fid in outputfidlist:
                dic[fid] = item[fid]
            result.append(dic)
        return result

    def filter_by_regex(self, dictlist, fieldname, regex, outputfidlist=[]):
        result = [item for item in dictlist if re.match(regex, item[fieldname]) != None]
        return self.filter_output(result, outputfidlist)

class _UT(unittest.TestCase):
    """docstring for _UT"""
    def setUp(self):
        logging.basicConfig(level="DEBUG")
        self.listofdic = []

        filename = 'tickets_before_3299.csv'
        f = open(filename, 'r')
        dictreader = csv.DictReader(f, dialect='excel-tab')
        for row in dictreader:
            row['Priority'] = int(row['Priority'])
            row['id'] = int(row['id'])
            if row['Resolved'] != "":
                row['Resolved'] = datetime.strptime(row['Resolved'], '%Y-%m-%d %H:%M:%S')
            row['Created'] = datetime.strptime(row['Created'], '%Y-%m-%d %H:%M:%S')
            row['LastUpdated'] = datetime.strptime(row['LastUpdated'], '%Y-%m-%d %H:%M:%S')
            self.listofdic.append(row)
        f.close()

   
    def test1(self):
        filtration = DataFiltration()
        resultlist = filtration.filter_by_fid(self.listofdic, 'id', 3297, 'GT')
        logging.debug(resultlist)
        self.assertEqual(len(resultlist), 2)
        self.assertEqual(resultlist[0]['id'], 3298)

        tmpdate = datetime(2013, 10, 17)
        res = filtration.filter_by_fid(self.listofdic, 'Created', tmpdate, 'GT')
        self.assertEqual(len(res), 11)

        res = filtration.filter_by_fid(self.listofdic, 'id', 3067, 'EQ')
        self.assertEqual(res[0]['Subject'], '[Legacy:RAQ] TSS on ZRR60B (migrated from 7B) is Standby')

        res = filtration.filter_by_fid(self.listofdic, 'id', 2100, 'LT')
        self.assertEqual(len(res), 2077)

    def test2(self):
        filtration = DataFiltration()

        tmpdate = datetime(2013, 10, 17)
        res = filtration.filter_by_fid(self.listofdic, 'Created', tmpdate, 'GT')
        self.assertEqual(len(res), 11)

        res = filtration.filter_output(res, ['id', 'Subject', 'Owner', 'Status', 'Created', 'Resolved'])
        self.assertEqual(len(res[0]), 6);

    def test3(self):
        filtration = DataFiltration()

        res = filtration.filter_by_fid(self.listofdic, 'Status', 'open', 'EQ')
        res1 = filtration.filter_by_regex(self.listofdic, 'Status', '^op')
        self.assertEqual(len(res1), len(res))


if __name__ == '__main__':
    logging.basicConfig(level="DEBUG")
    unittest.main()