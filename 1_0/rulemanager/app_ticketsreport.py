import unittest
import logging
from rawdatacollector.supporthelpdesk import TicketCollector

class TicketsReport():
    def run(self):
        ticketColl = TicketCollector()
        ticketColl.run()

class _UT(unittest.TestCase):
    """docstring for _UT"""
    def testOne(self):
        pass

if __name__ == '__main__':
    logging.basicConfig(filename='cap.log', level='DEBUG')
    app = TicketsReport()
    app.run()
