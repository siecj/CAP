import unittest
import subprocess
from TagDetector import TagDetector 
import logging
logging.basicConfig(level=logging.DEBUG)
from time import time

class CAP_CVACaseLocReport():
    """docstring for CAP_CVACaseLocReport"""
    def run(self):
        hostaddr = '10.35.18.44'
        username = 'anonymous'
        password = ''
        port  =  21
        rootdir_remote = '/CVA/InternalDrop/Core/'

        l_d= TagDetector(hostaddr, username, password, rootdir_remote, port)
        l_d.login()
        latest_two_tags = l_d.get_the_two_tag()
        if latest_two_tags == []:
            logging.debug("No new Tag detected")
            return
        else:
            logging.debug("New Tag detected "+str(latest_two_tags))
            subprocess.call(["perl", "svn_diff_line_count4CVA_CORE.pl",latest_two_tags[0], latest_two_tags[1]])

class _UT(unittest.TestCase):
    """unit test of CAP_TicketsReport"""
    def testOne(self):
        hostaddr = '10.35.18.44'
        username = 'anonymous'
        password = ''
        port  =  21
        rootdir_remote = '/CVA/InternalDrop/Core/'

        l_d= TagDetector(hostaddr, username, password, rootdir_remote, port)
        l_d.login()
        latest_two_tags = l_d.get_the_two_tag()
        print latest_two_tags

def main():
    report = CAP_CVACaseLocReport()
    report.run()

if __name__ == '__main__':
    main()

