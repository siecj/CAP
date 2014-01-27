# -*- coding: utf-8 -*-

import unittest
import logging
import csv
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np

class ChartGenerator():
    """docstring for ChartGenerator"""
    # def __init__(self, arg):
    #     super(ChartGenerator, self).__init__()
    #     self.arg = arg

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

    def draw_point_plot(self, dictlist, title, fid_x, fid_y1, fid_y2, y_min, y_max, legend1, legend2, outputfile, x_interval=1):
        ind = np.arange(len(dictlist))
        x_ray = self.get_x_from_dictlist(dictlist, fid_x, x_interval)
        y_1 = self.get_column_from_dictlist(dictlist, fid_y1)
        y_2 = self.get_column_from_dictlist(dictlist, fid_y2)

        plt.cla()
        p1 = plt.plot(ind, y_1, 'bo-')
        p2 = plt.plot(ind, y_2, 'ro-')
        plt.axis([ind[0], ind[-1], y_min, y_max])
        plt.xticks(ind, x_ray)

        plt.title(title + '\n')
        plt.legend( (p1[0], p2[0]), (legend1, legend2), loc=4 )
        plt.grid(True, axis='y')
        fig = plt.gcf()
        fig.set_figwidth(13)
        plt.savefig(outputfile)

    def draw_bar_plot(self, dictlist, title, fid_x, fid_y1, fid_y2, fid_y3, y_min, y_max, legend1, legend2, legend3, outputfile, x_interval=1):
        ind = np.arange(len(dictlist))
        x_ray = self.get_x_from_dictlist(dictlist, fid_x, x_interval)
        y_1 = self.get_int_list_from_dictlist(dictlist, fid_y1)
        y_2 = self.get_int_list_from_dictlist(dictlist, fid_y2)
        y_3 = self.get_int_list_from_dictlist(dictlist, fid_y3)

        plt.cla()
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

    def get_column_from_dictlist(self, dictlist, fidname):
        result = []
        for item in dictlist:
            result.append(item[fidname])
        return result

    def get_int_list_from_dictlist(self, dictlist, fidname):
        result = []
        for item in dictlist:
            result.append(int(item[fidname]))
        return result

    def get_x_from_dictlist(self, dictlist, fidname, interval=1):
        result = []
        for i in range(len(dictlist)):
            if i % interval == 0:
                result.append(dictlist[i][fidname])
            else:
                result.append('')
        return result

class _UT(unittest.TestCase):
    """docstring for _UT"""
    def test1(self):
        logging.debug('------- test 1 ------')
        f = open('all_hist_graph.csv', 'r')
        reader = csv.DictReader(f)
        dictlilst = []
        for row in reader:
            dictlilst.append(row)
        f.close()
        logging.debug('load test data finish')
        cg = ChartGenerator()
        cg.draw_point_plot(dictlilst, 'Total Tickets Overview', 'Date', 'CreateTotal', 'CloseTotal', 0, 3500, 'Create Total', 'Close Total', 'total-tickets.png')

        logging.debug('------- end of test 1 ------')

if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    unittest.main()
        