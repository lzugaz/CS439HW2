import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class HoverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)
        
        # Create a canvas to embed the Matplotlib plot
        self.canvas = FigureCanvas(Figure(figsize=(5, 4)))
        layout.addWidget(self.canvas)
        
        # Create a simple plot
        self.ax = self.canvas.figure.subplots()
        self.x = np.linspace(0, 2 * np.pi, 100)
        self.y = np.sin(self.x)
        self.scatter = self.ax.scatter(self.x, self.y)
        self.ax.set_title('Hover over points')
        
        # Set up annotation box (initially invisible)
        self.annot = self.ax.annotate("", xy=(0, 0), xytext=(10, 10),
                                      textcoords="offset points", 
                                      bbox=dict(boxstyle="round", fc="w"),
                                      arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

        # Connect the hover event
        self.canvas.mpl_connect("motion_notify_event", self.hover)

    def update_annot(self, ind):
        # Get the position of the hovered point
        pos = self.scatter.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos
        text = f"x: {pos[0]:.2f}, y: {pos[1]:.2f}"
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.6)

    def hover(self, event):
        # Check if the event is inside the axes
        if event.inaxes == self.ax:
            # Check if the cursor is over a point
            cont, ind = self.scatter.contains(event)
            if cont:
                # Update and show the annotation
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.canvas.draw_idle()
            else:
                # Hide the annotation
                self.annot.set_visible(False)
                self.canvas.draw_idle()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HoverApp()
    window.show()
    sys.exit(app.exec())
