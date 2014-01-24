import unittest
import logging
import subprocess
import csv
import os
from datetime import *
from rawdatacollector.ticketcollector import TicketCollector
from datamanager.mongodb import RawDataDBHelper
from dataprocessor.datafiltration import DataFiltration
from reportpublisher.mail import *

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np

class TicketsReport():
    def run(self):
        # get all tickets
        # filter tickets to get internal data (responds.csv, all_hist.csv)
        # adapter old sricpt to get dictlist for chart and report
        # generate chart and report mail
        # send mail

        # sync tickets against web site
        # ticketColl = TicketCollector()
        # ticketColl.run()

        # get all tickets
        dbhelper = RawDataDBHelper()
        alltickets = dbhelper.search_all_by_key('TicketsReport')

        fil = DataFiltration()

        # get weekly tickets to generate responds.csv
        startdate = datetime.today() - timedelta(7)
        logging.debug(startdate)
        respondsfidlist = ['id', 'Subject', 'CF-System Type', 'CF-Region', 'Status', 'Priority', 'Owner', 'Created', 'Resolved', 'LastUpdated', 'Queue', 'CF-Root Cause']
        weeklytickets = fil.filter_by_compare(alltickets, 'Created', startdate, 'GT', respondsfidlist)
        self.generate_responds_csv(weeklytickets, respondsfidlist, startdate)
        logging.debug(len(weeklytickets))

        # generate all_hist.csv
        allhistfidlist = ['id', 'Created', 'Resolved', 'LastUpdated', 'Status', 'Queue', 'CF-System Type', 'CF-Region']
        fil = DataFiltration()
        ticlist = fil.filter_output(alltickets, allhistfidlist)
        self.generate_all_hist_csv(ticlist, allhistfidlist)

        # call perl script
        self.call_old_scripts()

        logging.debug("draw tickets-per-system plot")
        self.genSystemPlot()
        logging.debug("draw tickets-per-region plot")
        self.genRegionPlot()
        logging.debug("draw tickets overview plot")
        self.genTicketsOverviewPlot()

        strDate = startdate.strftime("%Y-%m-%d")
        reportAllFilename = "WeeklySummary_" + strDate + "_ALL.htm"
        srcFile = open(reportAllFilename)
        reportAllContent = srcFile.read()
        srcFile.close()

        logging.debug("send email")
        attachmentList = ['tickets-per-system.png', 'tickets-per-region.png', 'total-tickets.png']
        title = "CCT Weekly Report for Supporting Issues from "+strDate+" to "+date.today().strftime('%Y-%m-%d')
        # to=['sheng.chen@thomsonreuters.com', 'stephen.li@thomsonreuters.com', 'jianping.zuo@thomsonreuters.com', 'cynthia.wang@thomsonreuters.com', 'hongfeng.yao@thomsonreuters.com', 'peter.zhu@thomsonreuters.com', 'jiu.chen@thomsonreuters.com', 'liang.zhang1@thomsonreuters.com', 'chao.xie@thomsonreuters.com']
        to = ['jiu.chen@thomsonreuters.com']
        send_mail('CAP@thomsonreuters.com',to, title, reportAllContent, attachmentList)

        self.clear_temp_file()


    def generate_responds_csv(self, dictlist, fidlist, startdate):
        for item in dictlist:
            if item['Status'] == 'stalled':
                item['Status'] = 'Resolved'
                item['Resolved'] = item['LastUpdated']

        f = open('responds.csv', 'w')
        f.write('#start_date: {0}\n'.format(startdate.strftime('%Y-%m-%d')))
        for fid in fidlist:
            f.write('{0}\t'.format(fid))
        f.write('\n')
        for ticket in dictlist:
            for fid in fidlist:
                if fid == 'LastUpdated':
                    continue
                f.write('{0}\t'.format(ticket[fid]))
            f.write('\n')
        f.close()

    def generate_all_hist_csv(self, dictlist, fidlist):
        for item in dictlist:
            if item['Status'] == 'stalled':
                item['Status'] = 'Resolved'
                item['Resolved'] = item['LastUpdated']
                
        mapQueue = {"General":1,"Service Affecting" :3,"Defect Report" :4,"Request For Help" :5}
        f = open('all_hist.csv', 'w')
        f.write('#')
        for fid in fidlist:
            f.write('{0},'.format(fid))
        f.write('\n')
        for item in dictlist:
            for fid in fidlist:
                if fid == 'Queue':
                    if mapQueue.has_key(item[fid]):
                        f.write('{0},'.format(mapQueue[item[fid]]))
                    else:
                        f.write(',')
                elif fid == 'LastUpdated':
                    continue
                else:
                    f.write('{0},'.format(item[fid]))
            f.write('\n')
        f.close()

    def load_all_hist_graph_csv(self):
        filename = 'all_hist_graph.csv'
        f = open(filename, 'r')
        reader = csv.DictReader(f)
        ind = 0
        result = []
        for row in reader:
            result.append(row)
        f.close()
        return result

    def load_all_hist_graph_month_csv(self):
        filename = 'all_hist_graph_month.csv'
        f = open(filename, 'r')
        reader = csv.DictReader(f)
        ind = 0
        result = []
        for row in reader:
            if ind == 0:
                continue
            else:
                result.append(row)
            ind += 1
        f.close()
        return result

    def call_old_scripts(self):
        subprocess.call(["perl", "rulemanager\_3_gen_report_ALL.pl"])
        subprocess.call(["perl", "rulemanager\_4_gen_graph_month.pl"])
        subprocess.call(["perl", "rulemanager\_4_gen_graph_week.pl"])

    def clear_temp_file(self):
        os.remove('all_hist.csv')
        os.remove('all_hist_graph.csv')
        os.remove('all_hist_graph_month.csv')
        os.remove('responds.csv')
        os.remove('tickets-per-region.png')
        os.remove('tickets-per-system.png')
        os.remove('total-tickets.png')

    def autolabel(self, rects):
        for rect in rects:
            height = rect.get_height()
            if (height < 3):
                y = rect.get_y()-2
            elif (height <= 9):
                y = rect.get_y()
            else:
                y = 0.35*height + rect.get_y()
            plt.text(rect.get_x()+rect.get_width()/2., y, '%d'%int(height), ha='center', va='bottom')

    def drawBarPlot(self, x_ray, y_1, y_2, y_3, y_max, title, legend1, legend2, legend3, outputfile):
        plt.cla()
        ind = np.arange(len(x_ray))
        width = 0.35

        y_3_bottom = []
        for i in range(len(y_1)):
            y_3_bottom.append(y_1[i] + y_2[i])

        p1 = plt.bar(ind, y_1, width, color='r')
        p2 = plt.bar(ind, y_2, width, color='y', bottom=y_1)
        p3 = plt.bar(ind, y_3, width, color='g', bottom=y_3_bottom)

        self.autolabel(p1)
        self.autolabel(p2)
        self.autolabel(p3)

        plt.title(title + '\n')
        plt.xticks(ind+width/2., x_ray )
        plt.yticks(np.arange(0,y_max,20))
        plt.legend( (p1[0], p2[0], p3[0]), (legend1, legend2, legend3) )

        plt.grid(True)
        plt.savefig(outputfile)

    def genSystemPlot(self):
        """Tickets Per System"""
        r = mlab.csv2rec('all_hist_graph_month.csv')
        x_ray = []
        y_GQS = []
        y_RAQ = []
        y_SDD = []
        y_SDD_bottom = []

        ind = np.arange(len(r))
        for i in range(len(r))[1:]:
            if i%2==0:
                x_ray.append(r[i][0])
            else:
                x_ray.append("")
            y_GQS.append(int(r[i][3]))
            y_RAQ.append(int(r[i][5]))
            y_SDD.append(int(r[i][7]))

        self.drawBarPlot(x_ray, y_GQS, y_RAQ, y_SDD, 121, "Tickets Per System", 
            'GQS', 'RAQ/DCMLS/TQS', 'SDD', "tickets-per-system.png")

    def genRegionPlot(self):
        """Tickets Per Region"""
        r = mlab.csv2rec('all_hist_graph_month.csv')
        x_ray = []
        y_EMEA = []
        y_AMERS = []
        y_APAC = []

        ind = np.arange(len(r))
        for i in range(len(r))[1:]:
            if i%2==0:
                x_ray.append(r[i][0])
            else:
                x_ray.append("")
            y_EMEA.append(int(r[i][11]))
            y_AMERS.append(int(r[i][13]))
            y_APAC.append(int(r[i][15]))

        self.drawBarPlot(x_ray, y_EMEA, y_AMERS, y_APAC, 121, "Tickets Per Region", 
            'EMEA', 'AMERS', 'APAC', "tickets-per-region.png")

    def genTicketsOverviewPlot(self):
        """"Total Tickets Overview"""
        r = mlab.csv2rec('all_hist_graph.csv')
        x_ray = []
        y_create_total = []
        y_close_total = []
        ind = range(len(r))
        for i in ind:
            if i % 8 == 0:
                x_ray.append(r[i][1].strftime('%m/%d/%y'))
            else:
                x_ray.append("")
            y_create_total.append(r[i][10])
            y_close_total.append(r[i][11])

        plt.cla()
        p1 = plt.plot(ind, y_create_total, 'bo-')
        p2 = plt.plot(ind, y_close_total, 'ro-')
        plt.axis([ind[0], ind[-1], 2500, 4000])
        plt.xticks(ind, x_ray)

        plt.title('Total Tickets Overview\n')
        plt.legend( (p1[0], p2[0]), ('Create Total', 'Close Total'), loc=4 )
        plt.grid(True, axis='y')
        fig = plt.gcf()
        fig.set_figwidth(13)
        plt.savefig("total-tickets.png")


class _UT(unittest.TestCase):
    """docstring for _UT"""
    def setUp(self):
        logging.basicConfig(level="DEBUG")

        dbhelper = RawDataDBHelper()
        self.alltickets = dbhelper.search_all_by_key('TicketsReport')
        
    def testOne(self):
        fil = DataFiltration()
        startdate = datetime.today() - timedelta(7)
        logging.debug(startdate)
        outputfidlist = ['id', 'Subject', 'CF-System Type', 'CF-Region', 'Status', 'Priority', 'Owner', 'Created', 'Resolved', 'Queue', 'CF-Root Cause']
        weeklytickets = fil.filter_by_compare(self.alltickets, 'Created', startdate, 'GT', outputfidlist)
        logging.debug(weeklytickets)

        # change weeklytickets to responds.csv
        tr = TicketsReport()
        tr.generate_responds_csv(weeklytickets, outputfidlist, startdate)

        subprocess.call(["perl", "rulemanager\_3_gen_report_ALL.pl"])

    def test2(self):
        outputfidlist = ['id', 'Created', 'Resolved', 'Status', 'Queue', 'CF-System Type', 'CF-Region']
        fil = DataFiltration()
        ticlist = fil.filter_output(self.alltickets, outputfidlist)

        tr = TicketsReport()
        tr.generate_all_hist_csv(ticlist, outputfidlist)

        subprocess.call(["perl", "rulemanager\_4_gen_graph_month.pl"])
        subprocess.call(["perl", "rulemanager\_4_gen_graph_week.pl"])

        tr.load_all_hist_graph_month_csv()


if __name__ == '__main__':
    # logging.basicConfig(filename='cap.log', level='DEBUG')
    logging.basicConfig(level='DEBUG')
    # unittest.main()
    app = TicketsReport()
    app.run()
