from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QScrollArea, QGroupBox, 
    QFormLayout, QLineEdit, QComboBox, QPushButton, QWidget, QLabel,
    QPlainTextEdit, QSizePolicy, QFileDialog
)

from PyQt5.QtCore import Qt, pyqtSignal
from collections import OrderedDict
from typing import List, Dict

from .utils_gui import ColorPicker, error2messagebox
from ..processing.behavior_collector import BehavInfo


pyqt_KEY_MAP = OrderedDict({  
            Qt.Key_Q: "q",
            Qt.Key_W: "w",
            Qt.Key_E: "e",
            Qt.Key_R: "r",
            Qt.Key_T: "t",
            Qt.Key_A: "a",
            Qt.Key_S: "s",
            Qt.Key_D: "d",
            Qt.Key_F: "f",
            Qt.Key_G: "g",
            Qt.Key_Z: "z", # -> quit collecting
            Qt.Key_X: "x" # -> remove collecting
        })
MAX_KEY = len(pyqt_KEY_MAP) - 1

BEHAV_KEY_REMOVE = Qt.Key_X
BEHAV_KEY_QUIT = Qt.Key_Z
BEHAV_KEY_USE = 0
    

# TODO: add a behavior remover (button x)
    
    
class SelectableRow(QPushButton):
    def __init__(self, behav_key, behav_name, behav_type, behav_color, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setStyleSheet("text-align: left; padding: 5px;")
        self.setLayout(QHBoxLayout())
        self.setFixedHeight(60)
        self.setStyleSheet("font-size: 12pt;")

        self.behav_name = behav_name
        self.behav_type = behav_type
        
        label_name = QLabel(f"({behav_key}) {behav_name} [{behav_type}]")
        
        color_box = QLabel()
        color_box.setFixedSize(30, 20)
        color_box.setStyleSheet(f"background-color: {behav_color.name()}; border: 1px solid black;")

        self.layout().addWidget(label_name)
        self.layout().addWidget(color_box)

        self.setCheckable(True)


class BehaviorPanel(QGroupBox):
    
    signal_add_behav = pyqtSignal(dict) # name, color
    signal_add_frame = pyqtSignal(dict) # start_frame, end_frame
    # TODO: signal_remove_frame
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()
        self.setFixedHeight(300)
        self.behav_set = None
        self.behav_pair = None
        self.state_add = (False, None, -1) # (state, key, start_frame)
        self.video_control = None
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # form
        layout1 = self.init_ui_form()
        layout.addLayout(layout1)
        
        # display
        layout2 = QVBoxLayout()
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)

        self.scroll_area.setWidget(self.scroll_widget)
        layout2.addWidget(self.scroll_area, stretch=4)
        
        self.button_load = QPushButton("Load Behavior")
        self.button_load.clicked.connect(self._load_behavior)
        layout2.addWidget(self.button_load, stretch=1)
        
        self.button_export = QPushButton("Export Behavior")
        self.button_export.clicked.connect(self._export_behavior)
        layout2.addWidget(self.button_export, stretch=1)
        
        layout.addLayout(layout2)
        
        self.setLayout(layout)
        
    def connect_video(self, video_panel):
        video_panel.file_selected.connect(self.receive_video)
        
    def connect_control(self, video_control):
        self.video_control = video_control
        self.signal_add_behav.connect(self.video_control.behav_plot_panel.add_behavior)
        self.signal_add_frame.connect(self.video_control.behav_plot_panel.add_frame)
    
    def read_frame(self):
        return self.video_control.getFrame()
        
    def receive_video(self, fileinfo):
        self.behav_set = BehavInfo(fileinfo["filename"], fileinfo["total_frames"])
        self.behav_set.behav_info = {}
        self.behav_set.behav_frames = {}
        self.behav_pair = dict()
        
    def init_ui_form(self):
        # font_css = "font-family: Arial; font-size: 12pt;"
        
        def _set_label(lb):
            label = QLabel(lb)
            return label
        
        layout_v = QVBoxLayout()
        
        layout_form = QFormLayout()
        self.text_name = QLineEdit()
        self.comb_type = QComboBox()
        self.color_picker = ColorPicker()
        self.button_add = QPushButton("Add Behavior")
        self.text_note = QPlainTextEdit()
        # self.text_note.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.)
        
        layout_form.addRow(_set_label("Behavior Name"), self.text_name)
        layout_form.addRow(_set_label("Behavior type"), self.comb_type)
        layout_form.addRow(_set_label("Color identifier"), self.color_picker)
        layout_form.addRow(_set_label("Note"), self.text_note)
        
        self.comb_type.addItems(["Event", "State"])
        self.button_add.clicked.connect(self._add_behavior)
        
        layout_v.addLayout(layout_form)
        layout_v.addWidget(self.button_add)
        
        return layout_v
    
    @error2messagebox(to_warn=True)
    def _add_behavior(self, *args, name=None, btype=None, color=None):
        global BEHAV_KEY_USE
        
        if self.behav_set is None:
            raise ValueError("Behavior set is not initialized")

        if name is None:
            name = self.text_name.text()
        if btype is None:
            btype = self.comb_type.currentText()
        if color is None:
            color = self.color_picker.color()  # QColor
        note = self.text_note.toPlainText()
        
        
        key_qt, key_str = list(pyqt_KEY_MAP.items())[BEHAV_KEY_USE]
        BEHAV_KEY_USE += 1
        
        row_layout = QHBoxLayout()
        
        self.behav_set.add_behavior(name, btype, note, color.name())
        # Row container
        row = SelectableRow(key_str, name, btype, color)
        self.behav_pair[key_qt] = row
        
        row_layout.addWidget(row)
        self.scroll_layout.addWidget(row)
        self.signal_add_behav.emit({
            "name": name,
            "type": btype,
            "color": color.name(),
            "note": note
        })
        
    def add_frame(self, pressed_key):
        
        # Quit collecting
        if pressed_key == BEHAV_KEY_QUIT:
            if self.state_add[0]:
                prev_button = self.behav_pair[self.state_add[1]]
                prev_button.setChecked(False)
                self.state_add = (False, None, -1)
            return
        
        if pressed_key == BEHAV_KEY_REMOVE:
            # TODO: remove behavior
            pass
        
        # Collecting start
        if pressed_key not in self.behav_pair.keys():
            raise ValueError("Key not recognized")
        
        behav_button = self.behav_pair[pressed_key]        
        behav_name = behav_button.behav_name
        nframe = self.read_frame()
        
        if self.state_add[0]: # collecting frame set
            if self.state_add[1] != pressed_key:
                raise ValueError("Key mismatch. Please type 'x' to quit collecting first.")
            self.behav_set.add_frame(behav_name, start_frame=self.state_add[2], end_frame=nframe)
            self.signal_add_frame.emit({
                "name": behav_name,
                "start_frame": self.state_add[2],
                "end_frame": nframe
            })
            self.state_add = (False, None, -1)
            behav_button.setChecked(False)
            
        else: # start collecting
            if behav_button.behav_type == "Event":
                self.behav_set.add_frame(behav_name, start_frame=nframe)
                self.signal_add_frame.emit({
                    "name": behav_name,
                    "start_frame": nframe,
                    "end_frame": nframe
                })
            elif behav_button.behav_type == "State":
                self.state_add = (True, pressed_key, nframe)
                behav_button.setChecked(True)
            else:
                raise ValueError("Behavior type not recognized")
        
    def update_panel(self, frame):
        pass
    
    @error2messagebox(to_warn=True)
    def _load_behavior(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Behavior",
                                                   "",
                                                   "Behavior Files (*.json *.txt)")
        self.behav_set = BehavInfo.load(file_path)
        for behav_name in self.behav_set.behav_info.keys():
            behav_type = self.behav_set.behav_info[behav_name]["behavior_type"]
            behav_note = self.behav_set.behav_info[behav_name]["behavior_note"]
            behav_color = self.behav_set.behav_info[behav_name]["behavior_color"]
            self._add_behavior(behav_name, behav_type, behav_color, behav_note)
        
        # TODO: update all the UI based on the loaded behavior
    
    def _export_behavior(self):
        pass
