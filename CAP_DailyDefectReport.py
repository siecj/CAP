import unittest
import csv
import os
from string import Template
from mail import *

from Daily_Defect_Report import Daily_Defect_Report

class CAP_DailyDefectReport():
    """docstring for CAP_DailyDefectReport"""   
    def run(self):
        report = Daily_Defect_Report()
        report.report()
        htmlMsg = self.genMailHtml()
        self.sendMail(htmlMsg)

    def getCsv(self):
        result = []
        rawdata = os.listdir("raw data")
        for f in rawdata:
            ext = os.path.splitext(f)
            if ext[1] == ".csv":
                result.append(os.path.join(os.getcwd(), "raw data", f))

        return result

    def genMailHtml(self):
        csvList = self.getCsv()
        mailHtml = ""
        for c in csvList:
            mailHtml += self.genTableHtml(c)

        tplFile = open("html-table-template.html", "rb")

        tplHtml = Template(tplFile.read())
        tplFile.close()

        return tplHtml.substitute(contentoftable=mailHtml)

    def genTableHtml(self, srcFile):
        caption = os.path.splitext(os.path.split(srcFile)[1])[0][3:]
        ifile  = open(srcFile, "rb")
        reader = csv.reader(ifile)

        # add table header
        html = "<p>"+caption+"</p>"
        html += '<table class="gridtable">'
        rowInd = 0
        for row in reader:
            html += "<tr>"
            if rowInd == 0:
                for col in row:
                    html += "<th>"+col+"</th>"
            else:
                for col in row:
                    html += "<td>"+col+"</td>"
            html += "</tr>"
            rowInd += 1
        html += '</table><br/>'
        ifile.close()

        return html

    def sendMail(self, message):
        title = "Open Defect"
        to=['jiu.chen@thomsonreuters.com', 'zhe.wang@thomsonreuters.com', 'shan.liu@thomsonreuters.com']
        # to=['jiu.chen@thomsonreuters.com']
        send_mail('CAP_TEAM@thomsonreuters.com',to, title, message)


class _UT(unittest.TestCase):
    """docstring for ClassName"""
    def testOne(self):
        obj = CAP_DailyDefectReport()
        r = obj.genMailHtml()
        print r

if __name__ == "__main__":
    obj = CAP_DailyDefectReport()
    obj.run()
