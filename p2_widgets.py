import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QComboBox, QSlider, QLabel, QWidget
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class BubbleChartApp(QWidget):
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.colorbar = None  # Initialize colorbar as None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.fig)

        # Dropdowns for selecting attributes
        self.x_dropdown = QComboBox(self)
        self.y_dropdown = QComboBox(self)
        self.size_dropdown = QComboBox(self)
        self.color_dropdown = QComboBox(self)

        # Add items (column names from DataFrame) to dropdowns
        self.columns = self.df.columns
        for col in self.columns:
            self.x_dropdown.addItem(col)
            self.y_dropdown.addItem(col)
            self.size_dropdown.addItem(col)
            self.color_dropdown.addItem(col)

        # Slider to control bubble size scaling
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setMaximum(100)
        self.size_slider.setValue(50)  # Initial scaling factor

        # Labels for the dropdowns
        x_label = QLabel('X Axis:')
        y_label = QLabel('Y Axis:')
        size_label = QLabel('Size:')
        color_label = QLabel('Color:')
        slider_label = QLabel('Size Scaling:')

        # Layout for the controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(x_label)
        controls_layout.addWidget(self.x_dropdown)
        controls_layout.addWidget(y_label)
        controls_layout.addWidget(self.y_dropdown)
        controls_layout.addWidget(size_label)
        controls_layout.addWidget(self.size_dropdown)
        controls_layout.addWidget(color_label)
        controls_layout.addWidget(self.color_dropdown)

        layout.addLayout(controls_layout)
        layout.addWidget(slider_label)
        layout.addWidget(self.size_slider)
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Connect dropdowns and slider to the update function
        self.x_dropdown.currentIndexChanged.connect(self.update_plot)
        self.y_dropdown.currentIndexChanged.connect(self.update_plot)
        self.size_dropdown.currentIndexChanged.connect(self.update_plot)
        self.color_dropdown.currentIndexChanged.connect(self.update_plot)
        self.size_slider.valueChanged.connect(self.update_plot)

        # Initial plot
        self.update_plot()

    def update_plot(self):
        # Get selected values from dropdowns
        x_attr = self.x_dropdown.currentText()
        y_attr = self.y_dropdown.currentText()
        size_attr = self.size_dropdown.currentText()
        color_attr = self.color_dropdown.currentText()

        # Convert the selected columns to numeric, forcing errors to NaN
        x = pd.to_numeric(self.df[x_attr], errors='coerce')
        y = pd.to_numeric(self.df[y_attr], errors='coerce')
        sizes = pd.to_numeric(self.df[size_attr], errors='coerce')
        colors = pd.to_numeric(self.df[color_attr], errors='coerce')

        # Drop rows with NaN values in any of the selected columns
        valid_data = pd.DataFrame({x_attr: x, y_attr: y, size_attr: sizes, color_attr: colors}).dropna()

        # Apply size scaling based on slider
        size_scaling_factor = self.size_slider.value()
        sizes_scaled = (valid_data[size_attr] - valid_data[size_attr].min()) / (valid_data[size_attr].max() - valid_data[size_attr].min()) * size_scaling_factor * 100 + 10

        # Clear the entire figure, including colorbars
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        # Create the bubble chart with valid data
        scatter = self.ax.scatter(valid_data[x_attr], valid_data[y_attr], s=sizes_scaled, c=valid_data[color_attr], cmap='viridis', alpha=0.6, edgecolors="w", linewidth=0.5)

        # Add a new colorbar
        self.colorbar = self.fig.colorbar(scatter, ax=self.ax)
        self.colorbar.set_label(color_attr)

        # Set axis labels and title
        self.ax.set_xlabel(x_attr)
        self.ax.set_ylabel(y_attr)
        self.ax.set_title("CIA Factbook 2023")

        # Redraw the plot
        self.canvas.draw()

if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate a bubble chart from a CSV dataset.')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV filename')
    args = parser.parse_args()

    # Load the dataset from the CSV file
    df = pd.read_csv(args.input)

    # Start the Qt application
    app = QApplication(sys.argv)
    main_window = BubbleChartApp(df)
    main_window.setWindowTitle('Interactive Bubble Chart with PyQt6')
    main_window.show()
    sys.exit(app.exec())
