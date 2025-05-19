from PyQt5.QtWidgets import (
        QGraphicsScene, QGraphicsView, QVBoxLayout, QHBoxLayout,
        QToolButton, QLabel, QWidget, QFileDialog, QGraphicsPixmapItem,
)
from PyQt5.QtGui import QPixmap, QImage, QFontMetrics
from PyQt5.QtCore import Qt, QRectF, QTimer, pyqtSignal


from ..processing import VideoReader
# from .video_control import VideoController

MOVE_FORWARD = 1
TOGGLE_PLAY = 0
MOVE_BACKWARD = -1

# TODO: add a full screen check button


class ScencePanel(QGraphicsView):
    def __init__(self):
        super().__init__()
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self.setMinimumSize(640, 480)
        
    def keypressEvent(self, event):
        pass
    
    def clear_scene(self):
        self._scene.clear()
        
    def update_scene(self, frame):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(pixmap_item)
        
        # resize view to fit image
        self.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(pixmap_item, mode=Qt.KeepAspectRatio)
        
    
        
class VideoPanel(QWidget):
    
    file_selected = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.video_reader = None # VideoReader()
        self.playing = False
        
    def init_ui(self):
        # entire layout
        layout = QVBoxLayout()
        
        # control panel
        layout_ui = self.init_ui_control_panel()
        layout.addLayout(layout_ui)
        
        # video scene
        self.scene_panel = ScencePanel()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_next)
        layout.addWidget(self.scene_panel)
        
        self.setLayout(layout)
        
    
    def init_ui_control_panel(self):
        layout = QHBoxLayout()
        self.button_load = QToolButton()
        self.text_load = QLabel("Video file name")
        self.button_zoom = QToolButton()
        self.button_move = QToolButton()
        self.button_reset = QToolButton()
        
        self.button_load.setText("📁")
        self.button_zoom.setText("🔍")
        self.button_move.setText("🖱️")
        self.button_reset.setText("🔄")
        
        self.button_load.clicked.connect(self._open_file_dialog)
        
        layout.addWidget(self.button_load)
        layout.addWidget(self.text_load)
        layout.addWidget(self.button_zoom)
        layout.addWidget(self.button_move)
        layout.addWidget(self.button_reset)

        return layout
    
    def _open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(self, 
                                                  "Select video file",
                                                  "",
                                                  "Video Files (*.mp4, *.mkv);;All file (*)"
                                                  )
        if not filename: 
            return
        
        # set file name
        self.videofile = filename
        metrics = QFontMetrics(self.text_load.font())   
        elided_text = metrics.elidedText(filename, Qt.ElideLeft, self.text_load.width())
        self.text_load.setText(elided_text)
        
        # read video file
        self.video_reader = VideoReader(filename)
        self.update_next()
        self.file_selected.emit({
            "filename": filename,
            "total_frames": self.video_reader.total_frames,
            "fps": self.video_reader.fps,
        })
            
    def mouse_click(self, event):
        pass
    
    @staticmethod
    def video_move_wrapper(func):
        def wrapper(self, *args, **kwargs):
            if self.video_reader is None:
                return None
            if self.playing:
                self.timer.stop()
                self.playing = False
            frame = func(self, *args, **kwargs)
            self.scene_panel.update_scene(frame)
        return wrapper
    
    @video_move_wrapper
    def update_next(self):
        return self.video_reader.move_next() # RGB image
    
    @video_move_wrapper
    def update_prev(self):
        return self.video_reader.move_prev() # RGB image
        
    @video_move_wrapper
    def update_specific_frame(self, nframe):
        return self.video_reader.move_specific_frame(nframe)
    
    def toggle_play(self):
        if self.video_reader is None:
            return None
        
        if self.playing:
            self.timer().stop()
            self.playing = False
        else:
            interval = 1000 // self.video_reader.fps
            self.timer.start(interval)
            self.playing = True
            
    def move_frame(self, move_type: int):
        if move_type == MOVE_FORWARD:
            self.update_next()
        elif move_type == MOVE_BACKWARD:
            self.update_prev()
        elif move_type == TOGGLE_PLAY:
            self.toggle_play()
        else:
            raise ValueError("Invalid move type")
    
    def connect_controller(self, controller):
        controller.move_video.connect(self.update_specific_frame)
        controller.play_video.connect(self.move_frame)
        
    