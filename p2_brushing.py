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
import numpy as np

class Brush:
    def __init__(self, xs, ys, ax, callback, color='red', alpha=0.6, edgecolor='black'):
        self.df = pd.DataFrame({'x': xs, 'y': ys})
        self.callback = callback
        self.ax = ax
        self.rec = RectangleSelector(ax, self.onselect, useblit=True, interactive=True)

    def onselect(self, eclick, erelease):
        # Get the coordinates of the selected region
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        selected = self.df[(self.df['x'].between(x1, x2)) & (self.df['y'].between(y1, y2))]
        self.callback(selected.index.tolist())  # Call the callback with the selected indices

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

        # Controls for Chart 1
        self.controls_layout1 = QHBoxLayout()
        self.controls_layout1.addWidget(QLabel('Chart 1:'))
        self.x_dropdown1 = self.add_dropdown(self.controls_layout1)
        self.y_dropdown1 = self.add_dropdown(self.controls_layout1)
        self.radius_dropdown1 = self.add_dropdown(self.controls_layout1)
        self.color_dropdown1 = self.add_dropdown(self.controls_layout1)
        self.size_slider1 = self.add_slider(self.controls_layout1)
        self.layout.addLayout(self.controls_layout1)

        # Controls for Chart 2
        self.controls_layout2 = QHBoxLayout()
        self.controls_layout2.addWidget(QLabel('Chart 2:'))
        self.x_dropdown2 = self.add_dropdown(self.controls_layout2)
        self.y_dropdown2 = self.add_dropdown(self.controls_layout2)
        self.radius_dropdown2 = self.add_dropdown(self.controls_layout2)
        self.color_dropdown2 = self.add_dropdown(self.controls_layout2)
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

        # Event handlers for plot updates
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

        # Initialize linked brushing for both charts
        self.brush1 = None
        self.brush2 = None

        # Track selected indices for brushing
        self.selected_indices = []

        # Initial plot
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

    def brush_callback(self, selected):
        self.selected_indices = selected
        self.update_plot()

    def update_plot(self):
        # Get selected attributes from dropdowns for both charts
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

        # Clear the entire figure for both canvases
        self.canvas1.figure.clf()  # Clear the figure for chart 1
        self.canvas2.figure.clf()  # Clear the figure for chart 2

        # Recreate the axes
        self.ax1 = self.canvas1.figure.add_subplot(111)
        self.ax2 = self.canvas2.figure.add_subplot(111)

        # Prepare data for chart 1
        x1 = pd.to_numeric(self.dataset[x_attr1], errors='coerce').fillna(0)
        y1 = pd.to_numeric(self.dataset[y_attr1], errors='coerce').fillna(0)
        radius1 = pd.to_numeric(self.dataset[radius_attr1], errors='coerce').fillna(1)
        color1 = pd.to_numeric(self.dataset[color_attr1], errors='coerce').fillna(0)

        # Prepare data for chart 2
        x2 = pd.to_numeric(self.dataset[x_attr2], errors='coerce').fillna(0)
        y2 = pd.to_numeric(self.dataset[y_attr2], errors='coerce').fillna(0)
        radius2 = pd.to_numeric(self.dataset[radius_attr2], errors='coerce').fillna(1)
        color2 = pd.to_numeric(self.dataset[color_attr2], errors='coerce').fillna(0)

        # Normalize radius
        scaled_radius1 = radius1 * size_scale1 / radius1.max()
        scaled_radius2 = radius2 * size_scale2 / radius2.max()

        # Create a mask for selected points
        if self.selected_indices:
            selected_mask1 = np.zeros_like(x1, dtype=bool)
            selected_mask1[self.selected_indices] = True
            selected_mask2 = np.zeros_like(x2, dtype=bool)
            selected_mask2[self.selected_indices] = True
        else:
            selected_mask1 = np.ones_like(x1, dtype=bool)
            selected_mask2 = np.ones_like(x2, dtype=bool)

        # Plot chart 1: gray for non-selected points, original colors for selected points
        self.ax1.scatter(x1[~selected_mask1], y1[~selected_mask1], s=scaled_radius1[~selected_mask1],
                         c='gray', alpha=0.4)
        scatter1 = self.ax1.scatter(x1[selected_mask1], y1[selected_mask1], s=scaled_radius1[selected_mask1],
                                    c=color1[selected_mask1], alpha=0.6, cmap='viridis')
        self.ax1.set_xlabel(x_attr1)
        self.ax1.set_ylabel(y_attr1)
        self.ax1.set_title(f'Bubble Chart 1: {x_attr1} vs {y_attr1}')
        self.colorbar1 = self.canvas1.figure.colorbar(scatter1, ax=self.ax1, label=color_attr1)

        # Plot chart 2: gray for non-selected points, original colors for selected points
        self.ax2.scatter(x2[~selected_mask2], y2[~selected_mask2], s=scaled_radius2[~selected_mask2],
                         c='gray', alpha=0.4)
        scatter2 = self.ax2.scatter(x2[selected_mask2], y2[selected_mask2], s=scaled_radius2[selected_mask2],
                                    c=color2[selected_mask2], alpha=0.6, cmap='viridis')
        self.ax2.set_xlabel(x_attr2)
        self.ax2.set_ylabel(y_attr2)
        self.ax2.set_title(f'Bubble Chart 2: {x_attr2} vs {y_attr2}')
        self.colorbar2 = self.canvas2.figure.colorbar(scatter2, ax=self.ax2, label=color_attr2)

        # Recreate the RectangleSelector for both axes after plot update
        if self.brush1:
            self.brush1.rec.disconnect_events()
        self.brush1 = Brush(x1, y1, self.ax1, self.brush_callback)

        if self.brush2:
            self.brush2.rec.disconnect_events()
        self.brush2 = Brush(x2, y2, self.ax2, self.brush_callback)

        # Adjust layout to avoid overlap
        self.canvas1.figure.tight_layout()
        self.canvas2.figure.tight_layout()

        # Redraw the canvases
        self.canvas1.draw()
        self.canvas2.draw()

    def on_select_chart1(self, eclick, erelease):
        """Handle selection in chart 1."""
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        # Apply the selection logic for chart 1, similar to brushing behavior
        selected = self.dataset[
            (self.dataset[self.x_dropdown1.currentText()].between(x1, x2)) &
            (self.dataset[self.y_dropdown1.currentText()].between(y1, y2))
        ]

        self.selected_indices = selected.index.tolist()  # Save selected indices
        self.update_plot()  # Update the plot to reflect the selection

    def on_select_chart2(self, eclick, erelease):
        """Handle selection in chart 2."""
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        # Apply the selection logic for chart 2, similar to brushing behavior
        selected = self.dataset[
            (self.dataset[self.x_dropdown2.currentText()].between(x1, x2)) &
            (self.dataset[self.y_dropdown2.currentText()].between(y1, y2))
        ]

        self.selected_indices = selected.index.tolist()  # Save selected indices
        self.update_plot()  # Update the plot to reflect the selection


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Linked Brushing Bubble Charts')
    parser.add_argument('-i', '--input', type=str, required=True, help='Path to the input CSV file')
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    window = LinkedBubbleChartApp(args.input)
    window.show()
    sys.exit(app.exec())
