import matplotlib as mpl
from matplotlib.widgets import RectangleSelector
import pandas as pd
from matplotlib import pyplot as plt
import typing
from numpy.typing import ArrayLike
import numpy as np

class Brush:
    def __init__(self, xs: ArrayLike, ys: ArrayLike, ax: mpl.axes, cb,
                 color='red', alpha=0.6, edgecolor='black'):
        self.df = pd.DataFrame()
        self.df['x'] = xs
        self.df['y'] = ys
        self.cb = cb
        self.ax = ax
        props = dict(facecolor=color, edgecolor=edgecolor, alpha=alpha, 
                     fill=True)
        self.rec = RectangleSelector(ax, self.callback, props=props)

    def update_coords(self, xs: ArrayLike | None = None, 
                      ys: ArrayLike | None = None):
        if xs is not None:
            self.df['x'] = xs 
        if ys is not None:
            self.df['y'] = ys

    def callback(self, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        selected = \
            self.df[ self.df['x'].between(x1, x2, inclusive='both') & 
                     self.df['y'].between(y1, y2, inclusive='both') ]
        self.cb(selected.index.tolist())

class interaction:
    def __init__(self, chart):
        self.chart = chart 
    
    def update(self, selected):
        self.chart.selected = selected 
        self.chart.draw()

class interaction:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.x = np.random.rand(100)
        self.y = np.random.rand(100)
        self.s = np.random.rand(100)*500
        self.c = np.random.rand(100)
        self.plot = self.ax.scatter(self.x, self.y, c=self.c, s=self.s)
        abrush = Brush(self.x, self.y, self.ax, self.update)
        plt.show()
    
    def update(self, selected):
        if not selected:
            self.plot = self.ax.scatter(self.x, self.y, c=self.c, s=self.s)
        else:
            mask = np.ones(100, dtype=bool)
            mask[selected] = False
            plot = self.ax.scatter(self.x[mask], self.y[mask],
                                s=self.s[mask], color='gray')
            self.plot = self.ax.scatter(self.x[selected], self.y[selected],
                                        s=self.s[selected], c=self.c[selected])
        self.fig.canvas.draw()


if __name__ == '__main__':
    interaction()
