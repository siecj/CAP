import logging
import unittest
import csv
from datetime import *

class DataStatistic():
    """docstring for DataStatistic"""

    def group_source_by_month(self, dictlist, fidname):
        """ group source dictionary list by month

        dictlist: source dictionary list
        fidname: fid in date type, used to group
        return: a list of dictionary list
        """
        result = {}
        for item in dictlist:
            monthstr = item[fidname].strftime('%Y-%m')
            if result.has_key(monthstr):
                result[monthstr].append(item)
            else:
                result[monthstr] = [item]

        return result

    def group_source_by_week(self, dictlist, fidname):
        result = {}
        for item in dictlist:
            monthstr = item[fidname].strftime('%Y-%U')
            if result.has_key(monthstr):
                result[monthstr].append(item)
            else:
                result[monthstr] = [item]

        return result

    def group_source_by_datetime(self, dictlist, fidname, dateformat):
        result = {}
        for item in dictlist:
            monthstr = item[fidname].strftime(dateformat)
            if result.has_key(monthstr):
                result[monthstr].append(item)
            else:
                result[monthstr] = [item]

        return result

class _UT(unittest.TestCase):
    """docstring for _UT"""

    def setUp(self):
        self.dictlist = []
        f = open('temp\\ticktes_before_3299.csv', 'r')
        reader = csv.DictReader(f, dialect='excel-tab')
        for row in reader:
            row['Created'] = datetime.strptime(row['Created'], '%Y-%m-%d %H:%M:%S')
            self.dictlist.append(row)
        f.close()
        logging.debug('Load dictionary list finish. Total {0} dictionarys'.format(len(self.dictlist)))

    def test1(self):
        stat = DataStatistic()
        result = stat.group_source_by_month(self.dictlist, 'Created')
        keylist = result.keys()
        logging.debug(sorted(keylist))
        self.assertEqual(42, len(result))

    def test2(self):
        stat = DataStatistic()
        result = stat.group_source_by_datetime(self.dictlist, 'Created', '%Y-%U')
        keylist = result.keys()
        logging.debug(sorted(keylist))
        self.assertEqual(178, len(result))


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    unittest.main()
        
