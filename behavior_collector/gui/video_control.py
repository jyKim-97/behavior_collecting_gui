from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QSlider, QDoubleSpinBox,
    QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer

from .utils_gui import print_keypress
from .behavior_summary_scene import BehaviorPlotWidget
from functools import partial

MOVE_FORWARD = 1
MOVE_BACKWARD = -1
NULL_SIGNAL = -10000


class VideoController(QGroupBox):
    
    signal_move_frame = pyqtSignal(int, int)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_frames = 1
        self.total_times = 0
        self.behav_plot_panel = None
        self.fps = 1
        
        self.setFixedHeight(300)
        self.init_ui()
        self.init_player()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # self.behav_plot_panel = BehaviorSummary()
        self.behav_plot_panel = BehaviorPlotWidget()
        layout2 = self.init_control_box()
        
        layout.addWidget(self.behav_plot_panel)
        layout.addLayout(layout2)
        self.setLayout(layout)
        
    def init_player(self):
        self.is_playing = False
        self.timer_play = QTimer() # toggle play
        self.timer_play.timeout.connect(partial(self.play_frame, MOVE_FORWARD))
        
    def init_control_box(self):
        
        def _set_full_summary():
            if self.check_full_behav.isChecked():
                self.behav_plot_panel.show_full_size(True)
            else:
                self.behav_plot_panel.show_full_size(False)
        
        layout = QVBoxLayout()
        
        layout1 = QHBoxLayout()
        self.dspin_time = QDoubleSpinBox()
        self.label_time = QLabel("0")
        
        self.spin_frame = QSpinBox()
        self.label_frame = QLabel("0")
        
        self.check_full_behav = QCheckBox("Show full summary")
        self.check_full_behav.clicked.connect(_set_full_summary)
        
        layout1.addWidget(self.dspin_time)
        layout1.addWidget(self.label_time)
        layout1.addWidget(self.spin_frame)
        layout1.addWidget(self.label_frame)
        layout1.addWidget(self.check_full_behav)
        
        layout.addLayout(layout1)
        
        self.video_controller = QSlider(Qt.Horizontal, self)
        layout.addWidget(self.video_controller)
        self._reset_control_box()
        
        self.dspin_time.editingFinished.connect(self.update_dspin_time_change)
        self.spin_frame.editingFinished.connect(self.update_spin_frame_change)
        self.video_controller.sliderReleased.connect(self.update_slider_change)
        
        return layout
    
    def connect_video(self, video_panel): # receive signal if video is loaded
        video_panel.file_selected.connect(self.update_video_information)
        
    def update_video_information(self, fileinfo_dict): # receive event 
        self.file_name = fileinfo_dict["filename"]
        self.total_frames = fileinfo_dict["total_frames"]
        self.fps = fileinfo_dict["fps"]
        self.total_times = self.total_frames / self.fps
        self._reset_control_box()
        self.behav_plot_panel.set_total_frames(self.total_frames)
        
    def _reset_control_box(self):
        self.dspin_time.setRange(0, self.total_times)
        # self.dspin_time.setValue(0)
        self.label_time.setText("/%.2f s"%(self.total_times))
        
        self.spin_frame.setRange(0, self.total_frames)
        self.label_frame.setText("/%d frame"%(self.total_frames))
        
        self.video_controller.setRange(0, self.total_frames)
        self.setFrame(0)
    
    @print_keypress("video control", debug=True)
    def keyPressEvent(self, event=None):
        if event.key() == Qt.Key_L: # move forward
            self.setFrame(dframe=MOVE_FORWARD)
        elif event.key() == Qt.Key_K: # move backward
            self.setFrame(dframe=MOVE_BACKWARD)
        elif event.key() == Qt.Key_Space: # toggle play
            self.toggle_play()
    
    def setFrame(self, frame: int=None, dframe: int=None):
        if frame is None and dframe is None:
            raise ValueError("Either frame or dframe must be provided")
        
        if frame is None:
            nframe = self.getFrame()
            frame = nframe + dframe
            
        if frame < 0 or frame >= self.total_frames:
            raise ValueError("Frame out of range")
        
        self.video_controller.setValue(frame)
        self.spin_frame.setValue(frame)
        self.dspin_time.setValue(frame / self.fps)
        
        if dframe is not None:
            self.signal_move_frame.emit(NULL_SIGNAL, dframe)
        else:
            self.signal_move_frame.emit(frame, NULL_SIGNAL)
        self.behav_plot_panel.move_indicator(frame)
        
    def getFrame(self):
        return self.video_controller.value()
    
    def play_frame(self, move_type: int):
        self.setFrame(dframe=move_type)
        
    def toggle_play(self):
        if self.is_playing:
            self.timer_play.stop()
            self.is_playing = False
        else:
            interval = int(1000//self.fps) // 2
            self.timer_play.start(interval)
            self.is_playing = True
        
    @staticmethod
    def update_frame(func):
        def wrapper(self, *args, **kwargs):
            if self.is_playing: # turn off
                self.toggle_play()
            nframe = func(self, *args, **kwargs)
            self.setFrame(frame=nframe)
        return wrapper
        
    @update_frame
    def update_slider_change(self):
        return self.video_controller.value()
    
    @update_frame        
    def update_spin_frame_change(self):
        return self.spin_frame.value() # int
    
    @update_frame
    def update_dspin_time_change(self):
        value_time = self.dspin_time.value() # float
        return int(value_time * self.fps)
