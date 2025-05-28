import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
# from PyQt5.QtWidgets import QSizePolicy
# from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import List

# TODO: add ytick size 

class BehaviorPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_full_size = False
        self.local_width = 100
        self.total_frames = 1
        self.num_behaviors = 0
        self.init_ui()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        
    def init_ui(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        # self.ax.axis("off")
        self.figure.tight_layout()
        
        self.line_cur, = self.ax.plot([0, 0], [-1, 20], lw=2, color='k')
        self.line_behavs = {}
        self.ax.set_ylim([-0.5, 1.5])
        
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        self.ax.set_yticks([])
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def set_total_frames(self, total_frames):
        self.total_frames = total_frames
        self.local_width = 100
        self.move_indicator(0)
        
    def move_indicator(self, cur_frame):
        # Update the x-axis limits to show the current frame
        if self.is_full_size:
            self.ax.set_xlim(0, self.total_frames)
        else:
            self.ax.set_xlim(cur_frame-self.local_width, cur_frame+self.local_width)
        self.line_cur.set_xdata([cur_frame, cur_frame])
        self.canvas.draw()
        
    def show_full_size(self, is_full_size=True):
        self.is_full_size = is_full_size
        
    def add_behavior(self, event_dict):
        behav_name = event_dict["name"]
        behav_color = event_dict["color"]
        
        nbehav = len(self.line_behavs)
        xdata = [np.nan, np.nan, np.nan]
        ydata = [nbehav, nbehav, np.nan]
        self.line_behavs[behav_name], = self.ax.plot(xdata, ydata, ".-", lw=1, color=behav_color)
        self.ax.set_ylim([-0.5, len(self.line_behavs)+0.5])
        self.ax.set_yticks(range(len(self.line_behavs)), labels=list(self.line_behavs.keys()))
        self.canvas.draw()
    
    def add_frame(self, event_dict):
        behav_name = event_dict["name"]
        frame_range = [event_dict["start_frame"], event_dict["end_frame"]]
        
        xdata = self.line_behavs[behav_name].get_xdata()
        ydata = self.line_behavs[behav_name].get_ydata()
        
        xdata = list(xdata) + frame_range + [np.nan]
        ydata = list(ydata) + [ydata[0], ydata[0], np.nan]
        
        self.line_behavs[behav_name].set_xdata(xdata)
        self.line_behavs[behav_name].set_ydata(ydata)
        self.canvas.draw()