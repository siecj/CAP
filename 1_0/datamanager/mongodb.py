import logging
import unittest
from pymongo import MongoClient

class MongoDBHelper():
    def __init__(self):
        self.client = MongoClient('localhost', 27017)  #defautl host and port
        self.db = self.client['cap']

    def save_rawdata(self, key, data):
        coll = self.db['rawdata']
        rawdata = {"key": key,
            "rawdata": data }
        coll.insert(rawdata)

    def get_rawdata(self, key):
        coll = self.db['rawdata']
        return coll.find({"key": key})

    def get_rawdata_with_filter(self, key, fieldname, fieldvalue):
        coll = self.db['rawdata']
        field = 'rawdata.' + fieldname
        return coll.find({"key": key, field: fieldvalue})

    def delete_all_rawdata(self, key):
        self.db.rawdata.remove({'key': key})

    def save_one(self, doc):
        coll = self.db['rawdata']
        coll.save(doc)

    def get_one_rawdata_by_order(self, key, fieldname, order):
        coll = self.db['rawdata']
        field = 'rawdata.' + fieldname
        return coll.find({"key": key}).sort(field, -1).limit(1)

class RawDataDBHelper():
    """docstring for RawDataDBHelper"""
    # def __init__(self, arg):
    #     super(RawDataDBHelper, self).__init__()
    #     self.arg = arg
    def save_rawdata(self, key, dic):
        coll = self.db['rawdata']
        rawdata = {"key": key, "rawdata": dic }
        coll.insert(rawdata)

    def search_all_by_key(self, key):
        coll = self.db['rawdata']
        cursor = coll.find({"key": key})
        result = []
        for item in cursor:
            result.append(item['rawdata'])
        return result

    def search_by_field(self, key, fieldname, fieldvalue):
        coll = self.db['rawdata']
        field = 'rawdata.' + fieldname
        cursor = coll.find({"key": key, field: fieldvalue})
        result = []
        for item in cursor:
            result.append(item['rawdata'])
        return result

    def search_one_with_order(self, key, fieldname, order):
        coll = self.db['rawdata']
        field = 'rawdata.' + fieldname
        return coll.find({"key": key}).sort(field, order).limit(1)['rawdata']

    def remove_by_key(self, key):
        self.db.rawdata.remove({'key': key}

    def save_document(self, doc):
        coll = self.db['rawdata']
        coll.save(doc)

class _UT(unittest.TestCase):
    """docstring for _UT"""

    def test1(self):
        logging.basicConfig(level="DEBUG")
        db = MongoDBHelper()
        cusor = db.get_one_rawdata_by_order('TicketsReport', 'id', -1)
        for data in cusor:
            logging.debug(data)

if __name__ == '__main__':
    logging.basicConfig(level="DEBUG")
    unittest.main()


