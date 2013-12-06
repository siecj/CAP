import unittest
import subprocess
from TagDetector import TagDetector 
import logging
logging.basicConfig(level=logging.DEBUG)
from time import time
import os
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np


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
            subprocess.call(["perl", "svn_diff_line_count4CVA_CORE.pl",latest_two_tags[1], latest_two_tags[0]])

            self.genPlot()

            # attachmentList = ['CORE.png']
            # title = "CVA CORE Test Affinity"
            # to=['jiu.chen@thomsonreuters.com', 'hongfeng.yao@thomsonreuters.com']
            # send_mail('hongfeng.yao@thomsonreuters.com',to, title, "", attachmentList)


    def genPlot(self):
        r = mlab.csv2rec('testAffinity.csv')
        x_ray = []
        y_ray = []
        ind = np.arange(len(r))
        for i in ind:
            x_ray.append(r[i][0] + "-" + r[i][1])
            y_ray.append((r[i][4] + r[i][6])*100.00 / (r[i][2] + r[i][3]))

        plt.cla()
        p1 = plt.plot(ind, y_ray, 'bo-')
        # p2 = plt.plot(ind, y_close_total, 'ro-')
        plt.axis([ind[0], ind[-1], 0, 12])
        plt.xticks(ind, x_ray, rotation=90)

        plt.title('TestCase#/LOC\n')
        plt.grid(True, axis='y')
        # fig = plt.gcf()
        # fig.set_figwidth(13)
        # fig.set_size_inches(16, 8)
        plt.savefig('CORE.png', dpi=100)

    def drawLinePlot(self, x_ray, y_ray, title):
        plt.cla()
        ind = np.arange(len(x_ray))
        p1 = plt.plot(ind, y_ray, 'bo-')
        plt.axis([ind[0], ind[-1], 0, 12])
        plt.xticks(ind, x_ray, rotation=90)

        plt.title('TestCase#/LOC\n')
        plt.grid(True, axis='y')
        plt.show()

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

    def testTwo(self):
        report = CAP_CVACaseLocReport()
        report.genPlot()

def main():
    report = CAP_CVACaseLocReport()
    report.run()

if __name__ == '__main__':
    main()

