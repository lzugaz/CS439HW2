import sys
import pandas as pd
import numpy as np
import argparse
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QComboBox, QSlider, QLabel, QVBoxLayout, QHBoxLayout, QWidget

class BubbleChartApp(QtWidgets.QMainWindow):
    def __init__(self, dataset):
        super().__init__()

        self.dataset = pd.read_csv(dataset)  
        self.attributes = self.dataset.columns.tolist()  
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        self.canvas = FigureCanvas(Figure(figsize=(6, 6)))
        self.ax = self.canvas.figure.subplots()
        self.layout.addWidget(NavigationToolbar(self.canvas, self))
        self.layout.addWidget(self.canvas)

        self.x_dropdown = QComboBox(self)
        self.y_dropdown = QComboBox(self)
        self.radius_dropdown = QComboBox(self)
        self.color_dropdown = QComboBox(self)

        for attr in self.attributes:
            self.x_dropdown.addItem(attr)
            self.y_dropdown.addItem(attr)
            self.radius_dropdown.addItem(attr)
            self.color_dropdown.addItem(attr)

        self.size_slider = QSlider(QtCore.Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setMaximum(100)
        self.size_slider.setValue(10)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel('X-Axis:'))
        controls_layout.addWidget(self.x_dropdown)
        controls_layout.addWidget(QLabel('Y-Axis:'))
        controls_layout.addWidget(self.y_dropdown)
        controls_layout.addWidget(QLabel('Radius:'))
        controls_layout.addWidget(self.radius_dropdown)
        controls_layout.addWidget(QLabel('Color:'))
        controls_layout.addWidget(self.color_dropdown)
        controls_layout.addWidget(QLabel('Bubble Size Scale:'))
        controls_layout.addWidget(self.size_slider)

        self.layout.addLayout(controls_layout)

        self.x_dropdown.currentIndexChanged.connect(self.update_plot)
        self.y_dropdown.currentIndexChanged.connect(self.update_plot)
        self.radius_dropdown.currentIndexChanged.connect(self.update_plot)
        self.color_dropdown.currentIndexChanged.connect(self.update_plot)
        self.size_slider.valueChanged.connect(self.update_plot)

        self.update_plot()

    def update_plot(self):
        x_attr = self.x_dropdown.currentText()
        y_attr = self.y_dropdown.currentText()
        radius_attr = self.radius_dropdown.currentText()
        color_attr = self.color_dropdown.currentText()
        
        if not (x_attr and y_attr and radius_attr and color_attr):
            print("Please select valid options for all fields.")
            return

        size_scale = self.size_slider.value()

        self.canvas.figure.clf()  
        self.ax = self.canvas.figure.add_subplot(111) 

        x = pd.to_numeric(self.dataset[x_attr], errors='coerce')
        y = pd.to_numeric(self.dataset[y_attr], errors='coerce')
        radius = pd.to_numeric(self.dataset[radius_attr], errors='coerce')
        color = pd.to_numeric(self.dataset[color_attr], errors='coerce')

        x = x.fillna(0)
        y = y.fillna(0)
        radius = radius.fillna(1)  
        color = color.fillna(0)

        scaled_radius = radius * size_scale / radius.max()  # Normalize and scale radius

        scatter = self.ax.scatter(x, y, s=scaled_radius, c=color, alpha=0.6, cmap='viridis')
        self.ax.set_xlabel(x_attr)
        self.ax.set_ylabel(y_attr)
        self.ax.set_title(f'Bubble Chart: {x_attr} vs {y_attr}')

        self.colorbar = self.canvas.figure.colorbar(scatter, ax=self.ax, label=color_attr)

        self.canvas.figure.tight_layout()

        self.canvas.draw()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Interactive Bubble Chart with PyQt6')
    parser.add_argument('-i', '--input', type=str, required=True, help='Path to the input CSV file')
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)

    window = BubbleChartApp(args.input)
    window.show()

    sys.exit(app.exec())
