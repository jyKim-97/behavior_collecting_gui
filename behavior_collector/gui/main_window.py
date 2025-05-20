import sys
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
# from .video_panel import VideoPanel
# from .video_panel import VideoPanel

from behavior_collector.gui.video_panel import VideoPanel
from behavior_collector.gui.video_panel import MOVE_FORWARD, MOVE_BACKWARD, TOGGLE_PLAY
from behavior_collector.gui.video_control import VideoController
from behavior_collector.gui.behavior_panel import BehaviorPanel
from behavior_collector.gui.behavior_panel import pyqt_KEY_MAP
from behavior_collector.gui.utils_gui import error2messagebox, print_keypress


IMAGE_BUFFER_SIZE = 200


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Behavior Detection Tool")
        self.showFullScreen()
        
        font = QFont("Arial", 12)
        self.setFont(font)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # Left side
        layout_l = QVBoxLayout()
        video_panel_l = VideoPanel()
        layout_l.addWidget(video_panel_l, stretch=4)
        
        self.control_panel = VideoController("Video Control")
        layout_l.addWidget(self.control_panel, stretch=1)
        
        self.control_panel.connect_video(video_panel_l)
        video_panel_l.connect_controller(self.control_panel)
        
        # right side        
        layout_r = QVBoxLayout()
        video_panel_r = VideoPanel()
        layout_r.addWidget(video_panel_r, stretch=4)

        video_panel_r.connect_controller(self.control_panel)
        
        self.behavior_panel = BehaviorPanel("Behavior Control")
        layout_r.addWidget(self.behavior_panel, stretch=1)
        self.behavior_panel.connect_video(video_panel_l)
        self.behavior_panel.connect_control(self.control_panel)
        
        layout.addLayout(layout_l)
        layout.addLayout(layout_r)
        self.setLayout(layout)
    
    @print_keypress("main window", debug=True)
    @error2messagebox(to_warn=True)
    def keyPressEvent(self, event=None):
        if event.key() in (Qt.Key_L, Qt.Key_K, Qt.Key_Space):
            self.control_panel.keyPressEvent(event)
        
        # behavior selection
        elif event.key() == Qt.Key_Enter:
            pass
        elif event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() in pyqt_KEY_MAP.keys():
            self.behavior_panel.add_frame(event.key())
        else: # Q,W,E,R,T,A,S,D,F
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())