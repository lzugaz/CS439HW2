import sys
import time

import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QGridLayout, QPushButton, QComboBox, QSlider, QLabel

import random

# Some random datasets to select from
tx = np.arange(10)
px = np.arange(20)
gx = np.arange(45)
temperatures = [ 32 + 60*random.random() for x in tx ]
prices = [ 20 + 180*random.random() for x in px ]
grades = [ 100*random.random() for x in gx ]
data = { 'Temperatures': {'x': tx, 'y': temperatures, 'xlabel': 'days', 'ylabel': 'Daily Max Temp (in F)'}, 
         'Prices': { 'x': px, 'y': prices, 'xlabel': 'items', 'ylabel': 'Price (in $)'},
         'Grades': { 'x': gx, 'y': grades, 'xlabel': 'student', 'ylabel': 'Midterm Grade (/100)' } }

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        layout = QtWidgets.QGridLayout(self.main_widget)
        self.width = 1

        self.mpl_canvas = FigureCanvas(Figure(figsize=(6, 4)))

        self.dropdown = QComboBox(self.main_widget)
        for name in data.keys():
            self.dropdown.addItem(name)

        self.slider = QSlider(self.main_widget)
        self.slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(10)

        layout.addWidget(NavigationToolbar(self.mpl_canvas, self), 0, 0, 1, 6)
        layout.addWidget(self.mpl_canvas,                          1, 0, 4, 4)
        layout.addWidget(QLabel('Data selection'),                   1, 4, 1, 1)
        layout.addWidget(self.dropdown,                            1, 5, 1, 1)
        layout.addWidget(QLabel('Line width'),                     2, 4, 1, 1)
        layout.addWidget(self.slider,                              2, 5, 1, 1)

        self.ax = self.mpl_canvas.figure.subplots()
        self.create_plot(data['Temperatures'])

        self.dropdown.activated.connect(self.update_data)
        self.slider.valueChanged.connect(self.update_width)

    def create_plot(self, d):
        self.plots = self.ax.plot(d['x'], d['y'], linewidth=self.width)
        self.ax.set_xlabel(d['xlabel'])
        self.ax.set_ylabel(d['ylabel'])

    def update_data(self, index):
        name = self.dropdown.currentText()
        self.ax.clear()
        self.plots = self.create_plot(data[name])
        self.mpl_canvas.draw()

    def update_width(self, width):
        self.width = width
        self.plots[0].set_linewidth(width)
        self.mpl_canvas.draw()


if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()