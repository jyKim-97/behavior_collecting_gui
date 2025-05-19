from PyQt5.QtWidgets import QColorDialog, QWidget, QMessageBox
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt, QSize
import traceback


class ColorPicker(QWidget):
    def __init__(self, initial_color=QColor("#ffffff")):
        super().__init__()
        # self.setFixedSize(QSize(40, 20))  # Small color swatch
        self._color = initial_color

        # Optional: show hand cursor on hover
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        color = QColorDialog.getColor(self._color, self, "Select Color")
        if color.isValid():
            self._color = color
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self._color)
        painter.setPen(Qt.black)
        painter.drawRect(self.rect())

    def color(self):
        return self._color

    def setColor(self, color):
        if isinstance(color, QColor):
            self._color = color
            self.update()
            
    
def error2messagebox(to_warn=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(traceback.format_exc())
                print(e)
                if to_warn:
                    QMessageBox.warning(None, "Warning", str(e))
                else:
                    QMessageBox.critical(None, "Error", str(e))
                    raise
        return wrapper
    return decorator
