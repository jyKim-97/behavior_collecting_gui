import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QMainWindow
)
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Initialize the line object
        self.x = np.linspace(0, 2 * np.pi, 100)
        self.y = np.sin(self.x)
        self.line, = self.ax.plot(self.x, self.y, lw=2)

        self.ax.set_xlim(0, 2 * np.pi)
        self.ax.set_ylim(-1.2, 1.2)

    def update_plot(self, frame_count):
        # Update Y data (e.g., phase shift)
        self.y = np.sin(self.x + 0.1 * frame_count)
        self.line.set_ydata(self.y)
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.plot_widget = PlotWidget()
        self.setCentralWidget(self.plot_widget)

        # Timer for simulating frame updates
        self.timer = QTimer()
        self.timer.setInterval(50)  # ms
        self.timer.timeout.connect(self.update_frame)

        self.frame_count = 0
        self.timer.start()

    def update_frame(self):
        self.plot_widget.update_plot(self.frame_count)
        self.frame_count += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Live Matplotlib Plot in PyQt5")
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())
