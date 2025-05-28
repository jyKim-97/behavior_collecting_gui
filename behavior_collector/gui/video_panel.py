from PyQt5.QtWidgets import (
        QGraphicsScene, QGraphicsView, QVBoxLayout, QHBoxLayout,
        QToolButton, QLabel, QWidget, QFileDialog, QGraphicsPixmapItem,
)
from PyQt5.QtGui import QPixmap, QImage, QFontMetrics
from PyQt5.QtCore import Qt, QRectF, QTimer, pyqtSignal


from ..processing import VideoReader, ThreadVideoReader
from .video_control import VideoController, MOVE_FORWARD, MOVE_BACKWARD, NULL_SIGNAL

MOVE_FORWARD = 1
TOGGLE_PLAY = 0
MOVE_BACKWARD = -1

# TODO: add a full screen check button


class ScencePanel(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.initizlied = False
        self.wheel_zoom_enabled = False
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self.setMinimumSize(640, 480)
    
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
        if not self.initizlied:
            self.reset_view()
            self.initizlied = True        
    
    def reset_view(self):
        self.resetTransform()
        items = self._scene.items()
        if items:
            self.fitInView(items[0], Qt.KeepAspectRatio)
    
    def enable_pan_mode(self):
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.wheel_zoom_enabled = True

    def disable_pan_mode(self):
        self.setDragMode(QGraphicsView.NoDrag)
        self.wheel_zoom_enabled = False
        
    def wheelEvent(self, event):
        if not self.wheel_zoom_enabled:
            return super().wheelEvent(event)
        
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)
    
        
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
        
        self.scene_panel = ScencePanel()
        layout_ui = self.init_ui_control_panel()

        layout.addLayout(layout_ui)
        layout.addWidget(self.scene_panel)
        
        self.setLayout(layout)
        
    
    def init_ui_control_panel(self):
        
        def _click_zoom_button():
            if self.button_zoom.isChecked():
                self.scene_panel.enable_pan_mode()
            else:
                self.scene_panel.disable_pan_mode()
        
        layout = QHBoxLayout()
        self.button_load = QToolButton()
        self.text_load = QLabel("Video file name")
        self.button_zoom = QToolButton()
        self.button_reset = QToolButton()
        
        self.button_load.setText("📁")
        self.button_zoom.setText("🔍")
        self.button_zoom.setCheckable(True)
        self.button_reset.setText("🔄")
        
        self.button_zoom.clicked.connect(_click_zoom_button)
        self.button_reset.clicked.connect(self.scene_panel.reset_view)
        
        self.button_load.clicked.connect(self._open_file_dialog)
        
        layout.addWidget(self.button_load)
        layout.addWidget(self.text_load)
        layout.addWidget(self.button_zoom)
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
        # self.video_reader = VideoReader(filename)
        self.video_reader = ThreadVideoReader(filename)
        self.update_next()
        self.file_selected.emit({
            "filename": filename,
            "total_frames": self.video_reader.total_frames,
            "fps": self.video_reader.fps,
        })

    def update_frame(self, frame=None, dframe=None):
        if frame == NULL_SIGNAL and dframe == NULL_SIGNAL:
            return
        
        if frame == NULL_SIGNAL:
            if dframe == MOVE_FORWARD:
                self.update_next()
            elif dframe == MOVE_BACKWARD:
                self.update_prev()
        else:
            self.update_specific_frame(frame)
    
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
    
    def connect_controller(self, controller: VideoController):
        controller.signal_move_frame.connect(self.update_frame)
    
    def keyPressEvent(self, event):
        print(f"Key pressed in videopanel: {event.key()}")
        event.ignore()
        
    