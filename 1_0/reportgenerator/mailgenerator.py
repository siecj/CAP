import logging
import unittest

class MailGenerator():
    """docstring for MailGenerator"""
    def gen_table_html(self, dictlist, caption, headers):
        html = "<p>"+caption+"</p>"
        html += '<table class="gridtable">'
        html += "<tr>"
        for col in headers:
            html +=  "<th>"+col+"</th>"
        html += "</tr>"
        for row in dictlist:
            html += "<tr>"
            for col in headers:
                html +=  "<td>"+row[col]+"</td>"
            html += "</tr>"
        html += '</table><br/>'
        return html

    def get_template(self, tplfile):
        f = open(tplfile, "rb")
        mailtpl = Template(f.read())
        f.close()
        return mailtpl

class _UT(unittest.TestCase):
    def test1(self):
        pass

if __name__ == '__main__':
    logging.baiscConfig(level='debug', format='[%(asctime)s][%(levelname)s]-%(message)s')
    unittest.main()
        