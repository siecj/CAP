# -*- coding: utf-8 -*-

import csv
from datetime import *
import logging
import unittest
import urllib, urllib2, cookielib
import socket
import StringIO
socket.setdefaulttimeout(120)
# import time
from ConfigParser import ConfigParser

from datamanager.mongodb import *

g_rt_username = 'jiu.chen'
g_rt_password = 'password'

class TicketCollector():
    """docstring for ClassName"""
    def __init__(self):
        self.cp = ConfigParser()
        self.cp.read("rawdata.conf")

    def login(self):
        cookiejar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        l_login_data = urllib.urlencode({'user' : g_rt_username, 'pass' : g_rt_password})
        opener.open('http://collectionscoresupport.ime.reuters.com/rt', l_login_data)
        self.m_opener=opener
        logging.debug("collectionscoresupport login done.")

    def fetch_after_id(self, ticketid=3299):
        url = self.cp.get("tickets", "tickets_url_after_id").format(ticketid)
        resp = self.m_opener.open(url)
        return resp.read()

    def fetch_by_id(self, ticketid):
        url = self.cp.get("tickets", "tickets_url_id").format(ticketid)
        resp = self.m_opener.open(url)
        return resp.read()

    def init_db_from_csv(self, filename):
        f = open(filename, 'r')
        ticketlist = self.parse_response(f.read())
        f.close()

        db = MongoDBHelper()
        logging.debug('clear all rawdata for Tickets Report')
        db.delete_all_rawdata('TicketsReport')
        for row in ticketlist:
            db.save_rawdata('TicketsReport', row)
        logging.debug('initialize ticket db finish')

    def parse_response(self, respcontent):
        """Parse collectionscoresupport response to dictionary list"""
        stream = StringIO.StringIO(respcontent)
        dictreader = csv.DictReader(stream, dialect='excel-tab')
        result = []
        for row in dictreader:
            row['Priority'] = int(row['Priority'])
            row['id'] = int(row['id'])
            if row['Resolved'] != "":
                row['Resolved'] = datetime.strptime(row['Resolved'], '%Y-%m-%d %H:%M:%S')
            row['Created'] = datetime.strptime(row['Created'], '%Y-%m-%d %H:%M:%S')
            row['LastUpdated'] = datetime.strptime(row['LastUpdated'], '%Y-%m-%d %H:%M:%S')
            result.append(row)
        stream.close()

        return result

    def update_unresolved_ticket(self):
        db = MongoDBHelper()
        cursor = db.get_rawdata_with_filter('TicketsReport', 'Status', 'open')
        logging.debug('Number of open ticket: {0}'.format(cursor.count()))
        for data in cursor:
            ticketid = data['rawdata']['id']
            resp = self.fetch_by_id(ticketid)
            ticket = self.parse_response(resp)[0]
            if ticket['Status'] != 'open':
                logging.debug('Ticket {0} status change'.format(ticket['id']))
            data['rawdata'] = ticket
            db.save_one(data)

    def update_delta_ticket(self):
        db = MongoDBHelper()
        cursor = db.get_one_rawdata_by_order('TicketsReport', 'id', -1)
        maxid = 0
        for data in cursor:
            maxid = data['rawdata']['id']
        logging.debug('Max ticket id in DB is {0}'.format(maxid))
        respcontent = self.fetch_after_id(maxid)
        ticketlist = self.parse_response(respcontent)
        for dic in ticketlist:
            db.save_rawdata('TicketsReport', dic)
        logging.debug('get delta data finish')

    def run(self):
        self.login()
        self.update_unresolved_ticket()
        self.update_delta_ticket()

    def get_all_tickets(self):
        db = RawDataDBHelper()
        return db.search_all_by_key('TicketsReport')

class _UT(unittest.TestCase):
    """docstring for _UT"""

    def testOne(self):
        logging.basicConfig(level="DEBUG")
        logging.debug('init db from Results_before_20131020.csv')
        col = TicketCollector()
        col.init_db_from_csv('Results_before_20131020.csv')
        logging.debug('finish')

    def testTwo(self):
        col = TicketCollector()
        col.login()
        col.fetch_by_id(3265)

    def testThree(self):
        logging.basicConfig(level="DEBUG")
        col = TicketCollector()
        col.run()

if __name__ == '__main__':
    logging.basicConfig(level="DEBUG")
    unittest.main()
        