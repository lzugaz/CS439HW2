import matplotlib as mpl
from matplotlib.widgets import RectangleSelector
import numpy as np
import argparse 
from matplotlib import pyplot as plt
import pandas as pd
import sys

from brush import Brush
import legend
from random import Random

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QGridLayout, QPushButton, QComboBox, QSlider, QLabel

from numpy.typing import ArrayLike
from bubble_chart import BubbleChart

class interaction:
    def __init__(self, chart):
        self.chart = chart 
    
    def update(self, selected):
        chart.selected = selected 
        chart.draw()

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self, args):
        super().__init__()
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        layout = QtWidgets.QGridLayout(self.main_widget)
        self.width = 1
        self.npoints = args.number

        x = np.random.rand(self.npoints)
        y = np.random.rand(self.npoints)
        c = np.random.rand(self.npoints)
        s = np.random.rand(self.npoints)

        self.mpl_canvas = FigureCanvas(Figure(figsize=(8, 8)))

        self.chart = BubbleChart(x=x, y=y, s=s, c=c, xname='x', yname='y', 
                                 sname='size', cname='colors', fig=self.mpl_canvas.figure)

        if args.brush:
            brush = Brush(x, y, self.chart.ax, self.update_selection, color='blue')

        self.toolbar = NavigationToolbar(self.mpl_canvas, self)
        self.button_x = QPushButton('Update X')   
        self.button_y = QPushButton('Update Y')    
        self.button_s = QPushButton('Update Size') 
        self.button_c = QPushButton('Update Color')
        self.button_i = QPushButton('Increase Size')
        self.button_d = QPushButton('Decrease Size')

        layout.addWidget(self.toolbar,      0, 0, 1, 6)
        layout.addWidget(self.mpl_canvas,   1, 0, 4, 4)
        layout.addWidget(self.button_x,     1, 4, 1, 1)
        layout.addWidget(self.button_y,     1, 5, 1, 1)
        layout.addWidget(self.button_s,     2, 4, 1, 1)
        layout.addWidget(self.button_c,     2, 5, 1, 1)
        layout.addWidget(self.button_i,     3, 4, 1, 1)
        layout.addWidget(self.button_d ,    3, 5, 1, 1)

        self.fig = self.chart.fig 
        self.ax = self.chart.ax 
        brush = Brush(x, y, self.ax, self.update_selection, color='blue')
        self.chart.draw()

        self.button_x.clicked.connect(self.update_x)
        self.button_y.clicked.connect(self.update_y)
        self.button_s.clicked.connect(self.update_s)
        self.button_c.clicked.connect(self.update_c)
        self.button_i.clicked.connect(self.update_i)
        self.button_d.clicked.connect(self.update_d)

    def redraw(self):
        self.chart.draw()
        self.mpl_canvas.draw()

    def update_x(self):
        x = np.random.rand(self.npoints)
        self.chart.set_data('x', x, 'x')
        self.redraw()

    def update_y(self):
        y = np.random.rand(self.npoints)
        self.chart.set_data('y', y, 'y')
        self.redraw()

    def update_s(self):
        s = np.random.rand(self.npoints)
        self.chart.set_data('s', s, 'sizes')
        self.redraw()

    def update_c(self):
        c = np.random.rand(self.npoints)
        self.chart.set_data('c', c, 'colors')
        self.redraw()

    def update_i(self):
        self.chart.scale = self.chart.scale * 1.5
        self.chart.update_sizes()
        self.redraw()

    def update_d(self):
        self.chart.scale = self.chart.scale / 1.5
        self.chart.update_sizes()
        self.redraw()

    def update_selection(self, selected):
        self.chart.selected = selected 
        self.redraw()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Demonstrate bubble chart')
    parser.add_argument('-n', '--number', type=int, default=100, help='Number of data points')
    parser.add_argument('--brush', action='store_true', help='Activate brush selector')
    args = parser.parse_args()

    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow(args)
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()