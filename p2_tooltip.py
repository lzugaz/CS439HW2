import sys
import pandas as pd
import numpy as np
import argparse
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QComboBox, QSlider, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from matplotlib.widgets import RectangleSelector
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import viridis


class Brush:
    def __init__(self, xs, ys, ax, callback, canvas, color='red', alpha=0.6, edgecolor='black'):
        self.df = pd.DataFrame({'x': xs, 'y': ys})
        self.callback = callback
        self.ax = ax
        self.canvas = canvas
        self.rec = RectangleSelector(ax, self.onselect, useblit=True, interactive=True)

    def onselect(self, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        selected = self.df[(self.df['x'].between(x1, x2)) & (self.df['y'].between(y1, y2))]
        self.callback(selected.index.tolist())  

        self.canvas.draw_idle() 


class LinkedBubbleChartApp(QtWidgets.QMainWindow):
    def __init__(self, dataset):
        super().__init__()

        self.dataset = pd.read_csv(dataset)
        self.attributes = self.dataset.columns.tolist()
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        self.canvas1 = FigureCanvas(Figure(figsize=(6, 6)))
        self.ax1 = self.canvas1.figure.subplots()

        self.canvas2 = FigureCanvas(Figure(figsize=(6, 6)))
        self.ax2 = self.canvas2.figure.subplots()
        chart_layout = QHBoxLayout()
        chart_layout.addWidget(NavigationToolbar(self.canvas1, self))
        chart_layout.addWidget(self.canvas1)
        chart_layout.addWidget(NavigationToolbar(self.canvas2, self))
        chart_layout.addWidget(self.canvas2)
        self.layout.addLayout(chart_layout)

        self.controls_layout1 = QHBoxLayout()
        self.controls_layout1.addWidget(QLabel('Chart 1:'))

        self.controls_layout1.addWidget(QLabel('X:'))
        self.x_dropdown1 = self.add_dropdown(self.controls_layout1)

        self.controls_layout1.addWidget(QLabel('Y:'))
        self.y_dropdown1 = self.add_dropdown(self.controls_layout1)

        self.controls_layout1.addWidget(QLabel('Size:'))
        self.radius_dropdown1 = self.add_dropdown(self.controls_layout1)

        self.controls_layout1.addWidget(QLabel('Color:'))
        self.color_dropdown1 = self.add_dropdown(self.controls_layout1)

        self.controls_layout1.addWidget(QLabel('Bubble Size Scale:'))
        self.size_slider1 = self.add_slider(self.controls_layout1)
        
        self.layout.addLayout(self.controls_layout1)

        self.controls_layout2 = QHBoxLayout()
        self.controls_layout2.addWidget(QLabel('Chart 2:'))

        self.controls_layout2.addWidget(QLabel('X:'))
        self.x_dropdown2 = self.add_dropdown(self.controls_layout2)

        self.controls_layout2.addWidget(QLabel('Y:'))
        self.y_dropdown2 = self.add_dropdown(self.controls_layout2)

        self.controls_layout2.addWidget(QLabel('Size:'))
        self.radius_dropdown2 = self.add_dropdown(self.controls_layout2)

        self.controls_layout2.addWidget(QLabel('Color:'))
        self.color_dropdown2 = self.add_dropdown(self.controls_layout2)

        self.controls_layout2.addWidget(QLabel('Bubble Size Scale:'))
        self.size_slider2 = self.add_slider(self.controls_layout2)
        
        self.layout.addLayout(self.controls_layout2)

        for attr in self.attributes:
            self.x_dropdown1.addItem(attr)
            self.y_dropdown1.addItem(attr)
            self.radius_dropdown1.addItem(attr)
            self.color_dropdown1.addItem(attr)

            self.x_dropdown2.addItem(attr)
            self.y_dropdown2.addItem(attr)
            self.radius_dropdown2.addItem(attr)
            self.color_dropdown2.addItem(attr)

        self.x_dropdown1.currentIndexChanged.connect(self.update_plot)
        self.y_dropdown1.currentIndexChanged.connect(self.update_plot)
        self.radius_dropdown1.currentIndexChanged.connect(self.update_plot)
        self.color_dropdown1.currentIndexChanged.connect(self.update_plot)
        self.size_slider1.valueChanged.connect(self.update_plot)

        self.x_dropdown2.currentIndexChanged.connect(self.update_plot)
        self.y_dropdown2.currentIndexChanged.connect(self.update_plot)
        self.radius_dropdown2.currentIndexChanged.connect(self.update_plot)
        self.color_dropdown2.currentIndexChanged.connect(self.update_plot)
        self.size_slider2.valueChanged.connect(self.update_plot)

        self.brush1 = None
        self.brush2 = None

        self.selected_indices_chart1 = []
        self.selected_indices_chart2 = []
        self.annot1 = self.ax1.annotate(
            "", xy=(0, 0), xytext=(20, 20),
            textcoords="offset points", bbox=dict(boxstyle="round", fc="red"),
            arrowprops=dict(arrowstyle="->")
        )

        self.annot1.set_visible(False)

        self.annot2 = self.ax2.annotate("", xy=(0, 0), xytext=(20, 20),
                                    textcoords="offset points", bbox=dict(boxstyle="round", fc="red"),
                                    arrowprops=dict(arrowstyle="->"))
        self.annot2.set_visible(False)

        self.canvas1.mpl_connect("motion_notify_event", self.hover_chart1)
        self.canvas2.mpl_connect("motion_notify_event", self.hover_chart2)

        self.update_plot()
        




     


    def add_dropdown(self, layout):
        dropdown = QComboBox(self)
        layout.addWidget(dropdown)
        return dropdown

    def add_slider(self, layout):
        slider = QSlider(QtCore.Qt.Orientation.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(100)
        slider.setValue(10)
        layout.addWidget(slider)
        return slider

    def brush_callback_chart1(self, selected):
        self.selected_indices_chart1 = selected
        self.update_plot()

    def brush_callback_chart2(self, selected):
        self.selected_indices_chart2 = selected
        self.update_plot()


    def update_annot_chart1(self, ind, sc, on):
        if on:
            pos = sc.get_offsets()[ind["ind"][0]]

            row = self.dataset.iloc[ind['ind'][0]]
            text = (
                f"name: {row['name']}\n"
                f"region: {row['region']}\n"
                f"CO2: {row['CO2']}\n"
                f"GDP_per_capita: {row['GDP_per_capita']}\n"
                f"airports: {row['airports']}\n"
                f"alcohol: {row['alcohol']}\n"
                f"area: {row['area']}\n"
                f"birth_rate: {row['birth_rate']}\n"
                f"broadband: {row['broadband']}\n"
            )

            if hasattr(self, 'hover_text'):
                self.hover_text.remove() 

            self.hover_text = self.ax1.text(
                0.95, 0.95, text, transform=self.ax1.transAxes,  
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white', alpha=0.8)
            )
            self.canvas1.draw_idle()  
        else:
            if hasattr(self, 'hover_text'):
                self.hover_text.remove() 
                del self.hover_text  
            self.canvas1.draw_idle()
    def update_annot_chart2(self, ind, sc, on):
        
        if on:
            pos = sc.get_offsets()[ind["ind"][0]]

            row = self.dataset.iloc[ind['ind'][0]]
            text = (
                f"name: {row['name']}\n"
                f"region: {row['region']}\n"
                f"CO2: {row['CO2']}\n"
                f"GDP_per_capita: {row['GDP_per_capita']}\n"
                f"airports: {row['airports']}\n"
                f"alcohol: {row['alcohol']}\n"
                f"area: {row['area']}\n"
                f"birth_rate: {row['birth_rate']}\n"
                f"broadband: {row['broadband']}\n"
            )

            if hasattr(self, 'hover_text'):
                self.hover_text.remove() 

            self.hover_text = self.ax2.text(
                0.95, 0.95, text, transform=self.ax2.transAxes, 
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white', alpha=0.8)
            )
            self.canvas2.draw_idle() 
        else:
            if hasattr(self, 'hover_text'):
                self.hover_text.remove() 
                del self.hover_text  
            self.canvas1.draw_idle()  
    

    def hover_chart1(self, event):
        if event.inaxes == self.ax1:
            cont, ind = self.scatter1.contains(event)
            
            if cont:
                self.update_annot_chart1(ind, self.scatter1, on=True)
            else:
                self.update_annot_chart1(ind, self.scatter1, on=False)



    def hover_chart2(self, event):
        if event.inaxes == self.ax2:
            cont, ind = self.scatter2.contains(event)
            
            if cont:
                self.update_annot_chart2(ind, self.scatter2, on=True)
            else:
                self.update_annot_chart2(ind, self.scatter2, on=False)
                self.canvas2.draw_idle()

    def update_plot(self):
        x_attr1 = self.x_dropdown1.currentText()
        y_attr1 = self.y_dropdown1.currentText()
        radius_attr1 = self.radius_dropdown1.currentText()
        color_attr1 = self.color_dropdown1.currentText()

        x_attr2 = self.x_dropdown2.currentText()
        y_attr2 = self.y_dropdown2.currentText()
        radius_attr2 = self.radius_dropdown2.currentText()
        color_attr2 = self.color_dropdown2.currentText()

        if not (x_attr1 and y_attr1 and radius_attr1 and color_attr1):
            return
        if not (x_attr2 and y_attr2 and radius_attr2 and color_attr2):
            return

        size_scale1 = self.size_slider1.value()
        size_scale2 = self.size_slider2.value()

        self.canvas1.figure.clf()  
        self.canvas2.figure.clf() 

        self.ax1 = self.canvas1.figure.add_subplot(111)
        self.ax2 = self.canvas2.figure.add_subplot(111)

        x1 = pd.to_numeric(self.dataset[x_attr1], errors='coerce').fillna(0)
        y1 = pd.to_numeric(self.dataset[y_attr1], errors='coerce').fillna(0)
        radius1 = pd.to_numeric(self.dataset[radius_attr1], errors='coerce').fillna(1)
        color1 = pd.to_numeric(self.dataset[color_attr1], errors='coerce').fillna(0)

        x2 = pd.to_numeric(self.dataset[x_attr2], errors='coerce').fillna(0)
        y2 = pd.to_numeric(self.dataset[y_attr2], errors='coerce').fillna(0)
        radius2 = pd.to_numeric(self.dataset[radius_attr2], errors='coerce').fillna(1)
        color2 = pd.to_numeric(self.dataset[color_attr2], errors='coerce').fillna(0)

        scaled_radius1 = radius1 * size_scale1 / radius1.max()
        scaled_radius2 = radius2 * size_scale2 / radius2.max()
        
        max_val1 = radius1.max()
        min_val1 = radius1.min()
        legend_sizes1 = np.linspace(min_val1, max_val1, 3) 
        legend_bubbles1 = legend_sizes1 * size_scale1 / max_val1

        for size, scaled_size in zip(legend_sizes1, legend_bubbles1):
            self.ax1.scatter([], [], s=scaled_size, c='gray', alpha=0.6, label=f'{size:.1f}')

        self.ax1.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Bubble Size", loc="upper right")

        if self.selected_indices_chart1:
            selected_mask1 = np.zeros_like(x1, dtype=bool)
            selected_mask1[self.selected_indices_chart1] = True
        else:
            selected_mask1 = np.ones_like(x1, dtype=bool)

        if self.selected_indices_chart2:
            selected_mask2 = np.zeros_like(x2, dtype=bool)
            selected_mask2[self.selected_indices_chart2] = True
        else:
            selected_mask2 = np.ones_like(x2, dtype=bool)
        
        max_val2 = radius2.max()
        min_val2 = radius2.min()
        legend_sizes2 = np.linspace(min_val2, max_val2, 3)  
        legend_bubbles2 = legend_sizes2 * size_scale2 / max_val2

        for size, scaled_size in zip(legend_sizes2, legend_bubbles2):
            self.ax2.scatter([], [], s=scaled_size, c='gray', alpha=0.6, label=f'{size:.1f}')

        self.ax2.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Bubble Size", loc="upper right")


        self.ax1.scatter(x1[~selected_mask1], y1[~selected_mask1], s=scaled_radius1[~selected_mask1],
                        c='gray', alpha=0.4)
        scatter1 = self.ax1.scatter(x1[selected_mask1], y1[selected_mask1], s=scaled_radius1[selected_mask1],
                                    c=color1[selected_mask1], alpha=0.6, cmap='viridis')
        self.ax1.set_xlabel(x_attr1)
        self.ax1.set_ylabel(y_attr1)
        self.ax1.set_title(f'Bubble Chart 1: {x_attr1} vs {y_attr1}')
        self.colorbar1 = self.canvas1.figure.colorbar(scatter1, ax=self.ax1, label=color_attr1)

        self.ax2.scatter(x2[~selected_mask2], y2[~selected_mask2], s=scaled_radius2[~selected_mask2],
                        c='gray', alpha=0.4)
        scatter2 = self.ax2.scatter(x2[selected_mask2], y2[selected_mask2], s=scaled_radius2[selected_mask2],
                                    c=color2[selected_mask2], alpha=0.6, cmap='viridis')
        self.ax2.set_xlabel(x_attr2)
        self.ax2.set_ylabel(y_attr2)
        self.ax2.set_title(f'Bubble Chart 2: {x_attr2} vs {y_attr2}')
        self.colorbar2 = self.canvas2.figure.colorbar(scatter2, ax=self.ax2, label=color_attr2)

        self.scatter1 = scatter1
        self.scatter2 = scatter2

        self.canvas1.mpl_connect("motion_notify_event", self.hover_chart1)
        self.canvas2.mpl_connect("motion_notify_event", self.hover_chart2)

        if self.brush1:
            self.brush1.rec.disconnect_events()
        self.brush1 = Brush(x1, y1, self.ax1, self.brush_callback_chart1, self.canvas1)

        if self.brush2:
            self.brush2.rec.disconnect_events()
        self.brush2 = Brush(x2, y2, self.ax2, self.brush_callback_chart2, self.canvas2)

        self.canvas1.figure.tight_layout()
        self.canvas2.figure.tight_layout()

        
        self.canvas1.draw_idle()
        self.canvas2.draw_idle()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Linked Brushing Bubble Charts')
    parser.add_argument('-i', '--input', type=str, required=True, help='Path to the input CSV file')
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    window = LinkedBubbleChartApp(args.input)
    window.show()
    sys.exit(app.exec())
