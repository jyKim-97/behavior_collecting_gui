from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QSlider, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal

# from .behavior_panel import BehaviorSummary
from .behavior_summary_scene import BehaviorPlotWidget
from .video_panel import MOVE_FORWARD, MOVE_BACKWARD, TOGGLE_PLAY


class VideoController(QGroupBox):
    
    move_video = pyqtSignal(int)
    play_video = pyqtSignal(int)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_frames = 1
        self.total_times = 0
        self.behav_plot_panel = None
        self.fps = 1
        self.setFixedHeight(300)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # self.behav_plot_panel = BehaviorSummary()
        self.behav_plot_panel = BehaviorPlotWidget()
        layout2 = self.init_control_box()
        
        layout.addWidget(self.behav_plot_panel)
        layout.addLayout(layout2)
        self.setLayout(layout)
        
    def init_control_box(self):
        layout = QVBoxLayout()
        
        layout1 = QHBoxLayout()
        self.dspin_time = QDoubleSpinBox()
        self.label_time = QLabel("0")
        
        self.spin_frame = QSpinBox()
        self.label_frame = QLabel("0")
        
        layout1.addWidget(self.dspin_time)
        layout1.addWidget(self.label_time)
        layout1.addWidget(self.spin_frame)
        layout1.addWidget(self.label_frame)
        
        layout.addLayout(layout1)
        
        self.video_controller = QSlider(Qt.Horizontal, self)
        layout.addWidget(self.video_controller)
        self._reset_control_box()
        
        # self.dspin_time.valueChanged.connect(self.update_time_change)
        # self.spin_frame.valueChanged.connect(self.update_frame_change)
        self.dspin_time.editingFinished.connect(self.update_dspin_time_change)
        self.spin_frame.editingFinished.connect(self.update_spin_frame_change)
        self.video_controller.sliderReleased.connect(self.update_slider_change)
        
        return layout
        
    def _reset_control_box(self):
        self.dspin_time.setRange(0, self.total_times)
        # self.dspin_time.setValue(0)
        self.label_time.setText("/%.2f s"%(self.total_times))
        
        self.spin_frame.setRange(0, self.total_frames)
        # self.spin_frame.setValue(0)
        self.label_frame.setText("/%d frame"%(self.total_frames))
        
        self.video_controller.setRange(0, self.total_frames)
        # self.video_controller.setValue(0)
        self.setFrame(0)
    
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
        
        # self.move_video.emit(frame)
        if dframe in (-1, 0, 1):
            self.play_video.emit(dframe)
        else:
            self.move_video.emit(frame)
        self.behav_plot_panel.move_indicator(frame)
        
    def getFrame(self):
        return self.video_controller.value()
        
    def connect_video(self, video_panel): # receive signal if video is loaded
        video_panel.file_selected.connect(self.update_video_information)
        
    def update_video_information(self, fileinfo_dict): # receive event 
        self.file_name = fileinfo_dict["filename"]
        self.total_frames = fileinfo_dict["total_frames"]
        self.fps = fileinfo_dict["fps"]
        self.total_times = self.total_frames / self.fps
        self._reset_control_box()
        
        self.behav_plot_panel.set_total_frames(self.total_frames)
    
    def move_frame(self, move_type: int):
        self.setFrame(dframe=move_type)
        
    def update_slider_change(self):
        self.setFrame(frame=self.video_controller.value())
        # self.update_frame_change(self.video_controller.value())
        
    def update_spin_frame_change(self):
        value_frame = self.spin_frame.value() # int
        self.setFrame(frame=value_frame)
        # self.update_frame_change(value_frame)
    
    def update_dspin_time_change(self):
        value_time = self.dspin_time.value() # float
        self.setFrame(frame=int(value_time * self.fps))
        # self.update_frame_change(int(value_time * self.fps))
        
