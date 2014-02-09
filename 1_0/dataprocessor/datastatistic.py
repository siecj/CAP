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

    def stats_with_filter(self, datagroup, fidname, fidvalue):
        result = []
        keylist = datagroup.keys()
        sortedkeylist = sorted(keylist)
        for key in sortedkeylist:
            datalist = datagroup[key]
            counter = 0
            for x in datalist:
                if x[fidname] == fidvalue:
                    counter += 1
            result.append(counter)
            logging.debug(key)
        return result

    def stats_group_data(self, datagroup):
        result = []
        sortedkeylist = sorted(datagroup.keys())
        for key in sortedkeylist:
            result.append(len(datagroup[key]))
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
        # logging.debug(sorted(keylist))
        self.assertEqual(178, len(result))

    def test3(self):
        stat = DataStatistic()
        result1 = stat.group_source_by_datetime(self.dictlist, 'Created', '%Y-%m')
        result2 = stat.stats_with_filter(result1, 'CF-Region', 'EMEA')
        logging.debug(result2)

    def test4(self):
        stat = DataStatistic()
        result1 = stat.group_source_by_datetime(self.dictlist, 'Created', '%Y-%m')
        result2 = stat.stats_group_data(result1)
        logging.debug(result2)
        for x in range(len(result2)):
            print sum(result2[0:x+1]) 


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    unittest.main()
        
