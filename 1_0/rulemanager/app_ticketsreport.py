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
from reportgenerator.chartgenerator import ChartGenerator

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np

class TicketsReport():
    def run(self):
        # sync tickets against web site
        ticketcoll = TicketCollector()
        ticketcoll.sync_with_website()

        # get all tickets
        alltickets = ticketcoll.get_all_tickets()

        fil = DataFiltration()

        # get weekly tickets to generate responds.csv
        startdate = datetime.today() - timedelta(7)
        respondsfidlist = ['id', 'Subject', 'CF-System Type', 'CF-Region', 'Status', 'Priority', 'Owner', 'Created', 'Resolved', 'LastUpdated', 'Queue', 'CF-Root Cause']
        weeklytickets = fil.filter_by_compare(alltickets, 'Created', startdate, 'GT', respondsfidlist)
        self.generate_responds_csv(weeklytickets, respondsfidlist, startdate)

        # generate all_hist.csv
        allhistfidlist = ['id', 'Created', 'Resolved', 'LastUpdated', 'Status', 'Queue', 'CF-System Type', 'CF-Region']
        fil = DataFiltration()
        ticlist = fil.filter_output(alltickets, allhistfidlist)
        self.generate_all_hist_csv(ticlist, allhistfidlist)

        # call perl script
        self.call_old_scripts()

        # refactor tickets-per-system plot
        monthdata = self.load_all_hist_graph_month_csv()
        chartgen = ChartGenerator()
        logging.debug("draw tickets-per-system plot")
        chartgen.draw_bar_plot(monthdata, 'Tickets Per System', 'Month', 'CreateGQS', 'CreateLegacy', 'CreateSDD', 0, 121, 'GQS', 'RAQ/DCMLS/TQS', 'SDD', "tickets-per-system.png", x_interval=2)
        logging.debug("draw tickets-per-region plot")
        chartgen.draw_bar_plot(monthdata, 'Tickets Per Region', 'Month', 'CreateEMEA', 'CreateAMERS', 'CreateAPAC', 0, 121, 'EMEA', 'AMERS', 'APAC', "tickets-per-region.png", x_interval=2)

        alldata = self.load_all_hist_graph_csv()
        logging.debug("draw tickets overview plot")
        chartgen.draw_point_plot(alldata, 'Total Tickets Overview', 'Date', 'CreateTotal', 'CloseTotal', 2500, 4000, 'Create Total', 'Close Total', 'total-tickets.png', x_interval=8)

        strDate = startdate.strftime("%Y-%m-%d")
        reportAllFilename = "WeeklySummary_" + strDate + "_ALL.htm"
        srcFile = open(reportAllFilename)
        reportAllContent = srcFile.read()
        srcFile.close()

        logging.debug("send email")
        attachmentList = ['tickets-per-system.png', 'tickets-per-region.png', 'total-tickets.png']
        title = "CCT Weekly Report for Supporting Issues from "+strDate+" to "+date.today().strftime('%Y-%m-%d')
        to = ['sheng.chen@thomsonreuters.com', 'stephen.li@thomsonreuters.com', 'jianping.zuo@thomsonreuters.com', 'cynthia.wang@thomsonreuters.com','peter.zhu@thomsonreuters.com']
        cclist = ['jiu.chen@thomsonreuters.com', 'hongfeng.yao@thomsonreuters.com', 'liang.zhang1@thomsonreuters.com', 'chao.xie@thomsonreuters.com']
        send_mail_ex(to, title, reportAllContent, images=attachmentList, cc=cclist)

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
                ind = 1
                continue
            else:
                result.append(row)
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
    logging.basicConfig(filename='cap.log', level='DEBUG')
    # logging.basicConfig(level='DEBUG')
    # unittest.main()
    app = TicketsReport()
    app.run()
